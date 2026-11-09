# Réseau automatique : Entrée → machines → Sortie

19 octobre 2026.

Le bouton **Relier entrée → sortie** utilise désormais les repères et les ressources demandées pour reconstruire toute la chaîne de transformation. Les anciens sélecteurs départ/arrivée sont supprimés. Le même bouton est accessible dans le panneau d’une Entrée ou d’une Sortie.

## Comportement

1. Définir la ressource et le débit disponible des Entrées, puis la ressource et éventuellement le débit cible des Sorties.
2. Poser les machines nécessaires. Une recette déjà choisie est respectée. Si elle manque, le réseau choisit la recette lorsqu’une seule possibilité existe dans le catalogue pris en charge.
3. Cliquer **Relier entrée → sortie**. Exemple : Minerai de fer → Fonderie → Constructeur de plaques → Sortie Plaques de fer. Aucun tronçon minerai → plaques ne peut remplacer ces transformations.
4. Le réseau estime les débits avec le moteur de conservation des ressources. Le mode Auto choisit le rang de convoyeur minimal permettant le débit atteignable. Un rang fixe reste possible.

Les machines parallèles sont raccordées par des répartiteurs et des fusions générés, placés sur des emplacements libres avec accès aux ports schématiques. Plusieurs Entrées et Sorties sont prises en compte. Les machines sans rapport avec les ressources demandées restent hors chaîne et leur nombre est indiqué ; elles ne sont pas branchées artificiellement dans une transformation incompatible.

Une étape absente, une recette incompatible, un passage bloqué ou un changement d’étage sans raccord calibré produit une erreur. Le projet reste intact : génération, recettes et liaisons sont appliquées ensemble, avec annulation Ctrl+Z. La reconstruction remplace les liaisons de transport existantes et les jonctions qu’elle avait générées, en conservant l’électricité et les objets manuels. Elle ne modifie pas les modules natifs compacts déjà calibrés.

Le panneau Construction mesure 240 px sur grand écran. La section **Convoyeurs**, avec son icône, précède **Construire** et la palette de machines. Le tracé manuel « Tronçon · B » et son raccourci ont été retirés. Les trajets manuels déjà sauvegardés restent lisibles dans les projets.

**Retirer les convoyeurs** supprime les liaisons de transport et les élévateurs, en conservant les machines, les répartiteurs/fusions et l’électricité. Le bouton est désactivé en l’absence de transport ; Ctrl+Z restaure l’ensemble. Vérifié sur le module compact natif également, où garder un élévateur sans ses liaisons pouvait invalider les contrôles de dégagement.

Le raccord automatique reste un plan schématique : les limites d’export des repères et trajets manuels documentées dans la partie Construction restent applicables. Il n’ajoute pas silencieusement d’élévateur ni de nouvelle machine.

## Architecture et contrôles

`workshop-network.js` est indépendant de l’interface et utilise `WorkshopModel`, le routeur de l’atelier et `FactoryFlowCore`. Il remonte depuis les ressources de sortie, identifie les fournisseurs compatibles, puis route les groupes de ressources. Les erreurs ne déclenchent pas de raccord direct de secours. Les recherches de placement et de chemin ont un budget de calcul pour éviter un blocage prolongé du navigateur.

Tests ajoutés : fonderie seule (30 lingots/min), fonderie + constructeur (20 plaques/min et objectif à 100 %), recettes automatiques, conservation des recettes choisies, absence de contournement, étapes manquantes, chemins bloqués, changement d’étage, deux fonderies avec répartiteur/fusion, plusieurs sorties, génération répétée sans doublons et protection du réseau natif calibré. Les 19 suites JavaScript passent.

Vérification Chrome : import d’un projet à quatre objets sans recettes, génération en un clic de trois convoyeurs, sélection du constructeur confirmant sa recette Plaque de fer et sortie estimée à 20/min. Ces contrôles portent sur l’atelier et ses estimations, sans test de ce réseau en jeu.
