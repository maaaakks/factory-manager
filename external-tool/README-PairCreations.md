# Prisme, Canopée et Bastion

21 octobre 2026. La collection compte huit créations, deux dans chacune des quatre catégories.

| Catégorie | Première création | Seconde création |
| --- | --- | --- |
| Industriel | Atlas | Aster, inspiration aéronautique |
| Futuriste | Lumen | Prisme |
| Organique | Sylva | Canopée |
| Brutaliste | Monolithe | Bastion |

## Prisme

Deux volumes facettés de tailles différentes. La toiture du volume principal mêle pans à 45°, vitrage oblique et plateau supérieur. Le petit pavillon tourne de 30° dans le plan et conserve sa position lorsque la halle s’agrandit. Il a été décalé pour dégager les trajets logistiques du cas témoin. Les fenêtres rectangulaires restent sous les pentes ; leurs pointes sont fermées par des cours contigus de poutres natives peintes.

## Canopée

Une grande coque en sept facettes, dont les angles successifs composent une voûte plutôt que des terrasses. Les panneaux natifs de 8 m gardent leur longueur. Le sommet est vitré, les rives sont épaisses et l’entrée possède un porche arrondi à taille fixe. L’élargissement insère des panneaux au sommet, tout en conservant les deux flancs inclinés. Le rendu reste polygonal, sans prétendre à une courbe lisse ou à un matériau organique réel.

## Bastion

Une composition basse, contrastant avec la porte verticale de Monolithe. Une dalle s’avance devant la façade reculée ; des ailes de hauteurs différentes encadrent une cour latérale traversante au niveau du sol. Les vitrages bas ont été dégagés devant les passages logistiques. Les strates, les retours pleins et l’annexe basse ancrent le bâtiment dans le terrain.

## Dimensions et validation

Chaque étude utilise les vues d’architecte, la rotation à la souris, le contrôle des vitrages et les menus de largeur et longueur existants. Largeur 64–96 m, longueur 48–80 m, par travées de 8 m ; hauteur minimale 32 m. Les machines et les réseaux du cas de cuivre ne sont pas déplacés. Les volumes secondaires sculptés peuvent rester fixes pendant l’agrandissement de la halle principale.

75 nouvelles combinaisons comparées entre JavaScript et Python ; rotations de panneaux normalisées, poutres limitées à 16 m, flancs inclinés conservés et source du projet immuable. Quinze formats natifs relus pour les trois études (base, extrêmes et intermédiaires), avec régénération des études affinées. Les 125 variantes des cinq créations précédentes ont été comparées à la version installée et gardent exactement la même géométrie. Chaque catégorie contient exactement deux études.

Les fichiers fournis comprennent les formats de base et maximaux, chacun avec JSON et paire SBP/SBPCFG. Les formats XL restent expérimentaux : placement, matériaux, lumière et collisions réelles des meshes restent à contrôler dans Satisfactory. Aucun dossier du jeu n’a été modifié.

Recette éditable : tools/build_pair_creations.py, puis tools/build_architecture_catalog.py. Les paramètres fixedLayout, repeatWidth et stretchWidthEnd servent à préserver les pavillons et les facettes dans les deux interpréteurs, sans déformer les actifs natifs.
