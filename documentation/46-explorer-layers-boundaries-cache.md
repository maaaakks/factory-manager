# Exploration : calques, sorties et cache

Le panneau gauche présente la sauvegarde, les calques puis les usines enregistrées. Les listes de propositions et la vue d’ensemble sont retirées ; les propositions restent cliquables sur la carte lorsque le zoom le permet. L’inspection est fermée sans sélection et peut être fermée explicitement.

Le volume schématique présente des calques indépendants par catégorie et une perspective avec recentrage. Les commandes Face, Côté, Masquer les toitures et Adapter son style dans l’atelier sont retirées. Le bouton Libérer la zone est retiré.

## Sorties physiques

Les entrées et sorties sont empilées avec leurs icônes de ressource. Une sortie peut terminer dans le premier coffre ou franchir le périmètre par une connexion dirigée vers l’extérieur. La capacité du premier convoyeur extérieur est prise en compte. Un convoyeur ouvert peut constituer une sortie si son extrémité aval, déduite de la connexion amont, dépasse la limite. Un convoyeur ouvert à l’intérieur ne suffit pas.

Le calcul conserve la priorité des besoins internes et les capacités partagées. Il estime ce qui est acheminable depuis la sauvegarde ; il ne mesure pas le débit instantané du jeu. Un périmètre proposé doit encore être confirmé. Sur la zone de référence à douze machines : 120 minerais de fer/min requis et 10 plaques renforcées/min acheminables par une sortie du périmètre.

## Géométrie des toits

Les pentes utilisent l’axe local X descendant et un pivot centré, puis la rotation native complète. La comparaison des extrémités de toits avec les murs triangulaires de jojo_autosave_2 fournit huit alignements exacts pour cette convention. La visualisation reste schématique : les variantes de coins sont simplifiées et toutes les familles architecturales ne sont pas validées individuellement.

## Conservation et cache

IndexedDB conserve le dernier monde analysé et ses zones. La session conserve cadrage, calques, sélection, périmètre, nom non enregistré et état du panneau. Un aller-retour Atelier → Explorateur restaure ces éléments sans nouvel appel d’analyse si la sauvegarde et le parseur n’ont pas changé.

Le serveur conserve aussi les analyses JSON compressées dans external-tool/data/save-cache : cinq instantanés maximum, 150 Mo compressés maximum. Les clés incluent chemin, taille, date et version du parseur/catalogue. Les fichiers importés sont identifiés par leur contenu. Une modification invalide le cache ; un cache corrompu est recalculé. Aucun fichier de sauvegarde du jeu n’est modifié. Le premier chargement initialise le cache.

## Validation locale

22 suites JavaScript passent, avec cas de sortie de périmètre, coffre terminal, capacité extérieure, convoyeur ouvert dirigé et alignement toiture. Les tests Python valident le cache, ses invalidations, la récupération après corruption et son éviction. Vérification Chrome : restauration de 7 888 bâtiments, calques, usine et caméra après navigation, sans POST /api/load supplémentaire ; contrôle visuel des toitures et des panneaux. Pas de nouvelle validation en jeu nécessaire pour cette lecture seule.
