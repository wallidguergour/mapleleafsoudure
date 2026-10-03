# Règles pour ce dépôt

- Ne jamais modifier l'identité Git de ce dépôt (`user.name` et `user.email` de la configuration locale).
- Ne jamais faire de `git push` sans mon accord explicite.

## Repères

- Site Jekyll publié par GitHub Pages sur https://mapleleafsoudure.com (gem `github-pages`, plugins `jekyll-seo-tag` et `jekyll-sitemap` uniquement).
- Contenu en français. Pas de tirets cadratins.
- Ne jamais modifier les textes de vente sans demande explicite.
- Aucun nom réel de personne dans les fichiers publiés ou versionnés, avec une seule exception : la page `/mentions-legales/` (`mentions-legales.html`), où l'éditeur renseigne lui-même son nom. Ne jamais y écrire ce nom à sa place.
- Vérification : `bash _outils/verifier-nom.sh` (noms lus dans `.noms-interdits`, fichier local non versionné).
- Tag Manager ne se charge qu'après acceptation des statistiques dans le bandeau (`_includes/consent-head.html`, `_includes/cookie-consent.html`).
- Page de vente `/soudeur-a-coup-sur/` : 99 € par défaut (lien Gumroad sans code). Avec `?src=yt-module33` (vidéo YouTube du module 3-3) : bandeau, 69 € et code Gumroad `AERO` (-30 %), gérés par le script placé avant `gumroad.js`. Le JSON-LD reste à 99 €.
- Articles de blog : `_posts/AAAA-MM-JJ-titre.md`, gabarit `_layouts/post.html`.
- Les docs internes (`*.md` à la racine) sont exclus du build et du dépôt : en ajouter un nouveau dans `exclude` (`_config.yml`) et dans `.gitignore`.
