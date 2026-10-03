#!/usr/bin/env bash
# Vérifie qu'aucun nom réel n'apparaît dans les fichiers suivis par Git ni dans le site construit.
# Seule exception autorisée : la page /mentions-legales/ (mentions-legales.html).
#
# Les noms recherchés ne sont jamais écrits dans le dépôt : ils sont lus dans la variable
# NOMS_INTERDITS ou dans le fichier local .noms-interdits (non versionné), sous forme
# d'expression régulière, par exemple : prenom|nom
#
# Usage : bash _outils/verifier-nom.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

motif="${NOMS_INTERDITS:-$(cat .noms-interdits 2>/dev/null)}"
if [ -z "$motif" ]; then
  echo "Aucun nom à rechercher : créer le fichier .noms-interdits (ex. prenom|nom)."
  exit 2
fi

trouve=0

echo "== Fichiers suivis par Git (hors mentions-legales.html)"
if git grep -n -i -E "$motif" -- . ':!mentions-legales.html'; then trouve=1; fi
if git ls-files | grep -i -E "$motif"; then trouve=1; fi

echo "== Site construit (hors /mentions-legales/)"
destination="$(mktemp -d)"
bundle exec jekyll build -q -d "$destination" || exit 2
if grep -r -l -i -E "$motif" "$destination" --exclude-dir=mentions-legales; then trouve=1; fi
rm -rf "$destination"

if [ "$trouve" -eq 0 ]; then
  echo "OK : aucun nom trouvé en dehors de /mentions-legales/."
else
  echo "ÉCHEC : nom trouvé ci-dessus."
fi
exit "$trouve"
