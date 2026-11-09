# Chapitre II — Atelier signature

21 octobre 2026. Première tranche implémentée, à affiner en jeu.

## Catalogue simplifié

M05 · Entrepôt modulaire reste indépendant. Les onze autres familles sont réunies dans **Classiques procéduraux** : le bouton de variation explore leurs règles et ne propose que les contenus débloqués. Les anciens identifiants restent lisibles, afin de conserver les compositions des projets enregistrés. Le catalogue présente ensuite **Chapitre II · Atelier signature**.

## Références examinées

- [TotalXclipse — 7 Steps To Better Factory Designs](https://www.youtube.com/watch?v=sMarWMlGAjE) : chapitres et description consultés, avec observation visuelle du traitement des baies. 0:51 profondeur ; 1:18 textures ; 1:50 lumière naturelle ; 2:27 modules réutilisables ; 3:01 détails superposés ; 4:21 couleurs ; 5:18 éclairage ; 6:26 finitions. La transcription est restée indisponible : ces notes ne prétendent pas restituer toutes les explications orales.
- [Reekitect — Compact Factory](https://www.youtube.com/watch?v=Js7zbvNY7CM) : séquences visuelles consultées. Cadres facettés, contours interrompus, longues lignes lumineuses, contrastes clairs/sombres et supports de circulation dessinés. Nous retenons le vocabulaire, sans reproduire son bâtiment.
- [Tenhope — Very Busy Screw Factory](https://www.youtube.com/watch?v=IMOjMljmZ-o) : séquence visuelle autour de 40 secondes. Machines exposées, niveaux distincts, escaliers et passerelles, structure noire et accents jaunes. Cette référence appelle un futur travail sur la structure de production ouverte, au-delà d'un habillage.

## Trois propositions construites

| Composition | Intention | Géométrie actuelle |
|---|---|---|
| Horizon | Clean, horizontal et calme | Corps clair, socle graphite, deux niveaux de vitrage sur les bâtiments hauts, aile supérieure en retrait, portique facetté sombre et petits accents cuivrés. |
| Faille | Une asymétrie lisible | Fente verticale de façade, vitrage vertical localisé, retour latéral étagé, palette ardoise et accents ivoire. |
| Ossature | Un premier vocabulaire industriel | Angles supérieurs retirés, vitrage par travées, persiennes et contreventements ponctuels, accent ocre sur structure sombre. Il s'agit encore d'une enveloppe, pas de la fabrique ouverte de Tenhope. |

Les trois compositions partagent une hiérarchie : silhouette → masses et ouvertures → tableaux de baie → accents localisés → détails de toiture. Elles n'ajoutent pas une décoration différente au hasard sur chaque panneau. Le bouton de variation de cette famille parcourt trois compositions ; les anciens styles conservent leur cycle historique. Les couleurs des machines et des réseaux restent indépendantes ; choisir cette nouvelle famille libère les anciens overrides des murs, cadres, vitrages et toits pour montrer sa palette.

## Traduction des guidelines

| Principe | Cette tranche | Raffinement suivant |
|---|---|---|
| Profondeur | Retraits de volumes selon les cases libres ; cadres de baies et lames sur deux plans. | Volumes inclinés ou courbes et véritables auvents composés. |
| Textures | Socle sombre, parois et vitrages hiérarchisés ; persiennes locales. | Bibliothèque de bardages et détails de jonction inspectés en jeu. |
| Lumière naturelle | Baies groupées, bande vitrée de toiture. | Répartition des verrières selon les travées de production. |
| Modules | Trois compositions déterministes partagées entre aperçu JS et export Python. | Sous-ensembles d'entrée, angle et couronnement sélectionnés indépendamment dans une grammaire cohérente. |
| Détails superposés | Tableaux, appuis, linteaux, lames, portique facetté, rives de toiture. | Gouttières, équipements techniques et raccordements des pieds de façade. |
| Couleurs | Palette sobre par composition, accent localisé. | Réglage du rapport matières/couleurs avec comparaison en jeu. |
| Éclairage | Les vitrages et repères actuels restent non émissifs. | Enseignes natives, guides lumineux, contraste jour/nuit ; validation de leur sérialisation et de leur rendu. |
| Finitions | Toits et terrasses fermés par les règles natives ; détails bornés et vérifiés contre les obstacles. | Inspection en jeu des joints, collisions, reflets et matériaux ; accès réellement parcourables. |

## Contraintes actuelles

Les machines, recettes et réseaux restent en place. Une case occupée ou traversée empêche le retrait ; un portique bloqué est omis en entier. Un plan très dense peut donc garder une silhouette plus simple. Réserver une marge d'habillage est conseillé pour juger ce style, mais n'est pas imposé automatiquement. Les détails vérifient les emprises et les parcours connus ; cela ne représente pas un test de collision avec les meshes du jeu.

Les exemples JSON fournis sont des maquettes d'habillage sur 48 × 40 m avec une machine de repère, pas des chaînes de production complètes ni les blueprints des auteurs. Importer le JSON dans l'atelier permet de comparer les variantes puis d'appliquer la famille à un vrai plan.

## Vérification

- 15 scènes Signature : formats carrés et rectangulaires, trois compositions, variantes et cycle, déterminisme, bornes, panneaux complets au sens du plan, préservation des données, verrous, sérialisation et protection des cellules occupées.
- Ces 15 scènes ont la même géométrie JS/Python et les mêmes masques de sols ; export `.sbp` temporaire et relecture binaire réussis.
- 168 scènes de familles : déterminisme, verrous et bornes. 42 combinaisons famille/variante : parité JS/Python et relecture binaire.
- Vérifications ciblées des façades modulaires, silhouettes, lisibilité/accès, apparence historique, kit M05, petits M05 et aperçu GPU.
- Trois maquettes contrôlées dans le navigateur, catalogue simplifié et variations vérifiés.
- Les tests historiques `check_workshop_design.cjs` et `check_architecture_compositions.cjs` demandent encore des réservations automatiques de trémies supprimées dans le comportement existant ; leur échec est également reproductible sur la source initiale. Le test historique `check_simple_planning.cjs` suppose un étage unique pour une demande verticale et échoue aussi sur la source initiale. Ils ne sont pas comptés comme réussis.

Aucune écriture dans une sauvegarde ou dans les dossiers de blueprints du jeu. Les relectures binaires et l'aperçu local ne constituent pas une validation visuelle ou fonctionnelle dans Satisfactory.
