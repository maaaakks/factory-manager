# Test natif 04 : plaques renforcées, 4×4 et trois étages

19 octobre 2026.

L’utilisateur confirme le bon fonctionnement du test 03 en jeu. Le transport vertical de ce test est donc validé par son essai. Le test 04 ajoute une usine complète ; son fonctionnement en jeu reste à confirmer séparément.

## Résultat à essayer

`FT_TEST_04_PlaquesRenforcees.sbp` et `.sbpcfg`, dans le dossier de blueprints **SANDBOX**. Le menu Importer / Exporter de l’atelier propose le module 04 et permet de le réenregistrer. Les autres tests sont conservés. Ce module natif fixe est indépendant du brouillon ouvert dans l’atelier ; il ne constitue pas encore un exporteur natif de n’importe quel plan.

- Entrée unique : **120 minerais de fer/min**.
- Sortie : **10 plaques de fer renforcées/min**, convoyées dans un coffre Mk.1 vide.
- Puissance nominale de production : **78 MW**.
- Recettes standard, horloges à 100 %, sans éclats ni amplificateurs.
- Emprise **32×32 m**, soit 4×4 fondations. Dimension native du concepteur : 4.
- Trois sols complets, 48 fondations **béton de 1 m**.
- Machines et coffre personnalisés en noir : couleurs primaire et secondaire natives, sans modifier un nuancier partagé de la session.
- 47 convoyeurs Mk.2, 12 segments d’élévateurs Mk.2, six traversées de sol natives.
- Sept poteaux Mk.1, vingt câbles ; chaque machine est reliée au même réseau et chaque poteau respecte sa limite de quatre raccords.

## Hauteurs et implantation

L’utilisateur a choisi « hauteur minimale sans chevauchement » après clarification des 6 m. Les surfaces des sols sont à **1 / 10,5 / 20 m** : **9,5 m entre sols**, dont 1 m de dalle et 8,5 m libres. Le volume supérieur des assembleurs atteint 30,75 m, dans la limite de 32 m.

Ces dimensions utilisent les `mClearanceData` du jeu installé, dans `D:\steam\steamapps\common\Satisfactory\CommunityResources\Docs\en-US.json`, build 513885. La fonderie atteint 8,5 m ; le constructeur atteint 8,5 m en incluant sa tige de dégagement souple ; l’assembleur atteint 10,75 m avec son antenne. Les valeurs souples sont conservées pour éviter de couper les appendices avec un plancher.

| Niveau | Contenu | Flux |
| --- | --- | --- |
| RDC, 1 m | 4 fonderies + 2 constructeurs de tiges | 120 minerais → 120 lingots ; 30 lingots → 30 tiges |
| Étage 1, 10,5 m | 3 constructeurs de plaques + 3 de vis | 90 lingots → 60 plaques ; 30 tiges → 120 vis |
| Étage 2, 20 m | 2 assembleurs + coffre | 60 plaques + 120 vis → 10 plaques renforcées |

Les machines sont tournées vers leurs couloirs de distribution et collecte. Les montées de lingots utilisent le bord gauche, celle des tiges le bord droit. Deux montées centrales alimentent les assembleurs. Les deux répartiteurs des assembleurs occupent le couloir central et sont décalés en hauteur pour séparer les matières. Les virages à 90° utilisent des splines natives de rayon nominal 2 m ; les montées de bande sont bornées à 35°.

## Traversées réelles

Chaque passage comprend une fondation pleine en béton, un acteur `Build_FoundationPassthrough_Lift`, un segment d’élévateur inférieur et un segment supérieur. Les segments se connectent réciproquement au centre de la traversée ; `mSnappedPassthroughs`, `mBottomSnappedConnection`, `mTopSnappedConnection`, l’épaisseur de dalle et les modes de masquage des têtes suivent la structure relevée dans un blueprint local natif. Ce n’est pas un long élévateur simplement dessiné à travers une dalle.

Gabarits supplémentaires : répartiteur, fusionneur, fondation béton, coffre, constructeurs de tiges/vis et assembleur configuré, extraits des blueprints locaux. Les connexions précédentes et les inventaires sont retirés ; tous les acteurs et références sont réassemblés. Le parseur GPL-3.0 GreyHak déjà fourni est conservé.

## Procédure de test

1. Recharger SANDBOX pour actualiser le catalogue, puis sélectionner **FT_TEST_04_PlaquesRenforcees** et placer le blueprint.
2. Alimenter le **répartiteur central du RDC**, par son entrée du côté sud (Y négatif, face avant des trois répartiteurs alignés). Un convoyeur Mk.2 minimum est nécessaire pour apporter 120/min. Les quatre fonderies sont déjà raccordées à sa distribution.
3. Relier au réseau un poteau libre du RDC. Le premier poteau possède un raccord disponible ; le réseau intérieur dessert les quatorze machines.
4. Laisser les convoyeurs et inventaires des manifolds se remplir avant d’évaluer le régime permanent. Le démarrage ne donne pas immédiatement 100 % partout.
5. Vérifier la progression vers le coffre au dernier étage : 10 plaques/min en régime établi. Garder de la place dans le coffre pendant la mesure ; un coffre plein bloque normalement la production.

Points particulièrement utiles à observer en jeu : circulation à travers les six passages de sol, alimentation des deux recettes d’assembleur, absence de problème visuel aux virages courts et aux connexions de proximité, puis débit stable au coffre. Aucun essai de placement ni de production en jeu n’est effectué par les tests Python.

## Vérifications automatiques

`tests/check_native_factory.py` couvre l’écriture/relecture binaire du couple natif, 174 acteurs et 340 composants, les références internes, la réciprocité des raccords, la coïncidence des extrémités, les directions d’entrée/sortie des convoyeurs, le chemin de chaque recette jusqu’à son étape suivante puis au coffre, les entrées machines branchées, les traversées réciproques, le réseau électrique et les limites de poteaux, les couleurs noires, les volumes de machines et le dégagement sous les sols. Il injecte aussi des erreurs de recette, géométrie, orientation, traversée et couleur pour vérifier leur rejet.

Le bilan matière est recalculé séparément à partir du catalogue installé : seuls **−120 minerais et +10 plaques renforcées/min** restent après annulation des intermédiaires. Tous les convoyeurs et élévateurs sont Mk.2 : les lignes communes de minerais et vis peuvent donc transporter 120/min.

Ces contrôles vérifient la structure et les contraintes modélisées. Ils ne remplacent pas le test du moteur de jeu, notamment pour les maillages des accessoires et la circulation réelle. Le reçu `34-native-test04-receipt.json` garde `inGameValidated: false` jusqu’à un retour utilisateur sur ce nouveau module.

Les tests 01, 02 et 03 passent également après intégration. Les sauvegardes `.sav` et les blueprints personnels restent intacts ; seuls les fichiers dédiés à ce test sont créés ou remplacés, avec sauvegarde d’un éventuel exemplaire précédent.
