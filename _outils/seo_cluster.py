#!/usr/bin/env python3
"""
seo_cluster.py : recherche de requetes pour un cluster de videos (YouTube + Google)

1. Genere des idees de mots-cles a partir de tes sujets de depart (DataForSEO Labs)
2. Verifie la SERP Google des meilleures requetes :
   carrousel video, Shorts, video YouTube en resultat organique, featured snippet, questions PAA
3. Sort un CSV + un fichier Markdown pret a coller dans Gemini ou Claude

Installation :
    pip install requests

PowerShell :
    $env:DATAFORSEO_LOGIN="ton_login"
    $env:DATAFORSEO_PASSWORD="ton_mot_de_passe_api"

Exemple :
    python seo_cluster.py "devenir soudeur" "formation soudure" --racines soud --markets fr ca --serp-top 10
"""

import argparse
import csv
import os
import re
import sys

import requests

API = "https://api.dataforseo.com/v3"
MARKETS = {"fr": 2250, "ca": 2124}  # location_code France / Canada
VIDEO_TYPES = {"video", "short_videos"}
TOTAL_COST = 0.0


def call(endpoint, payload):
    """Appel API DataForSEO, cumule le cout reel renvoye par l'API."""
    global TOTAL_COST
    auth = (os.environ.get("DATAFORSEO_LOGIN"), os.environ.get("DATAFORSEO_PASSWORD"))
    if not all(auth):
        sys.exit("Identifiants manquants : DATAFORSEO_LOGIN et DATAFORSEO_PASSWORD")
    r = requests.post(f"{API}{endpoint}", auth=auth, json=[payload], timeout=120)
    r.raise_for_status()
    data = r.json()
    TOTAL_COST += data.get("cost", 0) or 0
    task = data["tasks"][0]
    if task["status_code"] != 20000:
        print(f"  ! Erreur API : {task['status_message']}")
        return None
    return (task.get("result") or [None])[0]


def parse_items(res, market):
    rows = []
    for it in (res or {}).get("items") or []:
        info = it.get("keyword_info") or {}
        props = it.get("keyword_properties") or {}
        intent = it.get("search_intent_info") or {}
        rows.append({
            "marche": market,
            "requete": it["keyword"],
            "volume": info.get("search_volume") or 0,
            "difficulte": props.get("keyword_difficulty"),
            "intention": intent.get("main_intent"),
            "serp_verifiee": False,
        })
    return rows


def match(requete, racines):
    """Vrai si une racine apparait en DEBUT de mot ("ia" capte "l ia" mais pas "kia")."""
    return any(re.search(r"(^|[\s'-])" + re.escape(x.lower()), requete.lower()) for x in racines)


def collect_keywords(seeds, market, limit, racines, aussi=None):
    """Suggestions (contiennent le sujet) + idees (semantiquement proches), filtrees par racines."""
    rows = []
    for seed in seeds:
        rows += parse_items(call("/dataforseo_labs/google/keyword_suggestions/live", {
            "keyword": seed,
            "location_code": MARKETS[market],
            "language_code": "fr",
            "include_seed_keyword": True,
            "limit": limit,
        }), market)
    rows += parse_items(call("/dataforseo_labs/google/keyword_ideas/live", {
        "keywords": seeds,
        "location_code": MARKETS[market],
        "language_code": "fr",
        "include_seed_keyword": True,
        "limit": limit,
    }), market)

    # Dedoublonnage
    uniques = {}
    for r in rows:
        uniques.setdefault(r["requete"], r)
    rows = list(uniques.values())

    # Filtre : au moins une racine de --racines, ET au moins une de --aussi si fourni
    if racines:
        rows = [r for r in rows if match(r["requete"], racines)]
    if aussi:
        rows = [r for r in rows if match(r["requete"], aussi)]
    return rows


def check_serp(keyword, market):
    res = call("/serp/google/organic/live/advanced", {
        "keyword": keyword,
        "location_code": MARKETS[market],
        "language_code": "fr",
        "device": "desktop",
        "depth": 10,
    })
    if not res:
        return {}
    items = res.get("items") or []
    types = set(res.get("item_types") or [])

    paa = [q.get("title") for it in items if it["type"] == "people_also_ask"
           for q in (it.get("items") or []) if q.get("title")]

    # Videos dans les blocs carrousel ou Shorts
    bloc_youtube = any("youtube.com" in (v.get("url") or "")
                       for it in items if it["type"] in VIDEO_TYPES
                       for v in (it.get("items") or []))
    # Video YouTube affichee comme resultat organique classique
    youtube_organique = any(it["type"] == "organic" and "youtube.com" in (it.get("url") or "")
                            for it in items)

    formats = sorted(VIDEO_TYPES & types)
    if youtube_organique:
        formats.append("youtube_organique")

    return {
        "serp_verifiee": True,
        "video": bool(formats),
        "formats_video": ", ".join(formats),
        "video_youtube": bloc_youtube or youtube_organique,
        "featured_snippet": "featured_snippet" in types,
        "questions_paa": " | ".join(paa),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("seeds", nargs="+", help="Sujets de depart du cluster")
    p.add_argument("--markets", nargs="+", default=["fr", "ca"], choices=MARKETS)
    p.add_argument("--limit", type=int, default=100, help="Idees max par marche")
    p.add_argument("--serp-top", type=int, default=10, help="Requetes verifiees par marche")
    p.add_argument("--racines", nargs="+", default=None,
                   help="Ne garder que les requetes contenant ces racines (ex. soud chaudron)")
    p.add_argument("--aussi", nargs="+", default=None,
                   help="La requete doit AUSSI contenir une de ces racines (ex. --racines soud --aussi ia robot)")
    p.add_argument("--out", default=None, help="Nom de base des fichiers de sortie")
    a = p.parse_args()

    base = a.out or "cluster_" + re.sub(r"\W+", "_", a.seeds[0].lower()).strip("_")
    rows = []
    for m in a.markets:
        print(f"[{m}] Idees de mots-cles...")
        ideas = sorted(collect_keywords(a.seeds, m, a.limit, a.racines, a.aussi), key=lambda r: -r["volume"])
        n = min(a.serp_top, len(ideas))
        print(f"[{m}] {len(ideas)} requetes, verification SERP des {n} premieres...")
        for i, r in enumerate(ideas):
            if i < a.serp_top:
                r.update(check_serp(r["requete"], m))
                tag = r.get("formats_video") or "pas de video"
                print(f"   {r['requete']} (vol. {r['volume']}) : {tag}")
            rows.append(r)

    fields = ["marche", "requete", "volume", "difficulte", "intention", "serp_verifiee",
              "video", "formats_video", "video_youtube", "featured_snippet", "questions_paa"]
    with open(f"{base}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # Priorite : requetes ou Google affiche deja une video ou un snippet
    top = [r for r in rows if r.get("video") or r.get("featured_snippet")]
    paa = sorted({q for r in rows for q in (r.get("questions_paa") or "").split(" | ") if q})
    non_verifiees = [r for r in rows if not r["serp_verifiee"]]

    with open(f"{base}_prompt.md", "w", encoding="utf-8") as f:
        f.write(f"# Donnees SEO mesurees : {', '.join(a.seeds)}\n\n")
        f.write("Construis titres et chapitres UNIQUEMENT a partir de ces requetes reelles. "
                "N'invente aucune requete ni aucun volume.\n\n")
        f.write("## Requetes a potentiel video (Google affiche video, Shorts ou snippet)\n\n")
        for r in top:
            tags = [t for t in (r.get("formats_video"), "featured_snippet" if r.get("featured_snippet") else "") if t]
            f.write(f"- [{r['marche']}] {r['requete']} (vol. {r['volume']}, {', '.join(tags)})\n")
        f.write("\n## Questions 'Autres questions posees'\n\n")
        f.writelines(f"- {q}\n" for q in paa)
        f.write("\n## Autres requetes (SERP non verifiee)\n\n")
        f.writelines(f"- [{r['marche']}] {r['requete']} (vol. {r['volume']})\n" for r in non_verifiees)

    print(f"\nFichiers : {base}.csv et {base}_prompt.md")
    print(f"Requetes a potentiel video : {len(top)} | Questions PAA : {len(paa)}")
    print(f"Cout reel de l'execution : {TOTAL_COST:.4f} $")


if __name__ == "__main__":
    main()
