#!/usr/bin/env python3
"""
youtube_infos.py : relève les données réelles d'une vidéo YouTube publique, pour le JSON-LD VideoObject.

Sortie (JSON) : identifiant, titre, date de mise en ligne, durée (secondes, mm:ss et ISO 8601),
description, chapitres trouvés dans la description, miniature la plus grande disponible.

Usage :
    py -3.12 _outils/youtube_infos.py https://www.youtube.com/watch?v=XXXXXXXXXXX
    py -3.12 _outils/youtube_infos.py XXXXXXXXXXX

Bibliothèque standard uniquement. Si YouTube ne renvoie pas une donnée, elle vaut null :
ne jamais la deviner.
"""

import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def video_id(arg):
    m = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([\w-]{11})", arg)
    if m:
        return m.group(1)
    if re.fullmatch(r"[\w-]{11}", arg):
        return arg
    sys.exit(f"Identifiant YouTube introuvable dans : {arg}")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", errors="ignore")


def champ_json(page, cle):
    """Lit la valeur JSON qui suit "cle": dans la page (chaîne, nombre ou booléen)."""
    i = page.find(f'"{cle}":')
    if i < 0:
        return None
    try:
        valeur, _ = json.JSONDecoder().raw_decode(page[i + len(cle) + 3:])
        return valeur
    except ValueError:
        return None


def en_secondes(horodatage):
    s = 0
    for partie in horodatage.split(":"):
        s = s * 60 + int(partie)
    return s


def mmss(s):
    h, reste = divmod(s, 3600)
    m, s = divmod(reste, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def iso8601(s):
    h, reste = divmod(s, 3600)
    m, s = divmod(reste, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m else "") + (f"{s}S" if s or not (h or m) else "")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    vid = video_id(sys.argv[1])
    _, page = get(f"https://www.youtube.com/watch?v={vid}")

    duree = champ_json(page, "lengthSeconds")
    duree = int(duree) if duree is not None else None
    description = champ_json(page, "shortDescription")

    # Chapitres : lignes de la description qui commencent par un horodatage (00:00, 1:02:03, [00:00]...)
    chapitres = []
    for ligne in (description or "").splitlines():
        m = re.match(r"^\s*\[?((?:\d{1,2}:)?\d{1,2}:\d{2})\]?\s*[-:–]?\s*(.+?)\s*$", ligne)
        if m:
            chapitres.append({"time": mmss(en_secondes(m.group(1))), "title": m.group(2)})

    miniature = None
    for nom in ("maxresdefault", "hqdefault"):
        try:
            statut, _ = get(f"https://i.ytimg.com/vi/{vid}/{nom}.jpg")
            if statut == 200:
                miniature = nom
                break
        except Exception:
            continue

    print(json.dumps({
        "youtube_id": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "titre": champ_json(page[page.find('"videoDetails"'):], "title") if '"videoDetails"' in page else None,
        "date_mise_en_ligne": champ_json(page, "uploadDate") or champ_json(page, "publishDate"),
        "duree_secondes": duree,
        "duree_mmss": mmss(duree) if duree is not None else None,
        "duree_iso8601": iso8601(duree) if duree is not None else None,
        "miniature": miniature,
        "prive_ou_non_repertoriee": bool(champ_json(page, "isPrivate") or champ_json(page, "isUnlisted")),
        "chapitres_description": chapitres,
        "description": description,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
