# Exploration : carte, usines et flux physiques

## Interface

- Navigation publique : Explorateur / Atelier (URL `/design` conservée).
- Textes d’introduction, en-tête au-dessus de la carte, filtre d’altitude et rayon de proposition retirés.
- Ouvrir la sauvegarde est l’action primaire dans le panneau gauche, avec un +. Sans sélection, le sélecteur de fichier .sav s’ouvre. La liste ne présélectionne plus arbitrairement une sauvegarde.
- Fond dans la carte en haut à droite ; Délimiter une usine en couleur primaire en bas à gauche ; gestes sous la carte.
- La croix ferme l’inspection et libère la place. Le bouton Inspection ou une nouvelle sélection la rouvre. La sélection existante est conservée.
- Ouvrir une usine proposée ou enregistrée conserve les calques. Double-clic pour inspecter un bâtiment ; clic simple sur un périmètre pour sélectionner l’usine sans déplacer la caméra. Les pastilles permettent de la cadrer.

## Détection et périmètres

Les propositions partent de concentrations de deux machines minimum. Les enveloppes fermées peuvent partitionner un groupe dense. Les connexions physiques locales réunissent les machines superposées, sans traverser les coffres ni sortir de l’emprise proposée. Les groupes dont les machines se recouvrent après ce suivi sont réunis.

La sélection manuelle inclut les bâtiments des calques masqués pour que masquer les murs n’exclue pas l’architecture de l’usine. Les propositions automatiques incluent l’architecture dans une enveloppe verticale élargie au-dessus des machines. Cela reste une proposition : espaces ouverts, bâtiments voisins et architecture très haute peuvent nécessiter une délimitation manuelle.

## Vue 3D

Moteur WebGL partagé avec l’Atelier ; géométrie envoyée une fois au GPU. Rotation et inclinaison au glisser, molette pour zoomer, Maj + glisser / clic droit pour déplacer. Boutons Perspective / Face / Côté et Recentrer. Aucun slider.

Les toitures sont visibles par défaut et masquables. Rotations quaternion des acteurs et instances légères conservées. Volumes schématiques pour les toits inclinés, rampes de murs, rampes inversées et murs inclinés. Les dimensions des autres machines restent approximatives, sans modèles du jeu. Repli SVG si WebGL indisponible. Aperçu limité explicitement à 10 000 objets ; destruction de l’observateur au retrait du dialogue.

## Ressources et transport

`FactoryMetrics.transportReport` suit les ports réciproques depuis chaque producteur, puis les convoyeurs et répartiteurs jusqu’aux premières machines/coffres. Un graphe de capacité par bâtiment garantit qu’un convoyeur partagé n’est pas compté deux fois. Affectation d’abord aux besoins internes, puis aux coffres. Le coffre reste la frontière de sortie, même s’il alimente autre chose ensuite.

Le tableau indique le débit acheminable estimé, les plafonds par convoyeur et les sections saturées. Les trajets inconnus, multi-produits, ports ambigus et convoyeurs non reconnus restent signalés. Les sources amont pour les recettes multi-ingrédients sont recherchées sans inventer leur attribution aux ports.

**Limites :** estimations par ressource à cadence enregistrée ; pas de simulation de la propagation d’une pénurie sur toutes les recettes, de répartition réelle des splitters, des capacités de stockage restantes ou de concurrence entre plusieurs ressources sur une même bande. Pureté des mineurs non établie. Aucun débit instantané mesuré : un fichier de sauvegarde ne donne pas une télémétrie en direct.

## Validation

- 20 suites Node, dont goulot partagé Mk.1/Mk.2, arrêt au premier coffre, ports réciproques et rotations/murs inclinés.
- Vérification Python des catégories, cadences et persistance isolée.
- Test navigateur Chrome avec une sauvegarde de 35 323 constructions : sélection directe, fermeture/réouverture du panneau, conservation des calques, délimitation et aperçu WebGL.
- Aucune écriture dans les sauvegardes du jeu.
