#!/usr/bin/env python3
"""
transcribe.py : transcrit une video locale (export DaVinci) avec Whisper, en local et gratuitement.

Sorties (a cote de la video) :
  - <nom>.srt              sous-titres a televerser sur YouTube
  - <nom>_transcript.md    transcription horodatee, matiere premiere pour l'article
  - <nom>_transcript.txt   texte brut

Installation :
    pip install faster-whisper
    Par defaut, tourne sur le processeur (--device cpu). Utilise --model medium pour aller plus vite.

Exemple :
    python transcribe.py video.mp4
    python transcribe.py video.mp4 --glossaire glossaire.txt --corrections corrections.json
    python transcribe.py video.mp4 --no-vad   # garde toute la parole, meme sur fond de musique
    python transcribe.py "Mon export.mov" --nom 012   # sorties : 012.srt, 012_transcript.md, 012_transcript.txt

Corrections : si corrections.json existe dans le dossier du script, il est charge
automatiquement. Idem pour glossaire-local.txt (termes sensibles, non versionne). Un fichier passe avec --corrections s'y ajoute et l'emporte en cas de doublon.
"""

import argparse
import json
import re
from pathlib import Path

from faster_whisper import WhisperModel

# Termes metier par defaut. Complete-les avec --glossaire (un terme par ligne).
GLOSSAIRE = [
    "TIG", "MIG", "MAG", "SMAW", "GTAW", "GMAW", "FCAW", "SAW",
    "CWB", "AWS", "CSA W47.1", "CSA W59", "ISO 9606", "WPS", "PQR", "WPQ",
    "CQPM", "Titre Pro", "chaudronnier", "chaudronnerie", "soudeur-monteur",
    "serrurerie metallerie", "inox", "aluminium", "acier Corten",
    "passe de racine", "chanfrein", "electrode", "baguette", "gougeage",
    "ressuage", "magnetoscopie", "ultrasons", "radiographie",
    "IGM", "CLOOS",
    "Maple Leaf Soudure", "Soudeur a Coup Sur",
]
# Noms propres sensibles (clients, personnes) : jamais dans le depot public.
# Ils sont lus dans glossaire-local.txt (un terme par ligne, fichier non versionne, a cote du script).


def ts(seconds, sep=","):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def mmss(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def fix(text, corrections):
    # Expressions les plus longues d'abord ("greta a pas" avant "greta"),
    # et uniquement sur des mots entiers pour ne rien casser ailleurs.
    for wrong in sorted(corrections, key=len, reverse=True):
        rx = r"(?<!\w)" + re.escape(wrong) + r"(?!\w)"
        text = re.sub(rx, lambda m, r=corrections[wrong]: r, text)
    return text.strip()


def load_corrections(extra=None):
    corrections = {}
    default = Path(__file__).resolve().parent / "corrections.json"
    if default.exists():
        corrections.update(json.loads(default.read_text(encoding="utf-8")))
        print(f"Corrections chargees : {default} ({len(corrections)} entrees)")
    if extra:
        corrections.update(json.loads(Path(extra).read_text(encoding="utf-8")))
    return corrections


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video", help="Fichier video ou audio (mp4, mov, wav...)")
    p.add_argument("--model", default="large-v3", help="large-v3 (precis) ou medium (rapide)")
    p.add_argument("--glossaire", help="Fichier texte : un terme metier par ligne")
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda", "auto"],
                   help="cpu par defaut (fonctionne partout), cuda si les librairies NVIDIA sont installees")
    p.add_argument("--corrections", help='JSON {"mauvais": "correct"} en plus de corrections.json')
    p.add_argument("--nom", help="Nom de base des fichiers produits, a cote de la video (par defaut : nom de la video)")
    p.add_argument("--no-vad", action="store_true",
                   help="desactive le filtre VAD (utile si de la parole est coupee, ex. sur fond de musique)")
    a = p.parse_args()

    video = Path(a.video)
    terms = list(GLOSSAIRE)
    local = Path(__file__).resolve().parent / "glossaire-local.txt"
    if local.exists():
        terms += [l.strip() for l in local.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"Glossaire local charge : {local}")
    if a.glossaire:
        terms += [l.strip() for l in Path(a.glossaire).read_text(encoding="utf-8").splitlines() if l.strip()]
    corrections = load_corrections(a.corrections)

    print(f"Chargement du modele {a.model}...")
    compute = "int8" if a.device == "cpu" else "auto"
    model = WhisperModel(a.model, device=a.device, compute_type=compute)

    # Le prompt initial oriente Whisper vers le bon vocabulaire (longueur limitee, d'ou la coupe)
    prompt = "Video sur la soudure et la chaudronnerie. Termes : " + ", ".join(terms)
    segments, info = model.transcribe(
        str(video),
        language="fr",
        initial_prompt=prompt[:800],
        hotwords=" ".join(terms),
        vad_filter=not a.no_vad,  # ignore les silences et le bruit d'atelier, sauf avec --no-vad
        beam_size=5,
    )

    nom = a.nom or video.stem
    srt, md, txt = [], [f"# Transcription : {nom}\n"], []
    for i, seg in enumerate(segments, 1):
        text = fix(seg.text, corrections)
        srt.append(f"{i}\n{ts(seg.start)} --> {ts(seg.end)}\n{text}\n")
        md.append(f"[{mmss(seg.start)}] {text}")
        txt.append(text)
        print(f"[{mmss(seg.start)}] {text}")

    base = video.parent / nom
    Path(f"{base}.srt").write_text("\n".join(srt), encoding="utf-8")
    Path(f"{base}_transcript.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    Path(f"{base}_transcript.txt").write_text(" ".join(txt) + "\n", encoding="utf-8")

    print(f"\nDuree : {mmss(info.duration)} | Fichiers : {base}.srt, _transcript.md, _transcript.txt")
    print("Relis le .srt avant de le televerser : Whisper se trompe rarement, mais jamais zero fois.")


if __name__ == "__main__":
    main()
