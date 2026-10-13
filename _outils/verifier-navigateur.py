#!/usr/bin/env python3
"""
verifier-navigateur.py : contrôles dans Chrome (bandeau de cookies, liens, page de vente, vidéo d'un article).

Usage :
    py -3.12 _outils/verifier-navigateur.py
    py -3.12 _outils/verifier-navigateur.py --article /formation-soudure/mon-article/

Le script construit le site (bundle exec jekyll build) dans un dossier temporaire et le sert lui-même.
Prérequis : py -3.12 -m pip install --user playwright (utilise le Chrome installé, aucun téléchargement).

Contrôles :
  1. Liens internes et ancres de toutes les pages (les liens provisoires « [[ ... ]] » sont signalés à part).
  2. Bandeau sur chaque page : visible, aucune requête Google Tag Manager ou Analytics avant le choix,
     boutons « Tout accepter » et « Tout refuser » de même taille, aucune erreur JavaScript.
  3. Refus, acceptation (GTM chargé, analytics_storage granted) et retrait du consentement.
  4. Page de vente : 99 € par défaut, 69 € et code AERO avec ?src=yt-module33.
  5. Avec --article : position du lecteur vidéo (visible sans défiler), sur ordinateur et sur mobile.
Code de sortie 1 en cas de problème.
"""

import argparse
import functools
import html.parser
import http.server
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
GOOGLE = ("googletagmanager.com", "google-analytics.com", "analytics.google.com")
PORT = 4011


class Liens(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.liens, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.liens.append(a[k])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--article", help="URL relative d'un article à contrôler (position de la vidéo)")
    a = p.parse_args()
    problemes, provisoires = [], []

    # Build et serveur local
    site = Path(tempfile.mkdtemp(prefix="site-verif-"))
    print("Build du site...")
    if subprocess.run("bundle exec jekyll build -q -d " + f'"{site}"', shell=True, cwd=RACINE,
                      capture_output=True).returncode != 0:
        sys.exit("ÉCHEC : le build Jekyll a échoué.")
    class Silencieux(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Silencieux, directory=str(site))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{PORT}"

    pages = sorted("/" + str(f.relative_to(site)).replace("\\", "/").replace("index.html", "")
                   for f in site.rglob("*.html")
                   if 'http-equiv="refresh"' not in f.read_text(encoding="utf-8", errors="ignore"))
    print(f"{len(pages)} pages")

    # 1. Liens
    cache = {}

    def get(url):
        if url not in cache:
            try:
                with urllib.request.urlopen(url, timeout=15) as r:
                    cache[url] = (r.status, r.read())
            except urllib.error.HTTPError as e:
                cache[url] = (e.code, b"")
        return cache[url]

    for page in pages:
        parseur = Liens()
        parseur.feed(get(base + page)[1].decode("utf-8"))
        for lien in parseur.liens:
            u = urlparse(urljoin(base + page, lien))
            if u.netloc != f"127.0.0.1:{PORT}" or lien.startswith(("mailto:", "data:")):
                continue
            if "[[" in lien:
                provisoires.append(f"{page} : {lien}")
                continue
            statut, corps = get(u._replace(fragment="").geturl())
            if statut != 200:
                problemes.append(f"lien {page} -> {lien} : {statut}")
            elif u.fragment:
                cible = Liens()
                cible.feed(corps.decode("utf-8"))
                if u.fragment not in cible.ids:
                    problemes.append(f"ancre introuvable {page} -> {lien}")

    with sync_playwright() as pw:
        navigateur = pw.chromium.launch(executable_path=CHROME, headless=True)

        def contexte(**kw):
            c = navigateur.new_context(user_agent=UA, **kw)
            # CookieConsent masque le bandeau aux robots : on se présente comme un visiteur normal
            c.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
            return c

        # 2. Bandeau sur chaque page
        for page in pages:
            c = contexte(viewport={"width": 1366, "height": 850})
            requetes, erreurs = [], []
            c.on("request", lambda r: requetes.append(r.url))
            pg = c.new_page()
            pg.on("pageerror", lambda e: erreurs.append(str(e)[:80]))
            pg.goto(base + page, wait_until="load")
            pg.wait_for_timeout(2500)
            if not pg.locator("#cc-main .cm").is_visible():
                problemes.append(f"bandeau absent : {page}")
            else:
                acc = pg.get_by_role("button", name="Tout accepter").first.bounding_box()
                ref = pg.get_by_role("button", name="Tout refuser").first.bounding_box()
                if not (acc and ref and abs(acc["width"] - ref["width"]) < 1 and abs(acc["height"] - ref["height"]) < 1):
                    problemes.append(f"boutons du bandeau inégaux : {page}")
            google = [u for u in requetes if any(d in u for d in GOOGLE)]
            if google:
                problemes.append(f"requête Google avant consentement : {page} ({google[0][:60]})")
            if erreurs:
                problemes.append(f"erreur JavaScript : {page} ({erreurs[0]})")
            c.close()

        # 3. Refus, acceptation, retrait
        c = contexte()
        requetes = []
        c.on("request", lambda r: requetes.append(r.url))
        pg = c.new_page()
        pg.goto(base + "/", wait_until="load")
        pg.wait_for_timeout(2000)
        pg.get_by_role("button", name="Tout refuser").first.click()
        pg.wait_for_timeout(800)
        pg.goto(base + "/blog/", wait_until="load")
        pg.wait_for_timeout(2000)
        if any(any(d in u for d in GOOGLE) for u in requetes):
            problemes.append("requête Google après refus")
        c.close()

        c = contexte()
        requetes = []
        c.on("request", lambda r: requetes.append(r.url))
        pg = c.new_page()
        pg.goto(base + "/", wait_until="load")
        pg.wait_for_timeout(2000)
        pg.get_by_role("button", name="Tout accepter").first.click()
        pg.wait_for_timeout(3000)
        if not any("googletagmanager.com/gtm.js" in u for u in requetes):
            problemes.append("GTM non chargé après acceptation")
        if "granted" not in pg.evaluate("JSON.stringify(dataLayer.filter(e => e && e[0]==='consent' && e[1]==='update'))"):
            problemes.append("Consent Mode non mis à jour après acceptation")
        pg.get_by_role("button", name="Gérer mes cookies").click()
        pg.wait_for_timeout(800)
        pg.locator("#cc-main .pm").get_by_role("button", name="Tout refuser").click()
        pg.wait_for_timeout(2500)
        requetes.clear()
        pg.goto(base + "/", wait_until="load")
        pg.wait_for_timeout(2000)
        if any("googletagmanager.com" in u for u in requetes):
            problemes.append("GTM chargé après retrait du consentement")
        c.close()

        # 4. Page de vente
        for q, prix_attendu, lien_attendu, bandeau_attendu in (
                ("", "99 €", "https://mapleleafwelding.gumroad.com/l/mtmqyo", False),
                ("?src=yt-module33", "69 €", "https://mapleleafwelding.gumroad.com/l/mtmqyo/AERO", True)):
            c = contexte()
            pg = c.new_page()
            pg.goto(base + "/soudeur-a-coup-sur/" + q, wait_until="load")
            pg.wait_for_timeout(2500)
            prix = set(pg.locator(".cvio-price__amount").all_inner_texts())
            liens = {h.split("?")[0] for h in pg.eval_on_selector_all("[data-gumroad-overlay-checkout]", "els => els.map(e => e.href)")}
            bandeau = pg.locator("#section-accroche").is_visible()
            if prix != {prix_attendu} or liens != {lien_attendu} or bandeau != bandeau_attendu:
                problemes.append(f"page de vente {q or '(défaut)'} : prix {prix}, liens {liens}, bandeau {bandeau}")
            c.close()

        # 5. Vidéo d'un article
        if a.article:
            for largeur, hauteur in ((1366, 850), (390, 844)):
                c = contexte(viewport={"width": largeur, "height": hauteur})
                pg = c.new_page()
                pg.goto(base + a.article, wait_until="load")
                pg.wait_for_timeout(2500)
                if pg.locator("#cc-main .cm").is_visible():
                    pg.get_by_role("button", name="Tout refuser").first.click()
                    pg.wait_for_timeout(500)
                cadre = pg.locator(".mls-video__frame iframe").first  # lecteur principal (en haut)
                if pg.locator(".mls-video__frame iframe").count() == 0:
                    problemes.append(f"article {a.article} : lecteur vidéo absent")
                else:
                    bx = cadre.bounding_box()
                    visible = max(0, min(bx["y"] + bx["height"], hauteur) - bx["y"]) / bx["height"] * 100
                    print(f"Vidéo {largeur}x{hauteur} : haut du lecteur à {bx['y']:.0f} px, visible sans défiler à {visible:.0f} %")
                    if bx["y"] >= hauteur:
                        problemes.append(f"article {a.article} ({largeur}x{hauteur}) : lecteur hors du premier écran")
                c.close()
        navigateur.close()
    serveur.shutdown()

    for l in provisoires:
        print("Lien provisoire :", l)
    if problemes:
        print("À CORRIGER :")
        for pb in problemes:
            print("  -", pb)
        sys.exit(1)
    print("OK : bandeau, consentement, liens et page de vente conformes.")


if __name__ == "__main__":
    main()
