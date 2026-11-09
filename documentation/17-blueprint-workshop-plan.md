# Atelier de blueprints — plan proposé

Le périmètre de première version est précisé dans [Créateur manuel de blueprints](18-manual-blueprint-creator-plan.md) : ouvrir, exporter, créer machines/convoyeurs/câbles et vérifier en jeu. La fusion et l'assemblage automatique décrits ici passent après cette version.

19 octobre 2026. Proposition de développement ; aucune importation, fusion ou exportation de blueprint n'a été validée en jeu dans cette étape.

## Décision proposée

Commencer le layout par un atelier externe de blueprints. Il sera distinct de l'explorateur de monde, avec un modèle et une interface propres, mais partagera le catalogue, les transformations, les graphes et l'aperçu en volume. Il ne nécessite pas de mod en jeu pour les premières étapes. L'édition en direct et la génération libre d'usines complètes restent des évolutions séparées.

La première bibliothèque doit contenir des modules construits et vérifiés en jeu. La création de nouveaux blueprints commencera par duplication/paramétrage de modules connus. Une génération arbitraire de toutes les classes de bâtiments est hors du premier périmètre.

## Trois opérations différentes

- **Assembler un projet** : placer plusieurs instances de modules dans notre atelier. Le projet peut dépasser la taille d'un blueprint natif.
- **Fusionner un blueprint exportable** : produire un fichier natif unique avec les objets transformés, les identités uniques et les références internes cohérentes. Le résultat doit respecter le format et le gabarit cible.
- **Raccorder les modules** : créer ou valider les liaisons entre ports. Des modules visuellement adjacents ne sont pas nécessairement connectés. Cette opération a sa propre étape de validation.

Si l'assemblage dépasse le gabarit autorisé, conserver une collection de blueprints et un plan de placement. Ne pas présenter cette collection comme un blueprint géant directement plaçable.

## Première preuve à obtenir

Avec un petit blueprint vanilla connu : lire le fichier et sa configuration, afficher son contenu, réexporter sous un nouveau nom, relire le résultat et vérifier son chargement/placement dans le jeu. Les originaux restent intacts. Une réimportation réussie dans notre parseur n'est pas une preuve de compatibilité en jeu.

Le parseur embarqué possède déjà `sbp_parse.parseBlueprint`, `resaveBlueprint`, `parseBlueprintConfig` et `resaveBlueprintConfig`. Son code accepte un ensemble précis de versions et de gabarits. Cela prouve l'existence des fonctions, pas la compatibilité de tous les blueprints ou la capacité de fusion. Les versions de fichier, du jeu et les types supportés devront être enregistrés pour chaque fixture.

## Tranches de développement

| Étape | Fonction petite et testable | Critère de passage |
| --- | --- | --- |
| B0 — Lecture | Ouvrir un petit blueprint vanilla ; afficher bâtiments, versions et gabarit | Nombre, types, positions et rotations cohérents avec le module de référence ; format inconnu explicitement refusé |
| B1 — Copie fidèle | Exporter une copie nommée avec les métadonnées nécessaires | Relecture structurelle correcte et copie chargée/placée en jeu sans perte de ses connexions |
| B2 — Manipulation | Placer deux instances, déplacer sur grille, tourner de 90°, annuler/rétablir | Transformations déterministes ; fichier source inchangé ; comparaison avec une disposition de référence |
| B3 — Fusion sans raccord | Fusionner deux très petits modules dans le gabarit cible | Identités distinctes, références internes conservées, coûts/métadonnées cohérents et placement en jeu réussi |
| B4 — Interfaces | Déclarer sur chaque module ses entrées/sorties, orientation, hauteur, ressources et capacités | Deux interfaces compatibles s'alignent ; incompatibilité visible ; données incertaines non inventées |
| B5 — Un raccord | Relier deux modules par un convoyeur simple dans un corridor réservé | Géométrie, sens et références valides ; convoyeur réellement connecté après placement en jeu |
| B6 — Modules paramétrés | Répéter une rangée connue et ses interfaces dans les limites supportées | Export de plusieurs tailles de la même famille, chacune vérifiée |
| B7 — Assemblage assisté | Choisir entrée/sortie cible et proposer quelques arrangements de modules validés | Bilan faisable, pas de recouvrement interdit connu, accès conservés, différences mesurées entre variantes |
| B8 — Extension | Étages, ascenseurs, styles de murs/toitures et autres familles de machines | Ajout famille par famille, avec fixtures et limites propres |

B0 à B3 commencent avec fondations, murs puis une petite machine et ses liaisons internes. Les circuits de fluides, trains, bâtiments moddés et rotations libres sont exclus du premier périmètre. Le gabarit cible est explicite ; pas de contournement des limites vanilla dans la première version.

## Métadonnées de module

Chaque module conservera son fichier source et sa version, son repère d'origine, ses instances, ses dimensions, les dégagements nécessaires et ses zones réservées. Les interfaces déclarées décriront position locale, direction, altitude, type de connexion, ressource et débit. Leur déclaration manuelle est acceptable au départ ; le graphe et la géométrie permettront ensuite de les assister.

Une composition conserve ses instances et transformations sans perdre la provenance. L'export peut aplatir la composition lorsque le format et le gabarit le permettent. Déplacer un module ne doit pas réécrire le fichier de bibliothèque d'origine.

## Difficultés et limites

La lecture et l'aperçu réutilisent des briques existantes. La fusion native est plus sensible : identités d'objets/composants, références imbriquées, transformations, convoyeurs en coordonnées locales, versions et métadonnées. La copie fidèle B1 est le premier verrou à lever avant d'investir dans l'interface de fusion.

Le calcul spatial nécessite des dimensions et dégagements fiables : nos boîtes schématiques actuelles ne prouvent pas qu'une disposition est constructible. Les références prises en charge seront validées sur des fixtures en jeu, pas seulement sur l'absence d'intersection de rectangles.

L'optimisation commencera par des arrangements limités et comparables : rangées, face à face, couloir logistique, puis étage. Les résultats annonceront surface, hauteur, longueur de transport et débit théorique. Un résultat « meilleur parmi les variantes testées » ne sera pas annoncé comme optimum global.

## Sources vérifiées

- Parseur local embarqué : `external-tool/vendor/sat_sav_parse/sbp_parse.py` et README, section `sbp_parse.py`. [Notes de version de l'auteur](https://github.com/GreyHak/sat_sav_parse/releases).
- [Blueprints : format, placement et connexion](https://satisfactory.wiki.gg/wiki/Blueprint).
- [Blueprint Designer : gabarits et restrictions](https://satisfactory.wiki.gg/wiki/Blueprints). Les volumes vanilla documentés sont 32³, 40³ et 48³ m selon le niveau ; ne pas les confondre avec l'encombrement extérieur du Designer. Les mineurs ne font pas partie du premier module exportable : leurs arrivées sont des interfaces externes.

## Première livraison recommandée

Une page « Atelier blueprints » : **Ouvrir → aperçu → exporter une copie**, avec le format et le gabarit indiqués et un résultat de validation lisible. La suite commence uniquement après la preuve de chargement et de placement de cette copie dans le jeu.
