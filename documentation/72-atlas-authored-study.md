# Atlas — étude architecturale 01

21 octobre 2026. Cette étude reprend le travail après le constat que les premières variantes Signature restaient trop proches de l'ancienne boîte tramée.

## Le changement de méthode

Atlas est une composition fixe de **64 × 48 m**, avec 32 m de hauteur minimale. Les grandes décisions sont dessinées explicitement : une halle haute, une galerie basse, une terrasse, une bande technique et un auvent d'accueil. Le générateur de façades historique n'est pas utilisé pour cette enveloppe. Il n'y a pas de bouton de variation aléatoire.

La page locale `/atlas` permet de tourner autour de cette composition, de voir la façade, une coupe, le côté technique et les vitrages. Elle fonctionne en lecture seule et propose le téléchargement de la maquette. Dans Design → Façades → Chapitre II, la carte Atlas ouvre cette page. Les anciennes variantes Signature restent lisibles pour les projets existants ; elles sont retirées des cartes proposées. Classiques procéduraux et M05 sont conservés.

## Ce qui a été tiré des vidéos

Les références ont été consultées par leurs chapitres, leurs descriptions et des séquences visuelles de plusieurs sections. Le commentaire audio n'a pas été transcrit ; ces notes distinguent les observations visuelles de leur application dans Atlas.

| Référence | Observation retenue | Application concrète |
|---|---|---|
| [Tutoriel de TotalXclipse](https://www.youtube.com/watch?v=sMarWMlGAjE), sections profondeur, matières, lumière naturelle et détails | Une paroi gagne à avoir un socle, un plan de remplissage et des éléments extérieurs distincts. Les détails servent ces plans. | Portiques à l'avant, vitrage central à 12 m de la limite avant, tableaux de baie profonds, couverture inclinée et rives qui suivent ses pentes. |
| [Compact Factory de Reekitect](https://www.youtube.com/watch?v=Js7zbvNY7CM) | Des contours facettés et des supports inclinés donnent une direction au bâtiment. Les lignes lumineuses soulignent des contours déjà lisibles. | Épaules inclinées des deux portiques ; appuis obliques et auvent bas d'accueil ; accents localisés. Les lignes émissives ne sont pas encore implémentées. |
| [Usine de vis de Tenhope](https://www.youtube.com/watch?v=IMOjMljmZ-o) | La production, les niveaux et les circulations participent au dessin. | Six volées d'escalier natives, une terrasse et un belvédère tourné vers une petite ligne de cuivre. Atlas garde une enveloppe plus fermée que cette référence. |
| [Nouvelle référence importante de TotalXclipse](https://www.youtube.com/watch?v=FeroE_hbawc) | Organiser l'espace, dédier des zones et utiliser les fonctions comme éléments de composition. | Séparation du parvis, de l'accès, de la galerie, du volume de production et de la bande technique ; ventilation portée par cette bande. |

### Les sept thèmes de la nouvelle référence

| Repère dans la vidéo | Traduction dans cette étude | Limite actuelle |
|---|---|---|
| 0:58 — Gestion de l'espace | Parvis de 8 m devant la halle, galerie latérale et passage sous la marquise. | Le gabarit est fixe, pas adapté à n'importe quelle production. |
| 3:38 — Zones de production dédiées | Les deux fonderies occupent la halle ; le coffre et les trajets ont été placés pour laisser les structures libres. | Une seule petite ligne de démonstration. |
| 5:46 — Éclairage | Lanterneau central, grands jours et trois projecteurs de paroi. | Les projecteurs décoratifs sont posés mais ne sont pas alimentés. Aucune lumière nocturne n'est simulée dans l'aperçu. |
| 7:36 — Profondeur | Portiques sur deux plans, façade centrale reculée, marquise et tableaux entre les plans. | Les jonctions doivent encore être inspectées avec les meshes réels du jeu. |
| 9:52 — Fonction mise en scène | Escalier, garde-corps, belvédère, extracteurs, charpente et convoyeurs sont de vraies pièces exportées. | Les parcours piétons et le fonctionnement de la ligne ne sont pas testés dans le jeu. |
| 13:01 — Éléments d'ambiance | Petit auvent d'arrivée, seuil et repères au sol. | Pas encore d'enseignes ni d'accessoires d'exploitation composés. |
| 14:10 — Infrastructures de transport | À conserver comme règle pour les futures liaisons entre bâtiments. | Aucune voie ferrée ajoutée à cette étude. |

## Géométrie et finitions

- La couverture de la halle a deux pans inclinés et un lanterneau. Les pignons inclinés sont fermés par leurs triangles natifs ; les rives suivent la pente.
- Les portiques ont des épaules facettées. Le premier est composé de plusieurs poutres peintes parallèles ; le second se trouve plus loin dans la profondeur.
- Les petits retours profonds sont constitués de cours jointifs de poutres natives. Ils ne sont plus représentés par quelques lames espacées.
- La galerie monte de 1 à 13 m par six volées d'escalier. La terrasse laisse une ouverture au-dessus de l'arrivée ; une porte haute donne sur le belvédère de la halle. La baie qui aurait obstrué cette porte a été retirée.
- La tour et la bande technique ont leurs propres hauteurs, équipements et rythme de remplissage. Elles ne sont pas des répétitions de la façade vitrée.

Ces décisions sont stockées dans le catalogue partagé, sous `studies.atlas`. La recette éditable est `external-tool/tools/build_atlas_study.py`. Après modification de la recette, exécuter ce script puis `tools/build_architecture_catalog.py` pour régénérer le catalogue navigateur. Les exemples et leur rapport natif doivent ensuite être régénérés avant mise à jour de la page de revue.

## Pièces natives et preuve obtenue

L'étude contient **467 pièces architecturales**, dont six escaliers, leurs paliers, des garde-corps, trois projecteurs et des équipements de ventilation. Elle utilise quelques gabarits d'acteurs natifs isolés provenant de la bibliothèque M05 de JazzFrank déjà présente et attribuée dans le projet ; son assemblage est original.

Le cas de cuivre demande théoriquement **60 minerais → 60 lingots/min**, pour 8 MW de machines hors projecteurs. L'export relu comporte huit convoyeurs, deux élévateurs et trois câbles électriques réciproques. L'entrée de minerai et la connexion au réseau électrique externe restent à raccorder.

Contrôles réalisés : géométrie identique dans JS et Python, géométrie préservée après routage natif, refus d'un mauvais format ou d'une collision avec l'escalier, refus d'un trajet traversant une structure, persistance JSON, longueurs de poutres natives, relecture du `.sbp` et du `.sbpcfg`, présence des six acteurs d'escalier, des trois projecteurs et des câbles. Les tests historiques de familles restent couverts par 168 scènes JS et 42 exports de combinaisons famille/variante ; les 15 scènes Signature précédentes restent compatibles. Les trois anciens tests déjà signalés dans la documentation 71 ne sont pas comptés comme corrigés.

L'aperçu utilise les géométries schématiques des pièces et des volumes de machines simplifiés. Il ne reproduit pas les textures, les reflets, l'éclairage ou les collisions des meshes de Satisfactory. **Aucun contrôle en jeu n'a été réalisé.** Le format 8 × 6 est un **XL expérimental** : son placement dans le jeu et sa réédition dans un designer vanilla restent à vérifier.

## Fichiers fournis

- `Halle-Atlas-etude-01.factory-blueprint.json` : importer dans Factory Manager pour éditer la maquette.
- `Atlas-etude-01.sbp` et `Atlas-etude-01.sbpcfg` : paire native expérimentale, conservée hors des dossiers du jeu.
- Les captures montrent la composition et la coupe de la page locale. Le modèle interactif permet aussi d'examiner la façade et le côté technique.
