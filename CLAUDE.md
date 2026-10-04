# Règles pour ce dépôt

- Ne jamais modifier l'identité Git de ce dépôt (`user.name` et `user.email` de la configuration locale).
- Ne jamais faire de `git push` sans mon accord explicite.

## Repères

- Site Jekyll publié par GitHub Pages sur https://mapleleafsoudure.com (gem `github-pages`, plugins `jekyll-seo-tag`, `jekyll-sitemap` et `jekyll-redirect-from` uniquement).
- Contenu en français. Pas de tirets cadratins.
- Ne jamais modifier les textes de vente sans demande explicite.
- N'inventer aucun texte rédactionnel, chiffre ou fonctionnalité : utiliser des marqueurs `[[ À COMPLÉTER ]]`.
- Aucun nom réel de personne dans les fichiers publiés ou versionnés, avec une seule exception : la page `/mentions-legales/` (`mentions-legales.html`), où l'éditeur renseigne lui-même son nom. Ne jamais y écrire ce nom à sa place.
- Tag Manager ne se charge qu'après acceptation des statistiques dans le bandeau (`_includes/consent-head.html`, `_includes/cookie-consent.html`).
- Page de vente `/soudeur-a-coup-sur/` : 99 € par défaut (lien Gumroad sans code). Avec `?src=yt-module33` (vidéo YouTube du module 3-3) : bandeau, 69 € et code Gumroad `AERO` (-30 %), gérés par le script placé avant `gumroad.js`. Le JSON-LD reste à 99 €. Elle garde son menu réduit.
- Les docs internes (`*.md` à la racine) sont exclus du build et du dépôt : en ajouter un nouveau dans `exclude` (`_config.yml`) et dans `.gitignore`.

## Arborescence

```
/                               Accueil (JSON-LD WebSite)
/formation-soudure/             Pilier : devenir soudeur, certifications, formations, centres
/carriere-soudeur/              Pilier : soudeur salarié, salaires, expatriation, évolution
/entreprendre-soudure/          Pilier : à son compte, statut, tarifs, clients, atelier (+ carte Soudeur à Ton Compte)
/ia-soudure/                    Pilier : IA appliquée à la soudure et à la gestion d'atelier, articles sur les outils
/<pilier>/<titre-article>/      Articles (_posts/)
/formations/                    Catalogue : Soudeur à Coup Sûr, Soudeur à Ton Compte (à venir)
/soudeur-a-coup-sur/            Page de vente (ne pas déplacer)
/outils/                        Cartes des outils (_data/outils.yml)
/outils/<nom-outil>/            Page de présentation de chaque outil (ex. /outils/harword/)
/outils/generateur-portfolio/   Générateur (ancienne adresse /generateur_portfolio_web.html redirigée)
/blog/                          Tous les articles, regroupés par pilier
/a-propos/                      Parcours (jamais de nom)
/offres/                        Analyses d'offres, noindex
/mentions-legales/, /politique-de-confidentialite/, /conditions-generales-de-vente/
/robots.txt, /sitemap.xml, /llms.txt (généré)
```

- Piliers : `_data/piliers.yml` ; menu : `_data/navigation.yml` ; cartes outils : `_data/outils.yml`.
- Gabarits : `_layouts/pilier.html` (piliers), `_layouts/post.html` (articles), `_layouts/default.html` (autres pages).
- Includes communs : `menu.html`, `footer-links.html` (deux lignes : sections, puis pages légales), `breadcrumb.html` (fil d'Ariane + BreadcrumbList, piliers et articles), `organization-jsonld.html` (Organization unique, `@id` `https://mapleleafsoudure.com/#organization`, à inclure dans toute nouvelle page HTML autonome).

## Articles

- Fichier : `_posts/AAAA-MM-JJ-titre.md`, URL : `/<category>/<titre>/`.
- Chaque article déclare UNE seule catégorie dans son en-tête, `category: ...`, parmi : `formation-soudure`, `carriere-soudeur`, `entreprendre-soudure`, `ia-soudure`. Jamais `categories:`.
- Les articles sur les outils vont dans `ia-soudure`.
- Le gabarit ajoute le fil d'Ariane, le lien vers le pilier et « À lire aussi » (jusqu'à 3 articles de la même catégorie).

## Stratégie des outils

- mapleleafsoudure.com porte le contenu, le référencement et la présentation commerciale des outils.
- Chaque outil a une page de présentation `/outils/<nom>/` et une carte dans `_data/outils.yml`.
- Les applications tournent sur des sous-domaines séparés construits avec Lovable (ex. harword.mapleleafsoudure.com), hors de ce dépôt.
- Ne créer aucun lien vers un sous-domaine ou une URL qui n'existe pas encore : laisser le champ vide (`lien_externe`, `depot_github`, `documentation`), le gabarit n'affiche alors rien.
- Harword : open source sur GitHub (installation en autonomie) et installation sur site sur devis (bouton vers Calendly).

## Règles de publication

- Aucune page indexable ne doit contenir de marqueur `[[ ... ]]`. Une page en cours reste en `robots: "noindex, follow"`, `sitemap: false` et `llms: false` dans son en-tête, à retirer une fois terminée.
- Aucun JSON-LD sur des valeurs non confirmées : le préparer en commentaire HTML (ex. SoftwareApplication de Harword) ou le générer seulement quand les données existent (ex. FAQPage depuis le champ `faq`).

## Vérifications

- `bash _outils/verifier-nom.sh` : aucun nom réel hors `/mentions-legales/` (noms lus dans `.noms-interdits`, fichier local non versionné).
- `bundle exec ruby _outils/verifier-contenu.rb` : catégories des articles, marqueurs sur les pages indexables, sitemap et llms.txt sans page noindex, JSON-LD valide et sans marqueur. Code de sortie 1 en cas de problème.
- Lancer les deux avant chaque push.
