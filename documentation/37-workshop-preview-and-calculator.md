# Atelier : vue 3D et Calculator intégré

## Utilisation

- **Vue 3D**, au-dessus du plan, ouvre une perspective et une **vue en élévation**. Le sélecteur Face / Côté change uniquement l’axe d’observation. Tous les étages sont visibles ; le tampon est exclu.
- L’aperçu est en lecture seule. Les gestes et raccourcis de modification du plan sont bloqués pendant son ouverture. Fermer ou Échap revient au plan.
- Le menu **Calculator**, à côté d’Importer / Exporter, remplace Entrées → sorties et l’ancien onglet séparé. `/calculateur` redirige vers `/atelier?calculator=1`, avec le menu ouvert.
- Le champ **Ressource** est un seul sélecteur avec recherche intégrée, sans liste séparée. Flèches et Entrée permettent de choisir au clavier ; Échap referme les résultats.
- Choisir Entrée disponible ou Sortie souhaitée, sélectionner une ressource et saisir un débit, ou le laisser vide, puis Ajouter / modifier. Les lignes existantes se modifient avec **Modifier**.
- Les débits se recalculent immédiatement dans le résumé. **Calculer et placer** reste une action explicite qui remplace les objets après confirmation et permet Ctrl+Z. L’import de lien de partage / JSON Satisfactory Calculator est conservé dans le menu.

## Règles Auto

Le modèle conserve `rate: null` pour un débit automatique dans le brouillon, les projets et leurs exports JSON. Un résultat calculé ne remplace pas ce choix par un nombre figé.

| Objectifs | Résultat |
| --- | --- |
| 10 plaques renforcées/min, entrée fer Auto ou non renseignée | Besoin de 120 minerais de fer/min |
| 120 minerais de fer/min, plaques renforcées Auto | 10 plaques renforcées/min |
| 150 minerais de fer/min, 10 plaques renforcées/min | 120 consommés, 30 restants |
| 60 minerais de fer/min, 10 plaques renforcées/min | Erreur explicite : budget insuffisant |
| Tous les débits vides | Demande d’un débit d’entrée pour déterminer la sortie |

Les sorties chiffrées sont satisfaites d’abord. Les sorties Auto utilisent les entrées restantes. Plusieurs sorties Auto reçoivent le même débit par minute, limité par le premier budget d’entrée épuisé : c’est une règle de répartition explicite, pas un optimum économique unique. Une entrée sans débit n’impose pas de plafond. Les ressources d’entrée intermédiaires arrêtent la décomposition des recettes à cette ressource. Les autres besoins sont calculés et affichés, sans supposer un débit de miner mesuré.

Les recettes restent les recettes standard du catalogue local. Une ressource ne peut pas être simultanément entrée et sortie cible. Débits nuls, négatifs, non finis ou supérieurs à 100 000/min refusés.

## Aperçu et limites

L’aperçu utilise les positions, rotations, hauteurs et volumes du projet, avec ses sols, ses couleurs personnalisées et ses connexions. Il n’utilise pas les modèles visuels du jeu. Les gaines réservées et les liaisons logiques restent en pointillés ; leur affichage ne valide pas un trajet physique exportable. Les convoyeurs déjà proposés sur un même étage réutilisent les trajets schématiques du plan, mis en cache. Les volumes et les hauteurs restent ceux de l’atelier.

Le calcul des débits est séparé du placement : aucun solveur d’implantation n’est appelé pendant la saisie, le rendu ou l’ouverture de l’aperçu.

## Vérification du 19 octobre 2026

- `node tests/check_calculator_auto.cjs` : calcul inverse et direct, budgets restants, priorité aux sorties fixées, répartition Auto, erreurs, persistance, absence de mutation et génération des 14 machines pour les plaques renforcées.
- Contrôles existants : modèle Atelier, calculateur SCIM, assistance, implantation multiétage et patterns compacts réussis.
- Chrome, session de secours séparée : saisie par sélecteur de 120 minerais → plaques renforcées Auto ; résultat 10/min ; génération ; restauration après rechargement avec Auto conservé.
- Aperçu sur ce plan : 34 objets + 2 sols dans chaque projection ; Face / Côté ; R et Suppr avec une machine sélectionnée ; contenu du plan identique avant/après. Aucune erreur console observée.
- Aucun export vers le jeu ni remplacement du brouillon habituel pendant ces vérifications.
