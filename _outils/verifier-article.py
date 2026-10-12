#!/usr/bin/env python3
"""
verifier-article.py : contrôle un article de _posts/ selon les règles de CLAUDE.md.

Usage :
    py -3.12 _outils/verifier-article.py _posts/AAAA-MM-JJ-titre.md

Erreurs (code de sortie 1) :
  - en-tête incomplet : title, description (155 caractères maximum), date, category (une des 4)
  - vidéo : champs vidéo manquants, chapitres non croissants ou au-delà de la durée
  - H2 formulé en question : réponse directe hors de 40 à 60 mots
  - tirets cadratins, marqueurs [[ ... ]]
  - liens internes manquants : pilier de la catégorie et /soudeur-a-coup-sur/
Signalements (sans échec) : tics de langage, commentaires « à vérifier ».
"""

import re
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
PILIERS = [p["slug"] for p in yaml.safe_load((RACINE / "_data/piliers.yml").read_text(encoding="utf-8"))]
TICS = ["donc", "en fait", "voilà", "bref", "du coup"]


def secondes(t):
    t = str(t)
    if ":" not in t:
        return int(t)
    s = 0
    for p in t.split(":"):
        s = s * 60 + int(p)
    return s


def mots(texte):
    texte = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texte)   # liens Markdown
    texte = re.sub(r"<[^>]+>", " ", texte)                    # balises HTML
    return len(re.findall(r"[0-9A-Za-zÀ-ÿ'’%€-]+", texte))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fichier = Path(sys.argv[1])
    texte = fichier.read_text(encoding="utf-8")
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", texte, re.S)
    if not m:
        sys.exit("En-tête YAML introuvable.")
    fm = yaml.safe_load(m.group(1)) or {}
    corps = m.group(2)
    erreurs, signalements = [], []

    # En-tête
    for champ in ("title", "description", "date", "category"):
        if not fm.get(champ):
            erreurs.append(f"en-tête : champ « {champ} » manquant")
    if "categories" in fm:
        erreurs.append("en-tête : utiliser « category » (une seule), pas « categories »")
    if fm.get("category") and fm["category"] not in PILIERS:
        erreurs.append(f"en-tête : category doit être l'une de {', '.join(PILIERS)}")
    desc = fm.get("description") or ""
    if len(desc) > 155:
        erreurs.append(f"meta description trop longue : {len(desc)} caractères (155 maximum)")

    # Vidéos : principale (champs à la racine de l'en-tête) et complémentaires (videos_complementaires)
    def verifier_video(v, nom):
        for champ in ("youtube_id", "video_title", "video_description", "video_duration", "video_upload_date", "video_thumbnail", "chapters"):
            if not v.get(champ):
                erreurs.append(f"{nom} : champ « {champ} » manquant (valeur réelle relevée sur YouTube)")
        chapitres = v.get("chapters") or []
        debuts = [secondes(c.get("time", 0)) for c in chapitres]
        if debuts and debuts[0] != 0:
            erreurs.append(f"{nom} : le premier chapitre doit commencer à 00:00")
        if debuts != sorted(debuts) or len(set(debuts)) != len(debuts):
            erreurs.append(f"{nom} : horodatages des chapitres non strictement croissants")
        if v.get("video_duration") and debuts and debuts[-1] >= secondes(v["video_duration"]):
            erreurs.append(f"{nom} : un chapitre commence après la fin de la vidéo")
        for c in chapitres:
            if not isinstance(c.get("time"), str):
                erreurs.append(f"{nom} : horodatage « {c.get('time')} » à écrire entre guillemets")

    if fm.get("youtube_id"):
        verifier_video(fm, "vidéo principale")
    complementaires = fm.get("videos_complementaires") or []
    if complementaires and not fm.get("youtube_id"):
        erreurs.append("vidéos complémentaires sans vidéo principale (youtube_id)")
    places = re.findall(r'\{%\s*include\s+video-complementaire\.html\s+id="([\w-]{11})"\s*%\}', corps)
    ids = []
    for v in complementaires:
        vid = v.get("youtube_id", "?")
        ids.append(vid)
        verifier_video(v, f"vidéo complémentaire {vid}")
        if places.count(vid) != 1:
            erreurs.append(f"vidéo complémentaire {vid} : à placer une seule fois dans le texte (trouvée {places.count(vid)} fois)")
        if vid == fm.get("youtube_id"):
            erreurs.append(f"vidéo complémentaire {vid} : identique à la vidéo principale")
    for vid in set(places) - set(ids):
        erreurs.append(f"include video-complementaire.html id=\"{vid}\" sans entrée dans videos_complementaires")

    # Réponses directes sous les H2 formulés en question
    for h in re.finditer(r"^## ([^\n]+)\n\n([^\n]+(?:\n[^\n#<][^\n]*)*)", corps, re.M):
        titre, para = h.group(1).strip(), h.group(2)
        if titre.endswith("?"):
            n = mots(para)
            if not 40 <= n <= 60:
                erreurs.append(f"réponse directe de {n} mots (40 à 60 attendus) : « {titre} »")

    # Style et marqueurs
    # Tout le texte : corps + toutes les valeurs de l'en-tête (titre, intro, champs vidéo, chapitres)
    def valeurs(x):
        if isinstance(x, dict):
            return " ".join(valeurs(v) for v in x.values())
        if isinstance(x, list):
            return " ".join(valeurs(v) for v in x)
        return str(x)
    complet = valeurs(fm) + "\n" + corps
    if "—" in complet:
        erreurs.append(f"{complet.count('—')} tiret(s) cadratin(s)")
    if re.search(r"\[\[ [^\[\]]+ \]\]", complet):
        erreurs.append("marqueur [[ ... ]] présent")
    visible = re.sub(r"<!--.*?-->", "", complet, flags=re.S)
    for tic in TICS:
        n = len(re.findall(r"\b" + re.escape(tic) + r"\b", visible, re.I))
        if n:
            signalements.append(f"tic de langage « {tic} » : {n} fois")
    for c in re.findall(r"<!--(.*?)-->", corps, re.S):
        if "vérifier" in c.lower():
            signalements.append("commentaire : " + " ".join(c.split()))

    # Liens internes
    if fm.get("category") and f"](/{fm['category']}/)" not in corps:
        erreurs.append(f"lien interne manquant vers le pilier /{fm['category']}/")
    if "](/soudeur-a-coup-sur/)" not in corps:
        erreurs.append("lien interne manquant vers /soudeur-a-coup-sur/")

    print(f"Article : {fichier.name}")
    print(f"  catégorie : {fm.get('category')} | meta description : {len(desc)} caractères | chapitres : {len(fm.get('chapters') or [])}")
    for s in signalements:
        print("  SIGNALEMENT :", s)
    if erreurs:
        print("À CORRIGER :")
        for e in erreurs:
            print("  -", e)
        sys.exit(1)
    print("OK : article conforme.")


if __name__ == "__main__":
    main()
