# 62 — Plaques renforcées : cellules 5×5 issues de l'exemple utilisateur

Le plan `test` ouvert dans l'atelier était un terrain de 64×176 m (8×22 fondations). La génération précédente traitait les sous-zones comme des groupes indépendants à relier après placement et l'ancien serveur gardait son routeur Python en mémoire. Ce résultat ne représentait pas le modèle de sous-zones demandé.

## Référence et périmètre

Source : `exemple_60mineraix5plaquesrenfor.sbp`, fourni par l'utilisateur, conservé dans `data/workcell-iron-reference.sbp`. Ses huit machines sont reprises à leurs positions et orientations, avec un décalage vertical de 1 m pour la fondation. Deux fonderies, deux constructeurs de plaques, un constructeur de barres, deux constructeurs de vis et une assembleuse. Toutes les machines restent sur un seul sol. Le principe rejoint les paires face à face du blueprint rotors ; la verticalité reste dans les collectes de cellules, pas dans une forêt de bus génériques.

Les recettes de la maquette n'étaient pas toutes configurées et un convoyeur contournait les constructeurs de vis. La version de production remplace ce contournement par la collecte des vis vers la deuxième entrée de l'assembleuse. Cadences : fonderies 100 %, plaques 75 % chacune, barres 100 %, vis 75 % chacune, assemblage 100 %. Bilan théorique : 60 minerais → 60 lingots → 30 plaques + 15 barres → 60 vis → 5 plaques renforcées/min. La sortie reste un port libre d'assembleuse ; aucun coffre n'est ajouté dans l'emprise.

## Contrat de flux central

Les paires se font face autour de l'axe X=-8 m de la référence. La distribution entre au centre, la production ressort par les élévateurs latéraux vers la collecte haute, puis les lingots redescendent vers le distributeur central suivant. Le bus de lingots dessert plaques et barres ; la collecte des barres alimente la cellule de vis. Seules les plaques et les vis aboutissent aux deux entrées de l'assembleuse. La liaison de vis rejoint l'assemblage par le couloir de service central, sans grande boucle périphérique. Les contrôles verrouillent cet axe, les hauteurs de distribution/collecte, les matériaux aux entrées d'assemblage et les poses mesurées du blueprint utilisateur.

## Intégration

`iron-plates-workcells-v1` conserve les tracés et les ports calibrés. Les poses viennent de la référence native version 60 ; les acteurs sont reconstruits avec les modèles version 52 déjà utilisés par l'exporteur. Ce passage est vérifié par réouverture binaire. Le `.sbp` utilisateur original reste intact.

Le générateur de l'atelier sélectionne ces cellules pour fer → plaques renforcées jusqu'à 5/min, en rectangle et sans demande explicite d'étages. Auto commence à 40×40 m ; un terrain fixe inférieur est refusé sans remplacer le projet. Un terrain plus grand centre les mêmes cellules. La variante à entrée de lingots retire les fonderies et leur liaison de descente et réutilise directement la distribution centrale de lingots. Les autres recettes gardent leur comportement actuel : la généralisation de cette implantation reste une étape suivante.

Le profil conserve 25 fondations, 20 convoyeurs, 11 élévateurs et 11 câbles. Les élévateurs sont ceux des collectes locales et les transitions de cellules ; toutes les machines restent à Z=1 m. L'export et l'aperçu utilisent les mêmes ports et courbes. Les déplacements qui détachent les raccords sont refusés à l'export.

## Vérifications

- `node tests/check_workshop_workcells.cjs` : génération réelle 60→5, Auto 5×5, terrains fixes 40/48 m, conservation du projet source, rejet atomique du 4×4.
- `python tests/check_native_workcells.py` : bilan de flux, raccords et directions, corps de machines et convoyeurs, alimentation des huit machines, réouverture `.sbp`, cadences 1/2,5/5 et refus des modules détachés.
- Régression de l'ancien profil compact : `check_native_compact.py`.
- Régression des autres sous-zones : `check_workshop_subzones.cjs`.

Les contrôles sont locaux et natifs. La production et les accès piétons restent à vérifier en jeu. Aucun fichier n'est installé automatiquement dans les blueprints ou sauvegardes du jeu.

## Régression du calculateur : Compact + Bas

L'endpoint `/api/workshop/compact` renvoyait à nouveau le profil historique sur trois étages, même lorsque le planificateur demandait `workcells-5x5-v1`. Le serveur distribue maintenant explicitement ce profil et interdit un résultat multi-étages sous `storeyMode=single`. Le planificateur vérifie également le profil retourné et les niveaux réels avant de remplacer le projet.

`node tests/check_calculator_bas_http.cjs` teste le véritable serveur local (URL réglable par `FACTORY_TEST_URL`) : minerai et lingots, Compact avec Bas/Auto, 5×5 et un étage ; refus d'une réponse historique et de niveaux incompatibles ; contrôle serveur même sans marqueur de profil. Le parcours navigateur complet a été rejoué depuis les objectifs 60 minerais → 5 plaques, choix Compact et Bas, puis « Créer le blueprint ». Résultat affiché : un étage, 31 objets, 37,94 MW théoriques. Aucune écriture dans les dossiers du jeu.

## Formes disponibles et étages

Découpé est retiré du calculateur et de l'implantation. Les anciens projets restent lisibles ; une nouvelle génération découpée est refusée. Haut reste visible mais désactivé, avec une explication, et sa génération est refusée plutôt que de produire un placement générique non fiable.

Pour fer ou lingots → 5 plaques renforcées/min maximum, Allongé réutilise les cellules natives sur 32×64 m (4×8 fondations). L'assembleuse prolonge la ligne de cellules ; ses deux entrées reçoivent les plaques et les vis via deux descentes dédiées, sans bus de plusieurs centaines de mètres. Les poses internes, le bilan matière et les directions des ports sont conservés. Rectangle conserve le 40×40 existant. Bas et Auto gardent toutes les machines au même niveau. Une emprise fixe trop courte est refusée sans remplacer le projet.

Tests `check_workshop_layout_shapes.cjs` puis `check_native_layout_shapes.py` : huit variantes (deux matières d'entrée, deux formes, Bas/Auto), modèles, bilan de flux, collisions, directions et réouverture binaire. `FACTORY_SHAPE_SCENES` et `FACTORY_SHAPE_TMP` permettent de placer les scènes et fichiers de test hors du dossier du projet. Ces contrôles ne constituent pas une validation en jeu.
