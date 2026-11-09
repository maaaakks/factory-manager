# Façades en relief et raccords d’angle

## Utilisation

Atelier → Design → Façades → Industrie → **Entrepôt modulaire**.
**Varier ce style** parcourt trois compositions :

- Entrepôt : tours et grandes baies en retrait, avec des blocs intermédiaires.
- Galeries : travées saillantes symétriques, retraits sur plusieurs faces.
- Gradins : étages supérieurs en retrait et terrasses autour des volumes conservés.

Le réglage avancé **Relief des façades** permet de choisir directement une composition. Les autres familles conservent leur composition plane. Les anciens projets Entrepôt sans réglage de relief adoptent le mode Entrepôt ; réappliquer la carte de style actualise aussi sa palette et ses fenêtres. La variation reste annulable et ne déplace pas les machines.

## Composition réelle

La façade est calculée par tranches verticales de 4 m, avec des cellules natives de 8 m au sol. Une cellule périphérique peut être retirée à un niveau sans disparaître aux autres niveaux. Ce sont des changements du volume fermé, pas des traits décoratifs devant un rectangle.

Chaque retrait reçoit une couverture ; chaque retour d’un volume en surplomb reçoit une sous-face. Le dernier toit conserve ses formes existantes, avec les pignons et les vitrages du lanterneau. Les planchers supérieurs suivent le contour à leur propre altitude ; le rez-de-chaussée conserve la terrasse de fondations. Le couronnement est arrondi au module vertical si le format le permet.

La sélection de cellules protège les volumes de machines et les chemins de convoyeurs, avec une marge. Un retrait incompatible est abandonné localement. Les petits formats très remplis ou les bâtiments bas peuvent donc avoir beaucoup moins de relief. Ce n’est pas encore un placement des machines dans un gabarit architectural imposé.

## Angles et z-fighting

Chaque jonction convexe ou rentrante possède un seul montant. Les poteaux et diagonales concurrents sont retirés ; les traverses sont arrêtées avant le montant. Les bardages pleins de fin de travée utilisent des poutres natives de longueur ajustée : aucune réduction fictive d’un mur natif de 8 m dans la seule prévisualisation.

Les vitrages natifs gardent leurs dimensions. Leur jonction orthogonale est enveloppée par le montant commun. Les corniches ne sont plus superposées aux dernières courses du bardage d’angle. Les montants contigus sont regroupés puis découpés à la longueur native maximale de 16 m. Les nouveaux éléments sont vérifiés contre les volumes des machines.

Ce correctif vise les raccords générés par l’atelier. Il ne modifie pas les constructions déjà contenues dans une sauvegarde explorée et ne prouve pas l’absence de tout chevauchement possible dans le jeu.

## Référence M05

[M05_MODULE, JazzFrank](https://satisfactoryblueprints.com/blueprint/c255f7b1-4337-4197-b6f6-56223b05e4a1).

Le fichier de référence déjà téléchargé contient 289 acteurs. SHA-256 : `4cc3094d3bcf4696aa036224d2b3359386d9149e4e9dbbd4855c037bf83f61af`.

L’analyse des positions montre notamment plusieurs plans de façade séparés de 8 m, des blocs latéraux, une grande baie centrale, des auvents et un bandeau vitré supérieur. Le générateur reprend ces principes de composition avec sa propre géométrie. Sa palette distingue le corps orange et les cadres sombres. L’export de la famille Entrepôt emploie maintenant le véritable vitrage `Wall_Window_8x4_05`, identifié dans le fichier de référence, avec la recette et les ingrédients du catalogue local.

Ce n’est pas une copie intégrale de la collection M05. Les ventilateurs, passerelles, escaliers et modules C/M/IN complets ne sont pas reproduits. La vue 3D reste schématique et ne charge pas les modèles graphiques du jeu.

## Vérification

- 29 contrôles JavaScript, dont 9 scènes hautes couvrant trois compositions et trois formes de toit.
- Parité exacte de géométrie JavaScript/Python pour ces 9 scènes ; export binaire puis relecture.
- 33 scènes de familles et variantes ; 45 compositions natives historiques ; 12 cas de toiture historiques.
- Conservation de la production et des réseaux sur les modules calibrés de 120 minerais → 10 plaques renforcées, et contrôle de l’export générique cuivre sur un étage.
- Vérification visuelle en opaque, avec captures des compositions Entrepôt et Gradins.

Aucun projet utilisateur, fichier de sauvegarde ou blueprint en jeu n’est remplacé par les vérifications. Les nouvelles façades restent à valider en jeu.
