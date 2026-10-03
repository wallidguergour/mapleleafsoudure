# Règles pour ce dépôt

- Ne jamais modifier l'identité Git de ce dépôt (`user.name` et `user.email` de la configuration locale).
- Ne jamais faire de `git push` sans mon accord explicite.

## Repères

- Site Jekyll publié par GitHub Pages sur https://mapleleafsoudure.com (gem `github-pages`, plugins `jekyll-seo-tag` et `jekyll-sitemap` uniquement).
- Contenu en français. Pas de tirets cadratins.
- Ne jamais modifier les textes de vente sans demande explicite.
- Aucun nom réel de personne dans les fichiers publiés ou versionnés.
- Tag Manager ne se charge qu'après acceptation des statistiques dans le bandeau (`_includes/consent-head.html`, `_includes/cookie-consent.html`).
- Articles de blog : `_posts/AAAA-MM-JJ-titre.md`, gabarit `_layouts/post.html`.
- Les docs internes (`*.md` à la racine) sont exclus du build et du dépôt : en ajouter un nouveau dans `exclude` (`_config.yml`) et dans `.gitignore`.
