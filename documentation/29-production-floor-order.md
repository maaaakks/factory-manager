# Étages suivant la chaîne de production

19 octobre 2026.

Le placement assisté traite les recettes dans l’ordre de leurs dépendances, plutôt que de commencer par les machines les plus grandes. Une machine consommatrice ne peut pas être placée en dessous des machines du plan qui fabriquent ses ingrédients. Des étapes peuvent partager un étage si la place et les dégagements le permettent. Les chaînes indépendantes ne sont pas forcées sur des étages distincts. Les entrées intermédiaires fournies de l’extérieur coupent le développement des recettes comme auparavant.

Exemple vérifié, 10 plaques renforcées/min en 4×4 :

- Sol Z=0 : quatre fonderies de lingots de fer.
- Sol Z=8 : deux productions de barres et deux productions de plaques.
- Sol Z=16 : une production de plaques et trois productions de vis.
- Sol Z=24 : deux assembleuses de plaques renforcées.

Avec les planchers par défaut de 1 m, les machines reposent respectivement à Z=1, 9, 17 et 25. Les couloirs, sols et réservations logistiques restent vérifiés. La génération depuis le calculateur et « Calculer et placer » dans l’atelier utilisent la même règle. Les plans déjà enregistrés gardent leurs coordonnées jusqu’à une nouvelle génération explicite.

Le fond coloré de la zone représente le plancher de l’étage actuellement affiché, avec sa matière et sa couleur. Le vert est sa couleur par défaut, pas un indicateur d’efficacité. On peut modifier la matière et la couleur dans « Sols et espacement » puis « Appliquer l’aspect des sols ». Les cadres pointillés autour des machines sont les dégagements réservés. Les lignes pointillées entre objets sont les liaisons logiques proposées, encore non routées.

Validation : tests de placement ascendant pour fer, cuivre sur les trois formats et lingots fournis en entrée ; contrôles existants d’enveloppes, dégagements, niveaux, formats et assistance réussis.
