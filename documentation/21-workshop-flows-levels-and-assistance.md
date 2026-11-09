# Atelier : navigation, objectifs, étages et liaisons

État du 19 octobre 2026. Outil externe local, création sur plan uniquement.

## Utilisation

La même barre de navigation est utilisée dans l’explorateur et l’atelier : marque, deux destinations et indication du mode local. L’action d’ouverture d’une sauvegarde reste disponible dans l’explorateur.

Dans l’atelier :

1. Renseigner les entrées disponibles et les sorties souhaitées, en objets/minute, ou coller les objectifs d’un calculateur.
2. Choisir « Placer les machines des objectifs » pour proposer des machines et leur cadence. Les objets existants sont remplacés après confirmation ; l’annulation reste possible dans cette session.
3. Ajuster les positions et orientations. Shift ou R tourne de 90°, sauf pendant la saisie dans un champ. Les propriétés permettent aussi de choisir la recette et la cadence de chaque machine.
4. Ouvrir « Liaisons assistées », choisir deux machines, puis proposer un convoyeur avec repères de supports. Une autre action propose les poteaux électriques et les câbles.
5. Enregistrer ou exporter le projet JSON. Les anciens projets version 1 sont convertis en version 2 à la lecture ; la bibliothèque existante est conservée.

## Calculateur : contrat limité et explicite

Première prise en charge : huit recettes standard du catalogue local du jeu, build 513885 : lingots de cuivre/fer, fil électrique, câble, tôle de cuivre, plaques/barres de fer et vis. Aucun téléchargement ni dépendance supplémentaire.

Le lecteur expérimental accepte un lien de partage Satisfactory Calculator contenant `/index/json/` ou son objet JSON :

```json
{"Desc_Cable_C":"30","input":{"Desc_OreCopper_C":"30"}}
```

Ce sont les **objectifs** qui sont repris. Le layout et le graphe du site ne sont pas importés. Les machines sont recalculées localement avec les recettes standard. Les paramètres de transport/extraction du lien sont ignorés et annoncés dans l’interface. Les recettes alternatives et les options inconnues sont refusées ; une liste vide de recettes alternatives est acceptée.

Les tests prouvent la lecture du contrat JSON et d’un lien construit avec ce contrat. Ils ne prouvent pas la compatibilité avec toutes les variantes de liens actuellement produites par le site.

Le placement dispose les machines sur une grille avec espaces réservés, puis utilise les étages supérieurs si nécessaire. Il n’optimise pas les trajets, l’énergie ou la compacité. Limite de 100 machines pour cette assistance ; un projet conserve sa limite de 300 objets.

Les débits affichés sont des objectifs et des besoins théoriques de recettes. Ils ne constituent pas une mesure de capacité du plan, ni une simulation des machines et convoyeurs réellement raccordés. Une entrée fournie trop faible est signalée. Sans entrée déclarée, les besoins calculés sont proposés comme entrées lors du placement.

## Hauteur : première base utilisable

Chaque objet possède X/Y, altitude de base Z et hauteur H. Les collisions utilisent une enveloppe rectangulaire en 3D : deux machines peuvent occuper la même surface si leurs intervalles verticaux ne se chevauchent pas. Un contact de faces est autorisé.

La vue de dessus affiche des tranches de 8 m : 0–8, 8–16, etc. Z et H sont éditables librement dans l’inspecteur. La hauteur de travail est limitée à 48 m pour ce prototype ; ce n’est pas une affirmation sur les dimensions autorisées par un Blueprint Designer du jeu. Une machine qui traverse plusieurs tranches apparaît dans chacune.

Les empreintes, hauteurs par défaut et connecteurs restent des conventions de dessin modifiables, pas les collisions ni les coordonnées de ports extraites du jeu. Aucun plancher structurel n’est généré.

## Convoyeurs et poteaux

Le convoyeur est une liaison entre deux objets. Le chemin est recalculé sur une grille de 1 m, en évitant les enveloppes des objets à cette altitude. Les connecteurs sont conventionnels : sortie vers l’avant, entrée vers l’arrière, selon l’orientation. Des repères de supports sont dessinés tous les 8 m environ sur la partie quadrillée du tracé ; ils ne sont pas encore des objets éditables/exportables séparés.

Les deux machines doivent avoir exactement la même altitude. Une liaison verticale est refusée. Lorsqu’un déplacement empêche un ancien trajet, le tracé disparaît et une alerte s’affiche ; il n’est pas conservé comme un convoyeur valide.

L’assistance électrique réutilise ou place des poteaux près des machines de production et propose des câbles entre eux. Les coffres ne sont pas alimentés. Capacités de connexion, portée réelle, obstruction des câbles et alimentation effective ne sont pas validées. Les câbles pointillés sont des propositions.

Les intersections entre convoyeurs, courbures, répartiteurs/fusions, limites de débit, ports compatibles et règles de construction réelles ne sont pas encore contrôlés. Le résultat n’est pas un blueprint natif du jeu.

## Vérification effectuée

- Tests de modèle : cadre, rotation, chevauchements, duplication, import malformé.
- Tests d’assistance : collisions Z, obstacle bloquant, refus entre étages, réutilisation des poteaux, migration v1, conservation des nouveaux champs, import d’objectifs, génération sur plusieurs étages et limites de taille.
- Cas cuivre : 30 minerai/min → 30 câbles/min donne une fonderie, deux constructeurs de fil et un constructeur de câble, selon les recettes du catalogue local.
- Navigateur : ancien projet restauré ; import et placement des quatre machines ; convoyeur avec repères ; deux poteaux et câbles ; rotation Shift ; déplacement à Z=8 et changement d’étage ; avertissement de liaison interrompue ; sauvegarde puis rechargement des recettes, débits et liaisons ; navigation dans les deux sens. Aucune erreur console observée.
- Tests existants des métriques, coffres, zones, aperçu et fondation de l’explorateur réussis. Le test Python a été exécuté depuis l’installation Desktop avec son parseur fourni ; le staging ne contient pas ce dossier vendor.

## Prochaines petites étapes

1. Ports explicites et compatibles, avec flèches et débit attribué par liaison ; un premier cas fonderie → constructeur → coffre.
2. Répartiteur/fusion explicite pour une branche, puis capacité des convoyeurs et bilan de chaque machine.
3. Supports comme objets éditables, courbures et contrôles géométriques plus fins.
4. Élévateur : deux altitudes, emprise réservée sur les étages traversés et validation du raccordement aux convoyeurs.
5. Vue en volume synchronisée avec la sélection de l’étage, puis planchers et dégagements de maintenance.
