# Atlas conservé, Lumen et extension par travées

21 octobre 2026.

Atlas reste la halle industrielle de référence, avec sa recette native et son exemple original conservés. Lumen est une seconde étude : silhouette plus basse, coque claire, large visière en porte-à-faux, vitrage horizontal, pavillon d’entrée asymétrique et services dans une annexe fermée. Les accents cyan sont des poutres peintes ; ils ne sont pas émissifs.

Les deux compositions acceptent une profondeur de 48, 56, 64, 72 ou 80 m, à largeur constante de 64 m. Le sélecteur de la page 3D insère des travées arrière de 8 m, conserve l’entrée et les six escaliers d’Atlas, prolonge les parois et la couverture, et régénère le JSON téléchargé. Les pièces natives ne sont pas étirées ; les poutres prolongées sont redécoupées à 16 m maximum. Les machines et leurs connexions ne sont pas déplacées. Une collision avec le layout est refusée. Cette adaptation n’est donc pas un habillage automatique de n’importe quel plan, ni une adaptation en largeur ou en hauteur.

Les deux sens de glissement ont été inversés dans l’étude et dans la prévisualisation de l’atelier ; les flèches suivent les mêmes commandes. La géométrie et les coordonnées des exports ne sont pas permutées.

Validation : les 10 combinaisons style/profondeur ont une géométrie cohérente entre JavaScript et Python, un export natif généré et relu, et des poutres sous la limite native. Atlas garde six volées d’escalier à chaque longueur. Le projet source reste inchangé pendant la génération. L’export témoin de cuivre sert à vérifier le réseau ; il n’est pas optimisé pour remplir les plus grandes variantes.

Les fichiers JSON sont importables dans Factory Manager. Chaque SBP est accompagné de son SBPCFG. Aucun fichier n’a été installé dans les dossiers du jeu. Tous ces formats dépassant le designer vanilla sont expérimentaux ; ni les matériaux, ni l’éclairage, ni les raccords réels des meshes, ni le placement en jeu n’ont été validés.

Sources éditables : tools/build_atlas_study.py et tools/build_lumen_study.py ; catalogue partagé data/architecture-styles.json ; extension native authored_layout.py et son équivalent dans dist/workshop-design.js. Régénérer le catalogue navigateur avec tools/build_architecture_catalog.py après modification d’une recette. Les quatre références vidéo d’Atlas restent documentées dans son dossier ; Lumen est une proposition originale de direction futuriste.
