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
/techniques-soudure/            Pilier : procédés, réglages, positions, sécurité et santé du soudeur
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
- Chaque article déclare UNE seule catégorie dans son en-tête, `category: ...`, parmi : `formation-soudure`, `techniques-soudure`, `carriere-soudeur`, `entreprendre-soudure`, `ia-soudure`. Jamais `categories:`.
- Les articles sur les outils vont dans `ia-soudure`.
- Le gabarit ajoute le fil d'Ariane, le lien vers le pilier et « À lire aussi » (jusqu'à 3 articles de la même catégorie).
- Vidéo : `intro` (Markdown, affichée avant la vidéo), `youtube_id`, `video_title`, `video_description`, `video_thumbnail`, `video_duration`, `video_upload_date` et `chapters`, avec des valeurs réelles relevées sur YouTube. Le gabarit génère le JSON-LD VideoObject avec un Clip par chapitre.
- Vidéos complémentaires (plusieurs vidéos sur le même sujet, un seul article pour éviter la concurrence entre articles) : liste `videos_complementaires` dans l'en-tête, mêmes champs que la vidéo principale. La vidéo principale reste en haut ; chaque vidéo complémentaire est placée une seule fois dans la section qu'elle illustre avec `{% include video-complementaire.html id="<youtube_id>" %}`. Un VideoObject par vidéo est généré automatiquement.
- Le lecteur YouTube (youtube-nocookie.com) est chargé directement dans la page, sans attendre de clic, pour que Google détecte la vidéo : ce choix est déclaré dans la politique de confidentialité (stockage local du lecteur, domaines Google contactés).
- Sous chaque H2 formulé en question : une réponse directe de 40 à 60 mots, puis le développement.

## Stratégie des outils

- mapleleafsoudure.com porte le contenu, le référencement et la présentation commerciale des outils.
- Chaque outil a une page de présentation `/outils/<nom>/` et une carte dans `_data/outils.yml`.
- Les applications tournent sur des sous-domaines séparés construits avec Lovable (ex. harword.mapleleafsoudure.com), hors de ce dépôt.
- Ne créer aucun lien vers un sous-domaine ou une URL qui n'existe pas encore : laisser le champ vide (`lien_externe`, `depot_github`, `documentation`), le gabarit n'affiche alors rien.
- Harword : open source sur GitHub (installation en autonomie) et installation sur site sur devis (bouton vers Calendly).

## Règles de publication

- Aucune page indexable ne doit contenir de marqueur `[[ ... ]]`. Une page en cours reste en `robots: "noindex, follow"`, `sitemap: false` et `llms: false` dans son en-tête, à retirer une fois terminée.
- Aucun JSON-LD sur des valeurs non confirmées : le préparer en commentaire HTML (ex. SoftwareApplication de Harword) ou le générer seulement quand les données existent (ex. FAQPage depuis le champ `faq`).

## Articles à réviser chaque année

Articles contenant des chiffres réglementaires ou datés (cotisations, plafonds, ACRE, TVA, salaires, taux de change, loyers). Chaque année (en janvier, et en juillet pour les mesures qui changent en cours d'année), revérifier ces chiffres sur leurs sources, corriger l'article, mettre à jour la mention « Chiffres à jour au … » et la date de vérification ci-dessous. Tout nouvel article avec ce type de chiffres est ajouté à cette liste, et ses données réglementaires portent la mention visible « Chiffres à jour au <date> ».

Les chiffres tirés d'une vidéo (témoignage, offre d'emploi analysée) ne se « mettent pas à jour » : ils restent datés de la vidéo. Seules les règles officielles sont corrigées.

### `/carriere-soudeur/salaire-soudeur-canada/` (`_posts/2026-10-12-salaire-soudeur-canada.md`), vérifié en octobre 2026

- Heures supplémentaires au Québec : taux et demi (+50 %) au-delà de 40 h par semaine. Source : [CNESST](https://www.cnesst.gouv.qc.ca/fr/conditions-travail/salaire-paye/salaire/heures-supplementaires).
- PVT : 18 à 35 ans inclus, jusqu'à 24 mois, permis ouvert. Source : [IRCC, Expérience internationale Canada](https://www.canada.ca/fr/immigration-refugies-citoyennete/services/travailler-canada/eic.html).
- Citoyenneté : 1 095 jours de présence sur 5 ans, dont 730 comme résident permanent. Source : [IRCC, admissibilité](https://www.canada.ca/fr/immigration-refugies-citoyennete/services/citoyennete-canadienne/devenir-citoyen-canadien/admissibilite.html).
- Carte de résident permanent valide 5 ans. Source : [IRCC, carte RP](https://www.canada.ca/fr/immigration-refugies-citoyennete/services/residents-permanents/carte.html).
- Mobilité francophone : permis de travail hors Québec avec offre d'emploi, pas de résidence permanente directe. Source : page « Mobilité francophone » d'IRCC (canada.ca).
- Plafond CELI : 7 000 $ en 2026. Source : [Agence du revenu du Canada](https://www.canada.ca/fr/agence-revenu/services/impot/particuliers/sujets/compte-epargne-libre-impot/cotisations.html).
- Taux de change : « entre 1,50 et 1,60 $ pour 1 € selon la période », conversions au taux de 1,60 $ (mai 2026) : 2 891 € net, 619 € de loyer, 21,90 à 23,30 € brut de l'heure. À revoir si le taux sort de cette fourchette.
- Chiffres datés des vidéos (ne pas actualiser, garder la date) : offre à 29 à 40 $ brut de l'heure, 6 933 $ brut et 4 622 $ net par mois (mai 2026, vidéo 020) ; loyer de 990 $ (mai 2026) ; offres lyonnaises à 13,30 à 14,30 € brut de l'heure, 1 692 € et 2 275 € net (mai 2026) ; 13 à 13,50 € brut de l'heure en intérim (départ en 2023).

### `/entreprendre-soudure/soudeur-independant-salaire-tarifs/` (`_posts/2026-10-19-soudeur-independant-salaire-tarifs.md`), vérifié le 19 octobre 2026

Mention visible « Chiffres à jour au 19 octobre 2026 » à mettre à jour, ainsi que le tableau des revenus nets (recalculé avec ces taux).

- Cotisations micro-entreprise, prestations de services commerciales et artisanales (BIC) : 21,2 % ; contribution à la formation professionnelle des artisans : 0,3 % ; versement libératoire services BIC : 1,7 %. Source : [autoentrepreneur.urssaf.fr](https://www.autoentrepreneur.urssaf.fr/portail/accueil/sinformer-sur-le-statut/lessentiel-du-statut.html).
- ACRE : 15,9 % pendant 12 mois pour une activité commencée depuis le 1er juillet 2026 (10,6 % avant) ; demande à l'Urssaf dans les 60 jours, conditions restreintes depuis le 1er janvier 2026. Sources : [Service-Public.fr](https://entreprendre.service-public.fr/vosdroits/F11677), [urssaf.fr](https://www.urssaf.fr/accueil/actualites/acre-nouvelles-regles-demarches.html).
- Plafond de chiffre d'affaires, prestations de services : 83 600 € (2026). Franchise en base de TVA, services : 37 500 €, seuil majoré 41 250 €. Source : autoentrepreneur.urssaf.fr (ci-dessus).
- ARCE : 60 % des droits ARE restants, en deux versements, ou maintien partiel de l'ARE. Source : [France Travail](https://www.francetravail.fr/candidat/je-creereprends-une-entreprise/les-aides-financieres-creation-d/aide-a-la-reprise-et-a-la-creati.html).
- Chiffres datés des vidéos (ne pas actualiser) : 4 500 à 5 000 € super net par mois quand j'étais à mon compte en France ; 73 € de l'heure sur chantier (2020) ; 50 € de l'heure chez les particuliers ; simulation à 30 € de l'heure et 29,25 € la pièce ; taux de la vidéo (fin 2025) : ACRE à 10,6 %, total 12,3 %.

### `/formation-soudure/titre-pro-cqpm-cqp-soudeur-industriel/` (`_posts/2026-10-12-titre-pro-cqpm-cqp-soudeur-industriel.md`), vérifié en octobre 2026

- Taux d'insertion, nombres de certifiés et VAE (2021 et 2022), fiches et dates d'enregistrement. Sources : France Compétences, [RNCP 40037](https://www.francecompetences.fr/recherche/rncp/40037/) (Titre Pro) et [RNCP 39243](https://www.francecompetences.fr/recherche/rncp/39243/) (CQPM). Ajouter les années plus récentes quand elles sont publiées.
- Salaire en intérim : 1 900 à 2 000 € net par mois (témoignage de la vidéo, à garder daté).

## Vérifications

- `bash _outils/verifier-nom.sh` : aucun nom réel hors `/mentions-legales/` (noms lus dans `.noms-interdits`, fichier local non versionné).
- `bundle exec ruby _outils/verifier-contenu.rb` : catégories des articles, marqueurs sur les pages indexables, sitemap et llms.txt sans page noindex, JSON-LD valide et sans marqueur. Code de sortie 1 en cas de problème.
- `py -3.12 _outils/verifier-article.py _posts/<fichier>.md` : en-tête, champs vidéo et chapitres, réponses directes de 40 à 60 mots, tirets cadratins, marqueurs, liens internes ; signale les tics et les commentaires « à vérifier ».
- `py -3.12 _outils/verifier-navigateur.py [--article /<catégorie>/<slug>/]` : construit et sert le site, puis contrôle dans Chrome le bandeau et le consentement sur toutes les pages, les liens internes, la page de vente (99 € et 69 €) et la position de la vidéo d'un article. Prérequis : `py -3.12 -m pip install --user playwright`.
- Lancer `verifier-nom.sh`, `verifier-contenu.rb` et `verifier-navigateur.py` avant chaque push.

## Commande /article

`/article <numéro> <lien YouTube>` (fichier `.claude/commands/article.md`, local) : crée un article à partir de l'unique fichier `.mp4` ou `.mov` du dossier `E:\01_MAPLE_LEAF_SOUDURE\Articles\Videos\<numéro>\` (nom libre ; s'il y en a zéro ou plusieurs, la commande s'arrête et demande), puis s'arrête avant publication.

`/article <numéro> <lien YouTube> --avec <numéro> <numéro> ...` : même chose avec des vidéos complémentaires (même sujet). Elles sont aussi transcrites, servent de sources supplémentaires et sont intégrées dans l'article (lecteur et VideoObject), la vidéo principale restant en haut.

Liste de référence : `E:\01_MAPLE_LEAF_SOUDURE\Articles\Videos\liste-videos.md` (hors dépôt) : numéro, sujet, titre, lien, date de publication, durée, fichier et statut de l'article de chaque vidéo longue de la chaîne. Les numéros suivent l'ordre de publication (001 = la plus ancienne). La commande y lit les liens des vidéos complémentaires et y met à jour les statuts.

1. Transcription : `py -3.12 _outils/transcribe.py <vidéo> --model medium --nom <numéro>` (corrections `_outils/corrections.json` et glossaire `_outils/glossaire-local.txt` chargés automatiquement ; fichiers produits à côté de la vidéo, nommés d'après le numéro : `<numéro>.srt`, `<numéro>_transcript.md`, `<numéro>_transcript.txt`).
2. Compréhension de la transcription et choix d'une catégorie.
3. Recherche SEO : `_outils/seo_cluster.py` (identifiants DataForSEO dans `DATAFORSEO_LOGIN` et `DATAFORSEO_PASSWORD`), lancé depuis le dossier de la vidéo ; seules les requêtes fidèles au contenu sont gardées.
4. Données réelles de la vidéo : `py -3.12 _outils/youtube_infos.py <lien>`.
5. Rédaction selon les règles de ce fichier ; commentaire « à vérifier » en cas d'ambiguïté.
6. Vérifications (les quatre scripts ci-dessus et le validateur schema.org), commit sans push.
7. Arrêt : URL locale de relecture, points « à vérifier », description YouTube mise à jour de chaque vidéo, enregistrée dans `<dossier de la vidéo>\description-youtube.txt` (hors dépôt, à remettre à jour si l'article est corrigé). Push seulement après accord.

`_outils/glossaire-local.txt` contient des noms sensibles (clients, personnes) : il n'est jamais versionné.
