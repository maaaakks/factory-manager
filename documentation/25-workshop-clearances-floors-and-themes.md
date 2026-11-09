# Implantation avec dégagements, structure et thèmes

État : 19 octobre 2026. Le bouton Sélectionner / déplacer a été retiré. F, Échap, le clic dans la marge et les gestes de sélection restent disponibles.

## Problème corrigé

Le placement précédent utilisait des emplacements fixes puis vérifiait les seules collisions des rectangles. Cela ne prouvait ni l’existence de passages ni la constructibilité des raccordements. L’interface ne présente plus cette vérification comme un feu vert général.

Un diagnostic séparé compte les couples de machines de production dont le dégagement est inférieur à 4 m par défaut. Il avertit aussi sur les anciens plans collés sans les rendre illisibles ni déplacer leur contenu automatiquement.

## Nouvelle proposition de placement

Huit combinaisons d’orientations sont essayées pour les fonderies, constructeurs et assembleuses. Un placement par rectangles réserve :

- 4 m minimum entre machines de production (réglable entre 4 et 8 m) ;
- 2 m de marge sur les bords du secteur de production, comme réservation pour les virages ;
- une bande de logistique à gauche : gaine verticale de 2 m et emplacements pour répartiteurs/fusions ;
- les dalles et l’espace vertical entre étages.

Les machines sont posées au-dessus du plancher, dont l’épaisseur entre dans le volume. Le choix retient d’abord peu d’étages de production, puis un encombrement bas. Ce n’est pas une recherche d’optimum global des convoyeurs.

Le cas 10 plaques de fer renforcées/min conserve ses 14 machines et tient sur le plan 4×4 en quatre niveaux Z=0,8,16,24. Avec les enveloppes indicatives actuelles : une dalle de 1 m, machines à Z=1,9,17,25, hauteur d’enveloppe 6 m. Cela ne démontre pas la compatibilité avec les meshes, hauteurs et ports du jeu.

## Sols configurables

Structure et implantation propose : largeur des couloirs, pas vertical de 8/10/12/16 m, épaisseur de dalle de 0,5 à 2 m, matériau visuel béton/métal/asphalte et couleur.

« Optimiser sur plusieurs étages » recalcule le placement et son réseau. Un plan existant est remplacé après le dialogue habituel, avec annulation possible dans la session. « Appliquer l’aspect des sols » ne modifie que le matériau et la couleur.

Les dalles couvrent le niveau sauf la bande de gaine verticale ; un objet qui traverse une dalle est refusé. Une épaisseur/pas incompatible est refusée avant de remplacer le plan. Il n’y a pas encore de plancher en tuiles éditables individuellement, d’escaliers ou de calcul de structure.

## Réseau proposé : frontière de preuve

Le réseau déduit les flux par recette, regroupe les producteurs avec des fusions, répartit vers les consommateurs avec des répartiteurs et réserve des gaines pour les ressources qui changent d’étage. Les jonctions ont au maximum trois branches et leur bilan de débit est vérifié. Le cas de référence produit 22 objets de logistique supplémentaires, dont 5 gaines, et 41 liaisons logiques.

Les ports Entrée/Sortie sont des bornes de frontière, pas des coffres miniatures. Les objets de logistique ont des enveloppes conventionnelles de dessin.

Les traits pointillés optionnels sont des liens de réseau, pas des convoyeurs physiques. Les gaines sont des réservations de volume, pas une pile d’élévateurs raccordés générée. Le réseau n’est pas routé physiquement : coordonnées des ports, courbures, rayons de virage réels, capacité des bandes, collisions entre convoyeurs, croisements en hauteur et traversées de plancher avec raccords ne sont pas validés. Les 2 m annoncés sont une réserve de dégagement, pas un rayon de courbure testé.

Le bandeau affiche donc le nombre de liaisons à router. L’outil ne qualifie pas ce réseau de blueprint constructible ou d’usine à efficacité mesurée.

## Thèmes

Le sélecteur en haut à droite fournit Vert (conservé), Orange FICSIT, Dark et Light. Le choix est conservé dans ce navigateur et partagé par l’explorateur, le calculateur et l’atelier. Les sols conservent leur couleur propre, indépendamment du thème.

## Validation

Tests : référence 4×4 sur quatre dalles ; absence de collision ; dégagements de 4 m ; marges et bande logistique ; jonctions équilibrées à trois branches maximum ; références de gaines ; collisions avec les sols ; structure personnalisée ; refus d’une hauteur libre insuffisante ; sauvegarde des nouveaux champs ; suppression d’une gaine sans référence pendante ; alerte sur un ancien plan collé. Les suites atelier, formats, sélection, assistance et calculateur passent.

Navigateur : ancien plan signalé avec passages insuffisants ; bouton de sélection absent ; calculateur configuré en 4×4 puis proposition ouverte dans l’atelier avec 36 objets, quatre niveaux et 41 liaisons à router ; thèmes Light/Dark/Orange contrôlés, passage entre pages ; changement du sol en métal et affichage du réseau au dernier étage.

## Suite indispensable

Pour prouver la viabilité : ports géométriques par machine, routage des convoyeurs dans les couloirs, virages explicites, allocation des hauteurs de passage, segments d’élévateurs et trous raccordés aux planchers, puis diagnostic des liaisons qui ne passent pas. Commencer sur une fonderie, un constructeur et une branche, avant de certifier la chaîne de plaques renforcées entière.
