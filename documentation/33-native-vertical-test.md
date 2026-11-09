# Test natif 03 : transport vertical entre deux étages

19 octobre 2026.

Le test 02 est déclaré fonctionnel par l’utilisateur. Le test 03 garde les mêmes recettes et débits pour isoler l’ajout du transport vertical. Fichiers `FT_TEST_03_PlaquesEtages.sbp` et `.sbpcfg`, écrits directement dans `SaveGames/blueprints/SANDBOX`. Les tests 01 et 02 restent présents.

## Contenu et essai

- Fonderie de lingots de fer au rez-de-chaussée.
- Constructeur de plaques de fer sur un plancher situé 12 m plus haut.
- Deux convoyeurs Mk.1 et un élévateur Mk.1 montant de 12 m.
- Douze fondations de 1 m : huit en bas, quatre en haut.
- Deux poteaux Mk.1 et trois câbles : bas vers fonderie, bas vers poteau haut, haut vers constructeur.

Recharger SANDBOX puis chercher `FT_TEST_03_PlaquesEtages`. Après placement, raccorder le poteau du bas au réseau et alimenter la fonderie en minerai. Vérifier le passage des lingots sur le convoyeur inférieur, leur montée, puis leur arrivée au constructeur. Les plaques s’accumulent dans le constructeur à l’étage.

Résultat théorique inchangé : 30 minerais de fer/min → 20 plaques/min, 8 MW en fonctionnement. Les deux machines sont à 100 %. Il n’y a pas de coffre ni de convoyeur externe d’alimentation ou de sortie.

## Géométrie native

La surface du sol inférieur est à Z=100 cm, celle du plancher supérieur à Z=1300 cm. La fonderie repose à Z=100 ; le constructeur à Z=1300 et tourne de 180° pour faire face à l’arrivée du convoyeur supérieur. L’écartement de 12 m est conservateur pour le dégagement au-dessus de la fonderie. Référence des dimensions de la machine : [Smelter, wiki officiel](https://satisfactory.wiki.gg/wiki/Smelter).

L’élévateur monte de Z=200 à Z=1400 cm à la position X=0, Y=1200. Il utilise un gabarit vanilla de 12 m déjà relié à des convoyeurs dans un blueprint local. Les deux extrémités de ce gabarit correspondent à l’origine de l’acteur et à son transform supérieur. Les directions natives d’entrée/sortie, mesurées depuis les tangentes des convoyeurs voisins, sont prises en compte ; l’acteur tourne de -90° pour recevoir le flux par +Y en bas et le renvoyer par -Y en haut.

Le plancher supérieur occupe X/Y=-800 à +800 cm. La gaine se situe en bordure, hors de ce plancher. **Il s’agit d’une gaine ouverte, sans objet de traversée de sol ni fondation traversée par le lift.** Cela isole le test de l’élévateur ; les traversées de plancher natives viendront séparément. Le câble reliant les deux poteaux passe également hors du bord du plancher pendant son changement de niveau.

Le module entre dans le volume d’un designer 4×4. L’export utilise les mêmes versions de sérialisation que les gabarits natifs déjà testés. Les câbles et convoyeurs sont régénérés avec leurs nouvelles références et coordonnées, sans connexion vers un blueprint d’origine.

## Validation locale

Les helpers `native_assembly.py` assemblent les acteurs, composants, ports, segments droits et câbles. Ils sont utilisés par ce module fixe, sans prétendre exporter automatiquement tous les plans de l’atelier.

`tests/check_native_vertical.py` contrôle les 22 acteurs et 24 composants, la relecture du fichier natif, les deux niveaux, la hauteur et le sens du lift, les raccords réciproques, les ports et géométries, les bornes électriques, les dégagements de la gaine et les câbles vis-à-vis des dalles. Les cas négatifs changent la hauteur du lift, bouchent la gaine ou inversent une machine/un élévateur : ils sont refusés. Les tests natifs 01/02 et le serveur restent réussis.

Le module a été enregistré depuis Chrome puis relu depuis le dossier SANDBOX. `33-native-test03-receipt.json` conserve les tailles et empreintes réelles. La validation en jeu du test 03 reste à faire par l’utilisateur ; le retour favorable du test 02 ne valide pas automatiquement le transport vertical.
