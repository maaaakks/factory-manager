# Calcul par entrées, tampon sur grille et capacités

19 octobre 2026 — suite de la tranche 26.

## Calculateur

Le format du blueprint précède les objectifs. Le menu « Calculer à partir de » propose trois modes :

- **Sorties souhaitées** : calculer les besoins pour les débits demandés.
- **Entrées disponibles → sortie maximale** : saisir les ressources et leurs disponibilités, puis choisir au moins une sortie. Une seule sortie est maximisée directement ; plusieurs sorties conservent les proportions saisies en parts.
- **Entrées + objectifs de sortie** : respecter les plafonds de sortie ; si une entrée manque, réduire toutes les sorties dans la même proportion. Un surplus d’entrée ne force pas une surproduction.

Le calcul développe les recettes standard jusqu’aux ressources fournies ou aux minerais. Il prend le plus petit rapport disponibilité/besoin comme facteur commun. Chaque ressource nécessaire doit avoir un budget explicite en mode entrée ; aucune ressource absente n’est supposée illimitée. Les doublons, entrées sans usage et une même ressource demandée en entrée et sortie sont refusés. Les proportions sont un choix utilisateur : ce prototype ne cherche pas automatiquement une répartition économique entre produits.

Exemples vérifiés : 120 minerais de fer/min donnent au maximum 10 plaques renforcées/min, ou 80 plaques de fer/min. Avec un objectif de 20 plaques renforcées/min et 120 minerais/min, le mode combiné propose 10/min et indique 50 % de l’objectif. Le transfert vers l’atelier utilise les sorties calculées, pas les valeurs initiales des proportions.

Les limites de placement continuent de s’appliquer : l’outil ne réduit pas silencieusement la production maximale pour la faire rentrer dans le format choisi. Si le plan ne tient pas, le calculateur demande un autre format ou objectif. Les recettes alternatives ne sont pas prises en charge.

## Atelier

« Entrées → sorties » est un menu sur la barre d’Importer / Exporter. Il contient le résumé, l’édition des débits, la recherche des ressources et « Calculer et placer ». La recherche ignore les accents et la casse. Il n’y a plus de ligne dédiée au-dessus du plan.

Les actions ordinaires (poser, déplacer, tourner, tampon, enregistrer, annuler) ne créent plus de notification. Les erreurs et la protection des changements non enregistrés restent visibles. Ctrl+Z et les boutons d’historique restent disponibles.

Le tampon est une extension SVG jointive au bord droit, à la même échelle et sur la même grille que le blueprint. Les objets gardent leur forme et orientation. On peut les prendre, les déplacer, les tourner pendant la prise, puis les déposer sur le plan ou dans le tampon. On peut aussi poser directement un objet de la palette dans le tampon. Un dépôt qui dépasse du tampon ou chevauche un objet est refusé sans perte ; un dépôt hors des deux zones supprime l’objet avec annulation possible.

Le tampon conserve les coordonnées de dépose. Les anciens objets stockés sans coordonnées compatibles sont disposés automatiquement dans l’extension à l’affichage, puis leurs coordonnées sont enregistrées à la prochaine dépose. La taille de l’extension s’adapte aux enveloppes des objets et au contenu existant. Le tampon reste hors de la consommation et de la production du blueprint ; le dépôt détache les liaisons.

## Électricité

Le calculateur et l’atelier affichent les MW théoriques des machines de production posées, suivant leur cadence. Le catalogue public contient la puissance nominale et l’exposant de cadence des trois machines prises en charge. Source : documentation locale du jeu `D:/steam/steamapps/common/Satisfactory/CommunityResources/Docs/en-US.json`, classes `Build_SmelterMk1_C`, `Build_ConstructorMk1_C`, `Build_AssemblerMk1_C`, champs `mPowerConsumption` et `mPowerConsumptionExponent`.

Calcul : somme des puissances nominales multipliées par la cadence à la puissance de cet exposant. Ce total exclut les extracteurs externes, les objets du tampon et toute mesure d’alimentation réelle. Il suppose les machines en fonctionnement. La chaîne standard de 10 plaques renforcées/min affiche 78 MW. Les constantes sont incluses dans `dist/planner-data.json` ; toute reconstruction de ce catalogue doit conserver ou réextraire son bloc `power`.

## Convoyeurs

Le panneau Convoyeurs permet de choisir la capacité du réseau : Mk.1 à Mk.6. Les valeurs proviennent du [wiki officiel, Conveyor Belts](https://satisfactory.wiki.gg/wiki/Belts). Les couleurs des liaisons comparent localement le débit prévu et la capacité : vert avec réserve, ambre à partir de 90 % de charge, rouge si la demande dépasse la capacité, gris si le débit est inconnu. Le détail au survol et la liste des goulots indiquent débit demandé, capacité et fraction maximale passant sur ce tronçon.

Pour une liaison manuelle, on peut indiquer le débit prévu. Sinon, il n’est déduit que pour une liaison directe entre machines avec une seule ressource commune et sans branchement ambigu. Les autres liaisons restent grises. Un champ optionnel de capacité par liaison est accepté par le modèle ; l’interface actuelle règle la capacité commune du réseau.

Les liaisons logiques sont affichées par défaut en pointillés, avec leur état de capacité. Elles restent non routées. Les trajets manuels sur un étage sont continus et schématiques. Le panneau et les infobulles précisent cette différence.

**Limite** : il s’agit de plafonds locaux calculés, pas d’une simulation globale de transport. Les déficits ne sont pas propagés dans le réseau, et les stocks, démarrages, répartitions dynamiques, raccords physiques et l’efficacité réelle en jeu ne sont pas simulés. « 50 % du débit passe » signifie capacité/demande sur le tronçon, pas 50 % d’efficacité de toute l’usine.

## Validation

`node tests/check_workshop_capacity.cjs` : maximum par entrée, proportions multiples, besoins manquants, budgets, plafonds combinés, surplus, puissance/cadence, capacité des convoyeurs, débit inconnu, persistance et validation du tampon sur grille, import ancien. Les suites atelier existantes et le calculateur passent également.

Vérifications dans l’interface : 120 fer/min → 10 plaques renforcées/min ; 60 fer/min → 5/min ; objectif 20/min limité à 10/min ; transfert du résultat calculé dans l’atelier ; recherche « renforcee » ; disparition de la ligne dédiée ; aller-retour d’une assembleuse dans le tampon avec total 78 → 63 → 78 MW et aucune notification ordinaire ; changement de capacité révélant quatre goulots locaux dans le projet de référence. Le plan généré de test a été conservé dans un projet distinct avant réouverture de la référence.
