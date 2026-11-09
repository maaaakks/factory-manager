# Tableau simple, murs, entrée connectée et volume

18 octobre 2026 — prototype externe local. Cette étape simplifie l'affichage principal du document 15 ; les calculs détaillés restent accessibles.

## Carte lisible au dézoom

Les pastilles et cadres des zones disparaissent sous 0,75 pixel par mètre, ainsi que pour les zones trop petites à l'écran. Une usine enregistrée sélectionnée peut toujours garder son propre contour. Au dézoom, cliquer directement près d'une concentration permet de l'analyser et de zoomer dessus. Les pastilles réapparaissent au zoom rapproché. Les filtres d'altitude continuent de s'appliquer.

## Enveloppe guidée par les murs

Option « Guider par les murs fermés », activée par défaut. Depuis les machines d'un groupe, les segments des murs proches sont rasterisés sur une grille de 2 m, puis un remplissage détecte une région qui ne fuit pas vers l'extérieur. Une seconde tentative utilise les murs situés jusqu'à 24 m au-dessus du niveau des machines : cela fournit un guidage par projection du bâtiment, sans affirmer que le rez-de-chaussée est clos.

Pour éviter de fractionner une même chaîne à chaque cloison, l'enveloppe du résultat doit contenir les machines du groupe d'origine. Les machines proches à la même plage d'altitude dans cette enveloppe peuvent être regroupées. L'affichage est une enveloppe rectangulaire guidée par les murs, pas un volume exact et pas le contour précis d'une pièce. Les variantes inclinées, angles et portes sont exclues de cette première recherche de fermeture. Si aucune fermeture compatible n'est reconnue, le groupe spatial est conservé. La recherche s'arrête à 100 m autour du point de départ et essaye au plus douze machines par groupe.

Un résultat est marqué « enveloppe guidée par les murs ». L'utilisateur garde la possibilité de désactiver ce guidage ou de dessiner son propre périmètre. Les définitions enregistrées existantes ne sont pas remplacées silencieusement.

## Tableau de bord

La fiche principale affiche le nom, l'enregistrement, le nombre de machines et un tableau **Entrées → Sorties**. Les colonnes listent les ressources et les débits théoriques. Les sorties conservent la frontière au premier coffre et permettent d'en sélectionner un. Les intermédiaires, pourcentages par ressource et hypothèses sont rangés dans « Détails de production et diagnostic ».

Le pourcentage d'entrée est explicitement nommé **Transport** : rapport entre le plafond de convoyeurs calculé et le besoin des recettes, plafonné à 100 %. Ce n'est pas une validation de l'extraction ou du débit réel. L'absence de source, un parcours partiel ou des ports d'ingrédients ambigus laisse l'entrée « à vérifier ».

## Validation des chemins d'entrée

Le parcours remonte les ports connus jusqu'aux premières machines ou coffres et identifie les mineurs connectés. Les identifiants du gisement et le potentiel du mineur sont conservés quand disponibles. Le catalogue local inclut maintenant la cadence d'extraction normale issue de `mItemsPerCycle/mExtractCycleTime` des Docs installées ; la pureté absente reste inconnue.

Le plafond des convoyeurs est un flux maximal avec capacité portée par chaque tronçon, pour éviter de compter plusieurs fois un tronçon partagé avant une séparation. Les convoyeurs/ascenseurs ordinaires Mk.1 à Mk.6 utilisent les capacités nominales 60/120/270/480/780/1200 objets/min. Les sources ne reçoivent pas arbitrairement une cadence de mineur normale quand la pureté manque. Les transports moddés et répartitions avancées restent non validés. Les partages avec d'autres usines ne sont pas simulés ; le plafond calculé peut leur être partiellement réservé dans la partie réelle.

Références du catalogue de capacité : [convoyeurs, Wiki officiel](https://satisfactory.wiki.gg/wiki/Conveyor_Belts), [mineurs et pureté](https://satisfactory.wiki.gg/wiki/Miner_MK2). Les paramètres d'extraction proviennent aussi des Docs locales installées.

Sur `kouyère_110426-104516.sav`, le groupe cuivre correspondant aux chiffres de l'utilisateur contient 36 machines. La remontée trouve trois mineurs Mk.2 et un plafond de transport d'entrée de 720/min pour un besoin théorique de 360 minerais/min. La pureté n'est pas renseignée dans les propriétés sérialisées des gisements inspectés : extraction et alimentation réelle non confirmées.

## Voir la forme de l'usine

« Voir le volume de l'usine » ouvre un aperçu isométrique local. Positions et rotations viennent de la sauvegarde. Murs, fondations et toitures utilisent des dimensions simplifiées ; machines et autres constructions sont représentées par des boîtes. Les convoyeurs utilisent leur géométrie enregistrée. Un curseur fait tourner la vue ; une case masque les toitures. L'aperçu est limité à 2 500 constructions.

Ce rendu ne contient ni modèles, ni matériaux, ni textures du jeu et ne reproduit pas fidèlement chaque variante. Les dimensions/hauteurs, l'ordre d'occlusion et les couleurs sont schématiques. Pour un rendu proche du jeu, il faudrait une bibliothèque de modèles et matériaux correspondant aux variantes, puis appliquer les personnalisations de la sauvegarde. Cette étape ne récupère pas ces assets dans l'installation du jeu.

## Vérifications

- `node tests/check_dashboard.cjs` : seuil de zoom ; enceinte fermée, ouverte et située à un autre étage ; capacité d'entrée avec un tronçon partagé ; type de mineur ; ambiguïté de plusieurs ingrédients ; projection et dimensions schématiques.
- Tests existants de chemins vers coffres, production et persistance conservés.
- Import de jojo : 7 838 constructions, 1 939 murs, empreinte de sauvegarde inchangée.
- Import de kouyère : 34 139 constructions, 7 611 murs, 38 groupes de densité avant guidage par les murs.
- Navigateur : tableau compact, détail des sources, dézoom sans étiquettes (zéro pastille sur la vue d'ensemble de kouyère), sélection d'une usine et ouverture/rotation/masquage de toiture dans l'aperçu. La zone cuivre de 36 machines obtient une enveloppe guidée par les murs, sans remplacement de la définition personnelle « Copper » déjà enregistrée.

La prochaine étape de précision reste l'alimentation complète : pureté des gisements et répartition réelle des flux, puis propagation des limitations jusqu'aux sorties. Une valeur « Transport 100 % » ne remplace pas cette validation.
