# Trois nouvelles architectures

21 octobre 2026. Les trois créations originales rejoignent Atlas et Lumen dans la galerie. Le filtre Nouvelles études les compare côte à côte sur grand écran.

| Création | Direction | Décisions de composition |
| --- | --- | --- |
| Sylva | Paysage en terrasses, teintes sauge | Trois gradins, bandeaux pleins, pavillon vitré décentré, rives claires, jardinières vides en pièces natives. Quatre volées d’escalier et deux paliers rejoignent la terrasse basse par une vraie ouverture dans le toit. |
| Monolithe | Brutalisme monumental | Deux massifs opaques de 8 m de largeur, un linteau haut, un vitrage reculé et un auvent sombre beaucoup plus bas. Un filet bronze souligne le seuil. |
| Aster | Inspiration aéronautique | Pans de toiture natifs inclinés, épine vitrée haute, appuis en diagonale et avancée basse en guise de nez. Les arêtes suivent les pentes réelles des pièces. |

Ces styles changent la silhouette, les pleins et les vides, les niveaux et la toiture. Ils ne sont pas des recolorations d’Atlas ou de Lumen. La palette décrit les couleurs paramétrées dans les pièces ; les matériaux réels restent à contrôler dans Satisfactory.

Chaque création propose les vues Composition, Façade, Coupe et Arrière, les vitrages, les dimensions et le JSON correspondant au format choisi. Largeur de 64 à 96 m et longueur de 48 à 80 m, par travées natives de 8 m ; la hauteur minimale reste de 32 m. Les machines de l’exemple cuivre restent à leur place. Ce n’est pas un placement automatique de production et les collisions sont refusées.

Validation : comparaison JS/Python de 75 nouvelles combinaisons, vérification de l’immuabilité du projet et des segments de poutres de 16 m maximum, conservation des quatre escaliers de Sylva dans les variantes, quinze exports natifs relus pour les trois créations (formats de base, extrêmes et intermédiaires). Sylva a ensuite été affinée ; ses cinq exports ont été régénérés et relus. Les fichiers fournis comprennent les formats de base et maximaux avec JSON, SBP et SBPCFG.

Les modèles et réseaux sont vérifiés hors du jeu. Les formats XL, les collisions des meshes, les matériaux, l’éclairage et la circulation réelle restent expérimentaux. Les jardinières ne contiennent pas de végétation ; aucun effet lumineux ou végétal n’est simulé. Aucun dossier du jeu n’a été modifié.

La recette complète est tools/build_new_creations.py. Régénérer ensuite le catalogue navigateur avec tools/build_architecture_catalog.py. La page de détail s’alimente maintenant depuis les métadonnées du catalogue ; chaque nouvelle création dispose de ses textes et de ses règles de coupe sans dupliquer la page.
