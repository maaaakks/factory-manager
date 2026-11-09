# Patterns compacts relevés dans les blueprints kouyère

19 octobre 2026. Analyse des fichiers locaux, sans modification des originaux ni interaction avec la partie en cours.

## Sources et lecture

Fichiers examinés dans `C:\Users\YOUR_USER\AppData\Local\FactoryGame\Saved\SaveGames\blueprints\kouyère` : `SMELTERX2.sbp`, `CONSTRUCTORx2.sbp`, `ROTORS 4x4 - 10.667.sbp`.

Le relevé complet `36-layout-pattern-audit.json` contient les empreintes SHA-256, transformations, recettes, raccords, courbes, élévateurs et distances. `36-layout-pattern-audit.txt` fournit un relevé textuel. Les scripts de travail `audit-layout-patterns.py` et `extract-compact-patterns.py` parsèrent les fichiers natifs avec le parseur déjà embarqué.

La page locale **[Références compactes](http://127.0.0.1:8765/patterns.html)** affiche une vue de dessus et une élévation X/Z ou Y/Z, avec choix du niveau, électricité et cadres/planchers. Elle est accessible depuis **Atelier → Sols et espacement → Étudier les modules compacts**. Les corps et antennes sont des enveloppes simplifiées ; ce n’est pas un rendu des maillages du jeu. Les connexions électriques sont des traits schématiques entre les acteurs, pas une reconstruction exacte des câbles.

## Pattern principal : une paire traversée par une colonne centrale

Deux machines se font face. Le répartiteur se trouve entre leurs entrées à 1 m du sol. Les sorties partent aux extrémités opposées, remontent par deux élévateurs, puis reviennent vers un fusionneur situé au-dessus du répartiteur. Les entrées et sorties communes suivent donc le même axe horizontal à des hauteurs différentes.

| Mesure relative au sol des machines | SMELTERX2 | CONSTRUCTORx2 |
| --- | ---: | ---: |
| Distance entre centres des machines opposées | 14 m | 12 m |
| Répartiteur | +1 m | +1 m |
| Fusionneur, même X/Y que le répartiteur | +9 m | +6 m |
| Montée de chacun des deux élévateurs | 8 m | 5 m |
| Convoyeur droit entre répartiteur et chaque machine | 3 m | 2 m |
| Raccord mural sous le fusionneur | +8,6801 m | +5,70009 m |
| Nombre de câbles vers les deux machines | 2 | 2 |

Enveloppes au sol des seuls corps de machines, à partir des dégagements durs installés : environ 5×24 m pour la paire de fonderies et 8×22 m pour les constructeurs. Ces rectangles ne constituent pas une preuve de volume total des accessoires ou de circulation piétonne.

Le raccord mural utilise une rotation comprenant une inclinaison de 90°, pas simplement une rotation sur le sol. Il est monté sous le fusionneur, à environ 0,32 m ou 0,30 m sous son origine. Le bon gabarit conserve ce quaternion et ses références de câbles.

## ROTORS : répétition de ce module, pas placement machine par machine

Le graphe natif permet de détecter **2 paires de fonderies et 7 paires de constructeurs**, chacune reliée à un répartiteur commun et à un même fusionneur après ses élévateurs. Un constructeur reste seul. Le total est **4 fonderies, 15 constructeurs et 3 assembleurs**, soit 22 machines dans un concepteur 4×4.

- Les deux rangées de paires de fonderies sont espacées de **5 m**, leur largeur de dégagement dur.
- Les rangées de paires de constructeurs sont espacées de **8 m**, leur largeur de dégagement dur.
- Les trois assembleurs sont espacés de **9 m**, leur largeur de dégagement dur.
- Machines à **Z=0 / 10,8 / 18,8 m**. Les collectes des constructeurs se trouvent à +6 m de leur base ; celles de la fonte à +9 m.
- Un même axe de distribution/collecte traverse plusieurs rangées, puis rejoint les axes des autres niveaux.
- **10 raccords muraux** desservent les groupes ; les **3 assembleurs ont chacun leur poteau au sol**. Il ne s’agit donc pas d’imposer le même accessoire électrique partout.
- Le fichier contient **58 convoyeurs et 32 élévateurs, dont 8 descendants**.

Le gain vient de la répétition d’un module complet avec ses connexions. Ajouter quatre mètres autour de chaque machine détruit cette structure. À l’inverse, rapprocher aveuglément tous les rectangles sans réserver la colonne et ses têtes d’élévateurs ne reproduit pas le blueprint.

Le nom `10.667` n’est pas une mesure de production. Les trois assembleurs y sont enregistrés avec leur potentiel nominal par défaut, et un constructeur de vis possède un potentiel demandé d’environ 0,67. Cette analyse porte sur l’implantation ; elle ne certifie pas une efficacité individuelle de 100 % ni le débit en jeu.

## Petits espacements : ce qui est réellement mesuré

Dans ROTORS, la paire de répartiteurs de la fonte et la paire de fusionneurs correspondante sont espacées de **5 m centre à centre**. Les ports de passage sont à ±1 m de leur centre : il reste une bande droite de **3 m entre les deux ports**. Les groupes de constructeurs présentent souvent 8 m entre centres et donc 6 m de bande entre ports.

Les bandes de **2 m** observées dans CONSTRUCTORx2 relient un répartiteur à une entrée de machine. Ce n’est pas la même mesure qu’une distance entre centres de deux répartiteurs, ni une réserve de virage. Les deux bus d’ingrédients d’assemblage présentent aussi un décalage vertical de **3 m**.

Deux splines enregistrées dans ROTORS présentent une courbure horizontale locale échantillonnée d’environ **1,2105 m de rayon** :

- `Build_ConveyorBeltMk2_C_2146573637` ;
- `Build_ConveyorBeltMk3_C_2146573633`.

La dérivée et la dérivée seconde des Hermite sont évaluées sur les segments natifs. C’est une mesure sur ces tracés, pas une limite minimale universelle du moteur. Le rayon de 2 m du routeur actuel est conservateur. Il ne faut ni rejeter un gabarit connu uniquement pour ce motif, ni abaisser toutes les courbes à 1,21 m sans vérifier leur contexte.

## Attention particulière aux élévateurs

Le sens vient des composants connectés et du transform supérieur ; il ne se déduit pas de la seule comparaison des altitudes. Un acteur peut commencer en haut et porter une translation supérieure négative : ROTORS en utilise huit.

Les têtes directement accrochées aux machines ne se traitent pas comme un simple tube dont les ports seraient toujours à l’origine de l’acteur. Dans les petites références, la distance entre l’origine basse du tube et le port de sortie mesuré de la machine est différente pour la fonderie et le constructeur, environ 2 m et 1 m. Cela ne permet pas de généraliser un décalage de tête unique. Il faut préserver la géométrie et la connexion natives du module, puis calibrer ses interfaces extérieures.

L’assemblage doit aussi préserver le transform de la tête haute, les éventuelles traversées de plancher, l’espace de la tête au-dessus du tube et la capacité de chaque bande/élévateur. Une enveloppe 2D ou un trait vertical ne suffit pas à les vérifier.

## Dégagement souple et sol plein ne sont pas équivalents

Le constructeur possède un corps de dégagement dur de 6 m, mais des appendices souples qui montent jusqu’à 8,5 m. Les sorties de référence passent à +6 m sur un axe dégagé, pas à travers toutes les parties du constructeur. Le rectangle complet de hauteur 8,5 m serait trop grossier pour décider de tous les passages de bande.

ROTORS utilise des **cadres ajourés**, pas des étages complets de béton. Son second pas vertical de 8 m ne peut donc pas être repris automatiquement avec une dalle pleine de 1 m. La hauteur du fusionneur de fonte, ses accessoires et les antennes doivent être vérifiées avec le matériau et les ouvertures réellement choisis. Les cadres, dalles pleines et réservations centrales doivent devenir des profils de structure distincts.

## Décisions pour la refonte du placement

1. **Assembler des modules calibrés**, pas placer toutes les machines puis chercher la logistique. Premier lot : paire de fonderies, paire de constructeurs, variante simple pour les nombres impairs, paire d’assembleurs à deux bus d’entrée.
2. **Définir les interfaces du module** : entrée et continuation du répartiteur, collecte et continuation du fusionneur, point électrique, volumes durs occupés, dégagements souples contextuels, têtes et chemins d’élévateurs. Les corps et la colonne doivent être réservés ensemble.
3. **Répéter les modules par rangées et par étage**, avec un pas transversal mesuré de 5/8/9 m selon la famille, puis router seulement les liaisons entre modules. Vérifier ces nouveaux raccords ; ne pas considérer toute proximité comme une connexion.
4. **Réévaluer les capacités après le choix de recette.** Une paire de constructeurs de tiges donne 30/min ; deux constructeurs de vis donnent 80/min. Le collecteur commun ne peut donc pas rester automatiquement en Mk.1 après réutilisation du même gabarit. Une colonne partagée par plusieurs paires doit être dimensionnée au débit cumulé.
5. **Donner un score à la lisibilité** : peu d’axes, peu de croisements, sorties regroupées, une montée électrique entre étages, accès conservés. La seule minimisation d’aire n’est pas suffisante.

Pour le cas du test 04 : 4 fonderies donnent 2 paires ; 3 constructeurs de plaques donnent une paire et un simple ; 2 de tiges donnent une paire ; 3 de vis donnent une paire et un simple. Les deux assembleurs forment un groupe de finition. Cette décomposition est un candidat à reconstruire et à tester, pas une nouvelle version déjà vérifiée du test 04.

Le fichier `FT_TEST_04` reste intact. Son ancienne implantation ne sert pas de référence esthétique. L’algorithme actuel de placement des machines et ses liens logiques n’ont pas encore été remplacés par cette composition native en modules. La page de références le précise.

## Amélioration électrique déjà intégrée

L’atelier propose **Un poteau par machine** par défaut, avec **Poteaux partagés** comme autre choix. Après « Relier l’électricité », le poteau est placé au même coin relatif de la machine, en suivant sa rotation. Les quatre coins sont essayés dans un ordre stable si le premier est occupé. Les poteaux automatiques existants sont repositionnés ; les poteaux nommés manuellement ne sont pas déplacés. Une chaîne parcourt chaque étage avant de passer au suivant.

Chaque poteau dédié garde au plus trois raccords : sa machine et deux voisins. Le mode partagé reste borné à deux machines par poteau, pour réserver les prises de la chaîne. Les répétitions réutilisent les poteaux et le style est conservé dans le JSON du projet. Aucun brouillon utilisateur n’est réorganisé automatiquement au chargement : le changement s’applique en relançant l’assistance électrique.

Les raccords muraux sous fusionneur sont documentés et visualisés. Ils ne sont pas encore ajoutés arbitrairement dans le planificateur : ils feront partie du gabarit complet, avec leur vraie fixation et leur rotation 3D.

`tests/check_compact_patterns.cjs` vérifie les mesures et topologies du relevé ainsi que le choix électrique, les coins selon rotation, la réutilisation, la persistance et les limites des prises. Les tests précédents du modèle, de l’assistance et de l’apparence passent également.
