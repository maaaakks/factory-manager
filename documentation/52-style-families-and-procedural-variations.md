# 52 — Familles architecturales et variations procédurales

20 octobre 2026.

## Utilisation

Dans **Atelier → Design → Façades**, choisir une catégorie puis une famille. Un clic applique une composition complète. **Varier ce style** propose la variante suivante de la même famille. La catégorie sert à parcourir le catalogue : elle ne remplace pas le design tant qu'une nouvelle carte n'est pas choisie.

| Catégorie | Familles | Grammaire |
|---|---|---|
| Industrie | Entrepôt modulaire, Hangar industriel, FICSIT industriel | Ossature tramée ou montants verticaux, socles pleins, baies groupées, bandeaux ou éclairage haut. |
| Vitré & contemporain | Campus vitré, Façade technologique | Vitrages plus présents, montants réguliers, palettes claires ou froides et verrières composées. |
| Béton & infrastructure | Atelier béton, Béton monumental | Remplissages minéraux, trame ou pilastres, fenêtres groupées ou bandeaux. |
| Utilitaire | Compact fonctionnel | Enveloppe rectangulaire sobre, sans trame décorative extérieure. |

Les cartes montrent une vignette de matières et la famille active. Le panneau indique la variante courante et sa composition : type d'ossature, rythme des ouvertures et traitement d'entrée. Les packs déclarés débloqués continuent de limiter les choix.

## Inspiration Modular Warehouse

Référence : [M05_MODULE (modular warehouse), JazzFrank](https://satisfactoryblueprints.com/blueprint/c255f7b1-4337-4197-b6f6-56223b05e4a1).

L'analyse du fichier de référence effectuée en documentation 51 a relevé 289 acteurs, notamment des murs, plusieurs fenêtres, poutres, portes, toits, passerelles, ventilation et raccordements. La famille **Entrepôt modulaire** reprend les principes de trame répétable, socle plein, baies groupées, structure apparente, toiture coordonnée et portique en retrait. Il s'agit de notre propre composition procédurale ; aucun ensemble de géométrie du blueprint tiers n'est recopié.

La première version utilise les murs, fenêtres, toits et poutres natifs déjà pris en charge. Elle n'importe pas encore l'ensemble des ventilateurs, évents, escaliers et passerelles décoratives du modèle de référence. L'entrée est un portail ouvert, pas une porte à vantail animé.

## Ce qui varie

- **Fenêtres** : groupes symétriques, bandeaux horizontaux, alternance de travées, vitrage haut ou grandes façades vitrées selon les règles de la famille. Le rez-de-chaussée conserve son socle plein hors accès. Un petit bâtiment conserve un niveau vitré même lorsque le motif de bandeau aurait demandé un étage absent.
- **Palette** : combinaisons coordonnées de remplissage, ossature et vitrage ; changement progressif entre plusieurs variantes. La couleur des machines est indépendante.
- **Toiture** : puits central, verrière longitudinale, groupes symétriques ou groupes de trois/quatre selon la famille. La composition existante tient compte des coins retirés et peut revenir à un puits central si les groupes ne tiennent pas. Le hangar peut utiliser les pentes si la hauteur disponible le permet.
- **Entrée** : cadre simple, entrée avec poutres brise-soleil, ou double portique en retrait. Les éléments complémentaires restent dans le volume du blueprint et dans l'approche dégagée.
- **Contour** : angles en retrait sur les familles architecturales quand les coins sont libres. Le profil compact conserve le rectangle.

Le numéro de variante est déterministe et enregistré dans le projet. Recharger le même projet restitue les mêmes pièces. Les matières, trames et proportions de base restent liées à la famille, plutôt que d'être tirées au hasard indépendamment sur chaque panneau. Après la variante 999, le cycle repart à 1.

Les commandes « Rafraîchir les murs » et « Rafraîchir le toit » conservent leur portée : elles avancent les motifs de la partie concernée dans la famille active. Le bouton principal fait varier la composition complète.

## Contraintes et export

Cette passe modifie l'architecture ; l'implantation des machines, les recettes, les débits, les réseaux et les sols du plan restent en place. Le moteur conserve les contrôles d'emprise, de hauteur et de collision des pièces architecturales contre les volumes d'objets. L'entrée utilise les contrôles d'approche et de transport de la documentation 51. Une proposition impossible ne remplace pas le projet.

Les montants et traverses sont des poutres natives exportables. Des plans de profondeur distincts séparent montants, traverses, croisements, murs et cadres de baies, pour limiter les faces coplanaires. Les contours des verrières dans l'aperçu utilisent la palette de la famille.

Le moteur ne redistribue pas encore la production pour créer des ailes libres ou un bâtiment en L sur mesure : les retraits concernent les coins libres. Les contraintes peuvent empêcher un portail ou certaines décorations. L'absence de défaut visuel en jeu reste à vérifier dans un test réel.

Les projets antérieurs reçoivent les valeurs neutres : famille personnalisée, palette historique, aucun nouveau quadrillage. Le choix explicite d'une famille active les nouvelles règles.

## Catalogue extensible

La source est `external-tool/data/architecture-styles.json`. Elle décrit les catégories, palettes, familles, motifs admissibles, compositions de toit et traitements d'entrée.

Après modification, lancer `external-tool/tools/build_architecture_catalog.py` avec le Python du projet : il valide les références et génère `dist/architecture-catalog.js`. Le navigateur et l'export Python utilisent ce même catalogue. Les nouveaux types de géométrie demandent toujours une implémentation commune dans les deux moteurs et des tests de parité.

## Vérifications

- 96 scènes de style : huit familles, trois formats et plusieurs variantes, géométrie déterministe, fenêtres sur les petits bâtiments, bornes, verrous de packs, sérialisation et absence de modification de la production.
- 24 combinaisons famille/variante : égalité de la géométrie JS/Python et exports `.sbp` relus après écriture dans des dossiers temporaires.
- Trois variantes Entrepôt sur le plan calibré **120 minerais de fer → 10 plaques renforcées/min**, avec conservation des objets, liaisons, sols et débits.
- Tests existants de l'atelier et de l'architecture : parité, poutres, rampes, toiture, transport et contraintes.
- Navigateur : navigation entre catégories, application de famille, variantes successives et conservation de la variante 3 après rechargement.

Aucun export n'a été écrit dans les dossiers du jeu pendant cette passe. Les validations binaires et visuelles locales ne sont pas une nouvelle validation en jeu.
