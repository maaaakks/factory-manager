# Construction : interfaces, recettes, trajets et aperçu GPU

19 octobre 2026.

## Utilisation

- La palette **Machines** remplace « Transformation ». Un clic sur une machine affiche sa recette directement à droite. Shift + clic ou encadrement permet une sélection multiple ; chaque type présent a sa propre ligne de recette, appliquée à toutes les machines de ce type dans la sélection. Position et rotation restent pilotées sur le plan et par R.
- **Entrée** et **Sortie** sont deux outils distincts dans Logistique. Chaque repère a une ressource et un débit indépendants. Plusieurs repères d’une même ressource sont autorisés. La limite reste 300 objets au total, tampon compris ; il n’y a pas de limite à une seule entrée/sortie.
- Un clic sur un repère ouvre son panneau à droite. Une entrée demande un débit disponible ; une sortie permet un débit cible ou **Auto** (champ vide) pour rechercher le maximum atteignable par ses connexions.
- Les autres éléments logistiques n’ont pas de formulaire de propriétés à droite. Ils restent sélectionnables, déplaçables, tournables et supprimables au clavier.
- **Convoyeur · A → B**, en haut de la palette Construction, ou B : cliquer sur le départ, cliquer éventuellement dans le vide pour ajouter des points de passage, puis cliquer sur l’arrivée. Échap/F annule ; Suppr/Retour arrière retire le dernier point pendant le tracé. Le bouton du panneau d’entrée peut préselectionner le départ. Le rang se choisit avant la pose, ou reste en Auto.
- Les points de passage guident le routage sur la grille. Le routeur calcule des segments évitant les enveloppes des bâtiments et conserve les points dans le projet. Il ne garantit pas encore les rayons de courbure constructibles dans le jeu. Les trajets manuels relient des objets sur un même étage ; les trajets verticaux physiques restent fournis par les profils natifs calibrés.
- Pour modifier un tracé qui vient d’être posé, Ctrl+Z le retire ; on peut alors le retracer. L’édition directe des points d’un convoyeur existant et sa suppression individuelle via un panneau dédié restent à ajouter. Les commandes existantes d’effacement des liaisons restent disponibles dans Design / Réseau.

## Contrat de données commun

`flow-core.js` est indépendant de l’interface et du routeur. Il reçoit les bâtiments, recettes, connexions dirigées et capacités. L’explorateur pourra fournir ces mêmes données via un adaptateur ; son ancien diagnostic n’est pas remplacé implicitement par cette mise à jour.

Un repère conserve le type compatible `port`, avec une interface optionnelle :

```json
{"io":{"side":"input","item":"Desc_OreIron_C","rate":120}}
```

`side` vaut `input` ou `output`. `item` et `rate` peuvent être null tant que le repère n’est pas configuré ; une entrée configurée doit avoir un débit connu. Les anciens repères sans `io` restent lisibles. Les champs sont conservés dans les projets, le tampon et la bibliothèque. Ils ne changent pas le numéro de schéma existant.

Une liaison garde `from`, `to`, `kind`, `item` et `capacity`. Ses points facultatifs sont `waypoints:[{"x":30,"y":18}]`, au maximum 32 points dans les limites du plan. Le routage est recalculé après modification du plan ; un trajet bloqué ne compte plus comme transport disponible dans l’analyse.

L’adaptateur de l’atelier contrôle aussi le raccordement des extrémités natives. Le moteur commun accepte un prédicat `linkAvailable` pour que l’explorateur transmette ultérieurement la disponibilité effectivement déduite des ports enregistrés.

## Estimation des flux

L’analyse résout une circulation en régime stationnaire : conservation des ressources dans les jonctions, limites de capacité, budgets des entrées, proportions de chaque recette et limites des sorties. Une machine qui ne reçoit que la moitié d’un ingrédient ne consomme pas pour autant la totalité des autres ingrédients. Un coffre est une frontière : son contenu n’est pas automatiquement retransmis à une deuxième usine.

Le solveur linéaire travaille sur les liaisons existantes. Les objectifs explicites sont normalisés par leur débit ; les sorties Auto sont pondérées par le nombre d’objets acheminés. Ce n’est pas une politique configurable de priorité entre sorties. Une répartition particulière exige un réseau ou des objectifs correspondant à cette intention.

Les résultats distinguent :

- le débit atteignable à chaque sortie et le pourcentage de son objectif ;
- le débit distribué depuis chaque entrée et sa fraction utilisée ;
- la charge d’une liaison par rapport à sa capacité ;
- la présence d’un goulot, sans attribuer à un convoyeur une limitation due uniquement à une machine en amont.

Les interfaces non configurées, ressources ambiguës et trajets interrompus ne créent pas de débit fictif. Le calcul est mis en cache par version du projet, avec un budget de résolution ; un calcul incomplet est signalé comme partiel.

Ce sont des **estimations théoriques**, pas des mesures de production. Alimentation électrique, inventaires, temps de remplissage, règles avancées de splitters et géométrie réelle des raccords ne sont pas simulés.

## Aperçu opaque accéléré

Le chemin courant emploie désormais WebGL : triangles et lignes sont chargés dans des buffers GPU, et le depth buffer masque les surfaces cachées. Pendant rotation et zoom, seules les matrices et le cadrage changent ; la géométrie n’est pas redécoupée en SVG. Les deux projections réutilisent leurs buffers jusqu’à un changement de projet ou de thème. La transparence conserve le rendu SVG existant.

Le moteur SVG avec découpage reste un repli lorsque WebGL n’est pas disponible. Les pertes/restaurations du contexte graphique ne doivent pas recharger le brouillon. Les surfaces sont redimensionnées lors du passage fenêtre 3D / Design et des changements de taille de fenêtre.

Le test Chrome confirme `data-renderer="webgl"` et un compteur de chargement de géométrie inchangé après rotation/zoom. Cela vérifie l’absence de reconstruction pendant ces gestes, sans constituer une mesure de FPS sur tous les ordinateurs.

## Façades et export

La case « Habiller le blueprint » est retirée. **Générer l’habillage** active directement le style choisi ; **Retirer l’habillage** conserve une action explicite pour l’enlever.

« Angles » est renommé **Piliers aux coins** : il s’agit de montants verticaux aux quatre coins de la façade, de 30 cm, 50 cm ou 1 m de largeur. Ce réglage ne désigne pas un angle de rotation de mur.

Les repères entrée/sortie sont des annotations de frontière, pas des bâtiments du jeu. Les liaisons impliquant ces annotations et les trajets manuels à points de passage ne sont pas encore traduits en raccords natifs. Leur export natif est refusé explicitement : il ne faut pas remplacer silencieusement le tracé choisi par un autre. Les profils natifs déjà calibrés conservent leur export et leurs convoyeurs verticaux.

## Vérifications

- Tests du moteur commun : 120/min sur Mk.1 → 60/min, soit 50 % de l’objectif ; conservation des proportions de recettes avec plusieurs ingrédients ; plusieurs entrées du même item ; trajet bloqué ; ressource incompatible ; profil calibré 120 minerais → 10 plaques renforcées ; persistance des interfaces et points ; changement de recette collectif atomique.
- Suite Node existante réussie après les modifications du modèle et du routeur.
- Quatre variantes natives existantes créées, sérialisées et relues dans le dossier de travail, sans écriture dans les blueprints du jeu.
- Chrome, instance de test isolée au port 8766 : configuration de deux interfaces, tracé avec point de passage (30,18), diagnostic de sortie à 60/min et 50 %, couleur de goulot, recette appliquée à deux constructeurs, lignes séparées Fonderie / Constructeur dans une sélection mixte. Mode opaque GPU confirmé, avec géométrie chargée une seule fois pendant rotation et zoom.
