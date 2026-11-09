# Export natif du projet courant de l’atelier

19 octobre 2026.

## Utilisation

Dans **Importer / Exporter**, choisir la session puis **Enregistrer ce projet dans le jeu (.sbp)**. Le bouton utilise une copie du projet ouvert, son nom actuel et ses objets ; il n’exporte plus un module de test à sa place. Les anciens modules sont conservés dans un sous-menu distinct.

L’API `POST /api/blueprints/project` reçoit le projet et la session, vérifie le plan, construit les acteurs natifs, écrit et relit le binaire dans un dossier temporaire, puis enregistre le couple `.sbp` / `.sbpcfg` dans le dossier de blueprints choisi. Le bouton Enregistrer habituel conserve sa fonction de sauvegarde du projet éditable. L’export JSON reste disponible.

Le nom du fichier est `FT_<nom normalisé>_<empreinte identifiant projet>`. Deux projets de même nom sont distincts. Réexporter le même projet sous le même nom actualise son blueprint avec sauvegarde des fichiers précédents dans `external-tool/data/native-backups`. Le descripteur natif doit identifier ce projet avant tout remplacement ; un fichier extérieur ou illisible à la même destination est protégé. Les liens symboliques et les sessions sortant du dossier autorisé sont refusés.

Après export, recharger la session Satisfactory pour actualiser le catalogue. L’application confirme le nom et le dossier exacts, le nombre de bâtiments, convoyeurs, câbles et la puissance nominale. Le fonctionnement dans le moteur de jeu reste à tester pour chaque nouveau plan.

## Éléments pris en charge

- Fonderies, constructeurs, assembleurs, coffres Mk.1, poteaux Mk.1, répartiteurs et fusionneurs.
- Positions du plan et orientations de 90°. Conversion de l’axe de sortie de l’atelier vers celui de chaque classe native, avec unités mètres → centimètres et centrage dans le concepteur.
- Recettes solides compatibles avec les ports de la machine, un seul produit et au plus deux ingrédients. Les chemins d’assets viennent du catalogue du jeu installé. Les inventaires sont vides et leurs filtres sont adaptés à la recette ; l’horloge jusqu’à 100 % est conservée.
- Couleur globale activée : primaire et secondaire converties de sRGB vers les couleurs linéaires natives, appliquées aux bâtiments et accessoires générés. Sans personnalisation activée, les gabarits gardent leur apparence normale.
- Sols complets en béton, métal FICSIT ou asphalte, d’épaisseur 1 ou 2 m, dans les formats 4×4, 5×5 et 6×6.
- Liaisons explicites de type convoyeur sur un même niveau. Les raccords natifs utilisent les vrais ports, choisissent les sorties libres du répartiteur et les entrées libres du fusionneur, et identifient les ingrédients des assembleurs par leur provenance. Les six niveaux de convoyeurs suivent la capacité choisie dans l’atelier, 120/min par défaut.
- Câbles explicites entre poteaux et machines, avec limites des prises et longueur maximale de 100 m. Les liens « Relier l’électricité » deviennent donc des câbles natifs s’ils respectent ces limites.

Les repères d’entrée/sortie restent des annotations. Les objets du tampon restent hors du blueprint. Ces exclusions sont signalées dans le résultat ; les bâtiments physiques et liens non pris en charge ne sont jamais supprimés silencieusement pour fabriquer un export partiel.

## Contrôles et limites actuelles

Les enveloppes de l’atelier étant provisoires, l’export vérifie les dimensions de dégagement du jeu : emprise, hauteur, chevauchements, présence et traversée des sols. Une machine placée sur un étage doit reposer sur sa surface. Les fonderies et constructeurs dépassent notamment les anciennes enveloppes de 6 m utilisées par le planificateur.

Le routeur cherche des polylignes cardinales parmi un ensemble borné de couloirs, les arrondit avec des quarts de cercle de rayon nominal 2 m puis construit les splines natives. Il contrôle les directions des ports, les obstacles et les bandes déjà routées, à intervalles de 25 cm maximum pour les lignes droites. Des tunnels d’accès strictement alignés sont autorisés devant les ports situés dans l’enveloppe de leur propre machine. Le stockage des obstacles et des bandes est indexé pour borner le coût des recherches.

Ce n’est pas une recherche exhaustive de tous les chemins possibles : un échec indique que ce routeur n’a pas trouvé de trajet, pas une preuve d’impossibilité. L’ordre des liaisons peut influencer les chemins disponibles. Les maillages, animations et collisions fines du moteur ne sont pas simulés.

Restent bloqués explicitement :

- Réseau pointillé `planned` du calculateur : liens logiques à remplacer par des convoyeurs explicites avant export.
- Élévateurs réservés : absence de définition de deux extrémités et du sens de circulation dans le modèle de l’atelier. Le gabarit vertical des tests fixes ne suffit pas à déduire une connexion personnalisée.
- Liaisons entre niveaux, ports saturés, ingrédients ambigus d’un assembleur, trajets impossibles pour ce routeur, débits déclarés supérieurs à la capacité choisie, matières/épaisseurs ou recettes non compatibles.

Le formulaire affiche les erreurs groupées et n’écrit aucun blueprint dans ces cas. Les machines sans câble sont exportables avec un avertissement de branchement manuel ; exporter un bâtiment isolé reste utile et ne prétend pas livrer une ligne autonome.

## Tests

`tests/check_native_project.py` vérifie le projet personnalisé, les trois formats, les trois matières de sols, les six convoyeurs, les recettes et horloges, les couleurs, le tampon, les câbles, un virage à 90°, un répartiteur avec deux sorties physiques distinctes, l’écriture/relecture binaire, les noms stables, les sauvegardes et le refus de remplacer un fichier extérieur. Il injecte des erreurs de hauteur, dimensions, recette, débit, réseau logique, gaine et coordonnées non finies.

`tests/check_native_project_api.py` démarre un vrai serveur HTTP temporaire avec le dossier natif redirigé vers un dossier de test. Il couvre la réponse positive, les erreurs structurées 422, le refus sans en-tête local et la protection du chemin de session. Aucun fichier de jeu personnel n’est utilisé par ces tests.

Les quatre modules natifs précédents et les tests JS du modèle et de l’assistance passent aussi après intégration. Le navigateur Chrome est utilisé pour vérifier le bouton et les messages, puis pour exporter un projet de validation dans SANDBOX depuis un brouillon de secours distinct du brouillon utilisateur.

Sources ajoutées : `native_project.py`, métadonnées `data/native-assets.json` issues de CommunityResources/Docs du build installé et des chemins observés dans les gabarits locaux, endpoint serveur et bouton de l’atelier. Les sauvegardes du monde et la base des usines de l’explorateur ne sont pas modifiées.
