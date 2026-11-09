# Onglet Calculateur et import par lien

La navigation commune comporte désormais Explorateur, Calculateur et Atelier. /calculateur est une page locale dédiée, avec choix du produit, débit, format du blueprint et tableau des besoins/machines. Le champ JSON de la palette Atelier est masqué ; un bouton mène au calculateur.

L’utilisateur colle une URL entière Satisfactory Calculator. Les objectifs encodés dans /index/json/ sont décodés localement : aucun fichier JSON à obtenir et aucun chargement du site distant nécessaire. Le lien fourni pour Desc_IronPlateReinforced_C = 10 est pris en charge. Le bouton externe ouvre Satisfactory Calculator avec les mêmes objectifs.

Le catalogue comporte neuf recettes standard, dont les plaques renforcées et leurs prérequis fer/vis. Le calcul local donne 120 minerais de fer/min pour 10 plaques renforcées/min : 4 fonderies, 3 constructeurs de plaques, 3 de vis, 2 de barres et 2 assembleuses, toutes à 100 %. Les cadences sont affichées par machine, pas sous forme de pourcentages cumulés.

Le calcul est conservé dans ce navigateur. « Ouvrir dans l’atelier » transmet un nouveau projet local contenant format, recettes, cadences, machines et objectifs. Le brouillon existant est protégé par le dialogue habituel s’il contient des modifications non enregistrées ; les projets enregistrés restent dans la bibliothèque. Les convoyeurs et l’alimentation ne sont pas générés par cette transition.

Le résultat reprend les objectifs du lien et les recalcule avec nos recettes standard. Il ne récupère pas le graphe ou les choix internes complets du site ; les recettes alternatives et produits non pris en charge restent refusés. Aucun export natif ni validation en jeu n’est ajouté.

Validation : test automatisé sur le lien exact fourni, besoins et nombre de machines, absence de collision et transmission JSON. Tests existants atelier, formats et assistance réussis. Dans le navigateur : import du lien, affichage des 14 machines, passage à l’atelier et sauvegarde du nouveau projet, retour au calculateur, modification à 20/min donnant 240 minerais/min puis retour à 10/min. Aucune erreur console observée.
