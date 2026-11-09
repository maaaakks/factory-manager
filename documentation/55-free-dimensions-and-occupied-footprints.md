# Dimensions libres et emprise adaptée

## Utilisation

- **Atelier → Format → Libre…**, ou bouton **Dimensions** : largeur et profondeur en fondations, hauteur en mètres. Appliquer valide le volume avant de modifier le projet ; une réduction incompatible est refusée sans perte.
- **Calculator → Format du blueprint → Libre** : les mêmes trois valeurs créent un nouveau projet, sans adapter ni réduire le projet ouvert.
- Exemple : **12 × 6 fondations, hauteur 128 m** = terrain de **96 × 48 × 128 m**.

Les trois axes sont indépendants. Les formats classiques 4×4, 5×5 et 6×6 restent disponibles. Une fondation mesure 8 m ; les dimensions libres utilisent un pas de 8 m, entre 8 et 512 m par axe. C’est une borne technique de l’outil, pas une promesse de taille maximale supportée par le jeu. La hauteur affichée est le plafond autorisé, pas la hauteur imposée au bâtiment.

Les anciens JSON restent lisibles. `size` représente toujours l’axe X ; les nouveaux champs `depth` et `height` sont facultatifs et valent `size` s’ils sont absents. Les redimensionnements agrandissant le terrain conservent le centrage relatif par axe, les réseaux natifs, les chemins et les trémies. Les objets du tampon restent dans le tampon.

## Terrain et bâtiment sont distincts

Les dimensions libres activent **Suivre les bâtiments**. Le contour tient compte des volumes des objets et des chemins de convoyeurs, avec 4 m de marge avant arrondi aux cellules de 8 m. Il conserve les retraits externes et comble les petits vides intérieurs fermés. Il peut produire des ailes ou plusieurs pavillons plutôt qu’un rectangle plein.

Ainsi, un terrain carré 12×12 peut contenir une usine allongée, et un terrain 12×6 peut contenir une usine plus petite. Les murs, fenêtres, toits et sols suivent cette emprise. Les sols la suivent aussi sans habillage de façade.

Dans **Design → Façades → Personnaliser murs et toiture → Emprise du bâtiment**, choisir :

- **Suivre les bâtiments · marge de 4 m** ;
- **Occuper tout le terrain** pour conserver une enveloppe volontairement large.

Les profils en L/U/croix s’appliquent à l’emprise obtenue. Les retraits verticaux de l’Entrepôt modulaire utilisent ses propres bords et protègent les machines et convoyeurs. Les lanterneaux sont centrés sur l’emprise réelle. L’orientation des motifs et les compositions de vitrage prennent en charge les rectangles.

Ce contour n’est pas un nouveau solveur qui remplit une architecture imposée : les machines sont placées d’abord. Les modules calibrés de plaques renforcées gardent leur cœur compact, centré dans le terrain disponible.

## Construction, calculateur et visualisation

Le plan, les règles, le tampon, les collisions, les déplacements, l’altitude, l’occupation au sol, le cadrage 3D, les réseaux et les cartes de projets utilisent leurs axes respectifs. Le routeur respecte des bornes X/Y différentes et une hauteur indépendante.

Le projet accepte jusqu’à 1 000 objets placés ou en tampon, 5 000 liens et 64 planchers. La préférence d’étages peut aller jusqu’à 64 ; le calculateur conserve sa limite de 100 machines et ne garantit pas de trouver toute implantation géométriquement possible. Les limites physiques des équipements demeurent, notamment les élévateurs individuels de 48 m maximum.

## Export natif XL expérimental

L’export écrit les trois dimensions dans l’en-tête SBP, en unités de 8 m, et centre chaque axe horizontal séparément. Le parseur et les contrôles de graphe prennent en charge ces en-têtes. Les cubes historiques conservent leur représentation précédente.

Les sols, trémies, cadres, murs, fenêtres, poutres, toits, convoyeurs, élévateurs et positions natives utilisent le même repère rectangulaire. Les exports libres sont signalés **XL expérimental** dans les résultats natifs. Ils doivent être testés dans SANDBOX : la relecture du fichier et la vérification des raccords ne prouvent ni son acceptation par le jeu ni sa réédition dans un designer vanilla.

Aucun fichier de jeu n’est écrit automatiquement par la sélection du format, le calculateur ou la vérification native. L’écriture reste l’action explicite **Enregistrer ce projet dans le jeu (.sbp)**.

## Vérifications

- 30 contrôles JavaScript passent, dont 32 scènes rectangulaires et hautes : 12×6, 6×12, 12×12 et 4×10, avec quatre compositions de façade et deux modes d’emprise.
- 24 scènes de parité exacte JavaScript/Python, sols compris ; export binaire et relecture avec contrôle des trois valeurs de l’en-tête.
- Deux réseaux calibrés rectangulaires conservent leurs 54 convoyeurs et 21 élévateurs ; leurs raccords sont revérifiés après relecture.
- Export générique 12×6 de 60 minerais de cuivre → 60 lingots/min : vrais ports, 10 convoyeurs, 4 élévateurs, 8 MW et relecture binaire.
- Contrôles des élévateurs génériques et des anciens styles, toitures et modules compacts.
- Parcours navigateur : redimensionnement d’un projet existant, nouvelle génération 12×6×128 m, design adapté et vérification native en lecture seule.

Ces vérifications n’ont remplacé ni projets utilisateur ni blueprints dans le jeu.
