# Atelier : calques, réseaux et variations

## Réseaux en 3D

Dans l’atelier, les tracés verts/orange/rouges sont les convoyeurs et indiquent le diagnostic de charge. L’électricité est jaune. Une légende est affichée. Les convoyeurs physiques deviennent des rubans avec largeur et épaisseur, y compris leurs segments verticaux. Les liaisons logiques non routées restent pointillées.

Dans l’explorateur, les convoyeurs sont orange et suivent leurs splines et extrémités d’élévateurs enregistrées. Sur jojo_autosave_2, les 653 convoyeurs ont une géométrie exploitable ; contrôle visuel sur la zone de 55 convoyeurs. Ce sont des formes schématiques, sans modèle ni texture du jeu.

Les calques de l’atelier distinguent machines, logistique/élévateurs, convoyeurs, électricité, sols, murs et toits. Ils fonctionnent dans Construction, Design et la fenêtre 3D. Masquer ne supprime pas et ne modifie pas l’export. La sélection rectangulaire ignore les objets masqués ; les préférences d’affichage restent locales au navigateur.

## Variations d’implantation depuis Design

Dans Sols, Espacement et aération propose Compact, Équilibré, Aéré, hauteur entre étages et répartition automatique, verticale, sur un étage ou limitée. Le recalcul utilise les entrées/sorties du projet ouvert, pas le brouillon du calculateur. Il recrée les machines et les réseaux : les déplacements manuels sont remplacés. Le nom, l’identifiant du projet, le format, le tampon, la palette et l’habillage sont conservés. Le bouton Annuler restaure l’ancien plan.

Les petits cas fer → plaques renforcées en mode compact réutilisent les modules natifs calibrés. Les autres variantes utilisent la recherche générique avec réseau complet. Un échec signifie que cette recherche n’a pas trouvé d’implantation satisfaisant les contraintes ; ce n’est pas une preuve d’impossibilité absolue. Aucun résultat partiel n’est appliqué. Les limites préexistantes de l’export des élévateurs génériques restent applicables.

## Murs et toits

Variation est renommé Motif des murs : le numéro fait varier le rythme des fenêtres. Ajouter une toiture devient Couvrir le dernier étage : ajoute le toit au-dessus des machines.

Rafraîchir les murs modifie uniquement le motif des façades. Rafraîchir le toit utilise un motif indépendant et conserve les murs. Les puits de lumière, panneaux d’accent et teintes varient selon ce motif reproductible, conservé dans le JSON. Les formes proposées sont Terrasse plane, Pentes et verrières, ou Procédural. Les verrières montrent une ossature schématique ; elles utilisent les pièces vitrées natives à l’export.

Le mode procédural choisit un toit plat lorsque les pentes ne tiennent pas dans la hauteur disponible. Une pente imposée trop haute est refusée sans modification. Les pentes actuelles sont des modules de 8 m avec 2 m de dénivelé et leurs pignons. L’emprise générale des façades reste rectangulaire ; il n’y a pas encore de découpe du volume complet suivant l’occupation de chaque étage.

La réservation automatique d’une grande entrée de façade est retirée. Des panneaux peuvent encore être omis si un bâtiment ou un élévateur occupe leur volume ; le nombre est affiché. Ce sont des passages préservés, et non une raison de masquer arbitrairement une face entière. Les murs restent composés de modules natifs de 8 m ; les petits raccords autour d’un élévateur ne sont pas encore découpés sur mesure.

## Mes projets

Les cartes et le sélecteur affichent Input et Output avec les ressources et débits. Chaque carte permet de supprimer un projet de la bibliothèque du navigateur. Restaurer le dernier projet supprimé annule cette opération. Le brouillon actuellement ouvert et les blueprints déjà exportés dans le jeu ne sont pas supprimés.

## Validation

23 suites JavaScript : géométrie des rubans horizontaux/verticaux, chemins dégénérés, motifs indépendants, formats et limites de hauteur, plus régressions existantes. Python : douze comparaisons exactes entre enveloppe JavaScript et export Python, classes/recettes présentes, export et relecture de toits plats/inclinés, régressions export générique et modules compacts.

Les classes de toiture inclinée sont déclarées dans les Docs locales du jeu ; les chemins reprennent la convention des pièces plates déjà observées. Ces nouveaux assemblages sont validés en binaire local, pas par un nouvel essai en jeu. Aucun fichier du dossier Blueprint du jeu n’a été écrit pendant ces vérifications.

Contrôles Chrome sur instance de test isolée : filtres Construction/Design/3D, réseau de l’explorateur, refus d’un étage unique pour 120 minerais → 10 plaques en 4×4, succès d’une variante compacte en 6×6 avec hauteur 12 m, rafraîchissement indépendant des murs/toit, suppression puis restauration d’un projet de test.
