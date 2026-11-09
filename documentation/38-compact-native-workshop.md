# Implantation compacte branchée au calculateur et à l’export

19 octobre 2026. Premier profil : **120 minerais de fer/min → 10 plaques renforcées/min dans un coffre**, en 4×4 (32×32×32 m).

## Problème corrigé

Le placement précédent disposait des machines, puis ajoutait un réseau logique `planned` et des gaines réservées. Il ne réutilisait pas les modules mesurés dans les références kouyère. L’export refusait donc, correctement, des connexions qui n’avaient pas de réalisation physique.

Pour cette chaîne précise, **Calculer et placer** utilise maintenant un assembleur de modules natifs. Il retourne à l’atelier les objets, ports, splines, élévateurs et câbles physiques que l’export reconstruit depuis le projet courant. Les anciennes réservations ne sont pas converties en changeant leur étiquette : il faut recalculer le plan.

## Bilan de production

| Étape | Machines et cadence | Entrée / min | Sortie / min |
| --- | --- | --- | --- |
| Fonte | 4 fonderies à 100 % | 120 minerais | 120 lingots |
| Plaques | 4 constructeurs à 75 % | 90 lingots | 60 plaques |
| Tiges | 2 constructeurs à 100 % | 30 lingots | 30 tiges |
| Vis | 4 constructeurs à 75 % | 30 tiges | 120 vis |
| Assemblage | 2 assembleuses à 100 % | 60 plaques + 120 vis | 10 plaques renforcées → coffre |

La variante contient 16 machines contre 14 pour le calcul strict à cadence nominale. Les deux constructeurs supplémentaires permettent quatre paires régulières à l’étage. La consommation théorique passe de 78 à **75,88 MW**, grâce au sous-cadencement. Il s’agit d’une implantation calibrée et équilibrée, pas d’une preuve d’optimum global d’espace.

## Modules et niveaux

- RDC, surface Z=1 m : deux paires de fonderies et une paire de constructeurs de tiges.
- Deuxième niveau, surface Z=11,8 m : deux paires de plaques et deux paires de vis, rangées aux axes X=-12 / -4 / 4 / 12 m.
- Troisième niveau, surface Z=19,8 m : deux assembleuses, deux bus d’ingrédients décalés de 3 m en hauteur, fusion finale et coffre.
- 7 raccords muraux sous les collecteurs des paires ; un poteau pour chaque assembleuse. Une chaîne électrique relie les modules, sans dépasser quatre câbles par raccord Mk.1.

Les paires de fonte et de constructeurs sont clonées depuis les références natives documentées au chapitre 36, avec leurs têtes d’élévateurs, quaternions, courbes et raccords internes. Le collecteur de vis dispose d’une variante retournée de 180°, avec permutation des deux entrées latérales pour garder les chemins en place. Cela permet une distribution dans un sens et une collecte dans l’autre.

Le RDC contient **16 fondations en béton**. Les étages utilisent **32 cadres ajourés**, comme le principe de ROTORS. Ce profil ne promet pas les mêmes hauteurs avec des dalles pleines : leur substitution bloque l’export si une machine, un élévateur ou un convoyeur traverse la dalle. Les contrôles ne remplacent pas les essais de dégagements fins en jeu, notamment autour des accessoires souples et des cadres.

Réseau exporté : **54 convoyeurs Mk.2, 21 élévateurs, 24 câbles**, sans liaison `planned`. Les quatorze élévateurs internes des paires conservent leur gabarit Mk.1, suffisant pour leurs débits ; les sept liaisons verticales ajoutées sont Mk.2. Les capacités réelles des élévateurs sont vérifiées séparément.

## Utilisation dans l’atelier

1. Recharger l’application.
2. Dans un projet ayant ces objectifs, ouvrir **Importer / Exporter → Recalculer avec les modules compacts**, ou **Calculator → Calculer et placer**.
3. Confirmer le remplacement par le profil 4×4 à trois niveaux et cadres ajourés. Nom, objectifs, couleurs et tampon sont conservés ; Ctrl+Z permet de revenir.
4. Vérifier dans Vue 3D. Les traits physiques remplacent le réseau pointillé ; les élévateurs ne sont plus de simples réservations. Le repère d’entrée se trouve sur le répartiteur gauche au RDC.
5. **Enregistrer ce projet dans le jeu (.sbp)**, session SANDBOX.

L’exemple **Plaques 120 10 Paires** a été enregistré dans Mes projets du navigateur de validation. Son projet JSON est également fourni dans `38-compact-120-10.factory-blueprint.json`. Le brouillon habituel de l’utilisateur n’a pas été remplacé.

Le blueprint issu du vrai projet d’atelier a été écrit et relu dans :

`C:\Users\YOUR_USER\AppData\Local\FactoryGame\Saved\SaveGames\blueprints\SANDBOX\FT_Plaques_120_10_Paires_acdb6ad82e.sbp`

Après rechargement de la partie, chercher **FT_Plaques_120_10_Paires** dans les blueprints non classés. Alimenter le répartiteur gauche au RDC par son entrée sur la face X négatif, avec 120 minerais/min ; brancher un raccord mural ou un poteau au réseau. Attendre le remplissage initial des manifolds. Garder de la place dans le coffre pour vérifier le débit permanent de 10/min.

## Représentation et édition

`nativeProfile: iron-plates-pairs-v1` indique le profil calibré. Chaque objet porte un index de prototype autorisé et les données géométriques nécessaires à l’affichage. Chaque liaison physique décrit ses ports nommés et les segments Hermite dans le repère de son bâtiment source. L’export utilise les prototypes locaux autorisés, les transformations et recettes actuelles du projet, puis vérifie les raccords.

Noms, couleurs et déplacements cohérents sont conservés ; le fichier n’est pas un test prédéfini exporté indépendamment du plan affiché. Un déplacement isolé qui détache une courbe ou une tête, une cadence qui déséquilibre le réseau ou un ajout sans prototype natif ne sont pas réparés automatiquement : l’export demande de recalculer. Les réglages de structure et l’ajout automatique de poteaux sont désactivés pour ce profil afin de ne pas casser silencieusement son réseau.

Les autres chaînes continuent d’utiliser le placement logique existant. La généralisation des modules aux autres recettes, aux nombres impairs, aux dalles pleines avec traversées et au routage après édition reste à développer.

## Vérifications effectuées

- `tests/check_native_compact.py` : recettes, bilans de tous les ports, absence de mélange, capacités des bandes et élévateurs, 16 machines, 75,88 MW, coffre, 54 convoyeurs / 21 élévateurs / 24 câbles, 16 fondations / 32 cadres.
- Vérification des références réciproques, extrémités natives et tangentes. Le sens des têtes des élévateurs montants et descendants est contrôlé. Une tête retournée exprès est rejetée.
- Contrôles de corps de machines simplifiés, trajectoires dans le volume 4×4, continuité des splines, proximité des bandes à même hauteur et intersections avec les colonnes verticales. Géométrie interne des paires préservée depuis les sources natives.
- Écriture `.sbp` / `.sbpcfg` dans un dossier temporaire, relecture binaire, couleurs, renommage et translation cohérente ; débits falsifiés, géométrie détachée, coordonnées non finies et dalles incompatibles rejetés.
- `tests/check_workshop_native_compact.cjs` : import/export JSON avec données physiques conservées, 7 raccords muraux, 21 élévateurs, projection de toutes les courbes, cache sans mutation et translation.
- Régressions du modèle Atelier, de la sélection, du calculateur Auto, du placement logique et de l’export natif générique réussies.
- Chrome : génération depuis les objectifs, reconstruction depuis Importer / Exporter, visualisation 3D, enregistrement du projet, export natif SANDBOX et export JSON. Aucune erreur console observée.
- Le `.sbp` réellement installé dans SANDBOX a été reparsé et comparé au projet JSON exporté de l’atelier. Le reçu est conservé dans `38-compact-native-receipt.json`.

**Validation en jeu encore à faire.** La relecture du fichier et les contrôles géométriques/budgétaires ne mesurent ni le débit en partie, ni tous les volumes exacts des maillages du jeu.
