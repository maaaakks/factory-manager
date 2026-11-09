# Test natif 02 : chaîne de plaques de fer

19 octobre 2026.

Le premier module `FT_TEST_01_Fonderie` fonctionne selon le retour de l’utilisateur. Le second ajoute transport et alimentation électrique interne. Les fichiers `.sbp` et `.sbpcfg` sont enregistrés dans le même dossier `SaveGames/blueprints/SANDBOX`, sous le nom `FT_TEST_02_PlaquesFer`. Le test 01 reste présent.

## Contenu et essai en jeu

- Huit fondations standard de 1 m : plateforme de 16 × 32 m, compatible avec le volume du designer 4×4.
- Une fonderie de lingots de fer à 100 %.
- Un convoyeur Mk.1 droit relié à la sortie de la fonderie et à l’entrée du constructeur.
- Un constructeur de plaques de fer à 100 %.
- Un poteau Mk.1 et deux câbles internes, un vers chaque machine ; deux connexions du poteau restent libres.

Après rechargement de SANDBOX, chercher `FT_TEST_02_PlaquesFer` dans les blueprints, éventuellement en catégorie non définie. Le placer, raccorder le poteau au réseau et alimenter la fonderie en minerai, manuellement ou par convoyeur externe. Les plaques s’accumulent dans le constructeur : il n’y a pas encore de coffre ni de convoyeur de sortie. Retirer les plaques lorsque l’inventaire se remplit.

Débit théorique standard : **30 minerais de fer/min → 30 lingots/min → 20 plaques/min**, pour **8 MW en fonctionnement**. La conformité du transport et de l’alimentation doit encore être constatée dans le jeu. Un apport manuel intermittent ne permet pas de conclure à un fonctionnement stable à 100 % ; alimenter en continu pour mesurer le débit stabilisé.

## Construction native

Le module est assemblé à partir d’acteurs vanilla isolés des fichiers locaux : fonderie du test 01, constructeur configuré en plaques, convoyeur Mk.1, poteau, câbles et fondations. Les connexions d’origine sont supprimées, puis les identifiants et références internes sont régénérés. Les inventaires sont vides.

Les offsets des ports sont mesurés à partir des extrémités de convoyeurs déjà connectés et des coordonnées relatives de câbles dans les blueprints locaux. Ce ne sont pas les ports schématiques de l’atelier.

Positions locales, en centimètres : fonderie `[0,-800,100]`, constructeur `[0,800,100]`, poteau `[-600,0,100]`. Les fondations ont leur centre à Z=50, donc leur surface à Z=100. La sortie de fonderie est à `[0,200,100]` relativement à son acteur ; l’entrée du constructeur à `[0,-300,100]`. Le convoyeur droit mesure ainsi 11 m entre ses deux ports. Les deux connexions sont réciproques dans les composants natifs.

Les câbles contiennent leurs références de bornes, les listes de fils de chaque composant, les coordonnées des extrémités et leurs coordonnées relatives au transform de l’acteur. Le cache de longueur correspond à la géométrie. La fonderie et le constructeur reçoivent chacun un câble provenant du poteau ; aucune référence à un bâtiment externe n’est conservée.

Le résumé du coût de construction comprend 41 bétons, 6 barres de fer, 11 fils électriques, 2 plaques renforcées, 10 câbles et 6 plaques de fer. Les recettes de construction viennent du catalogue local du jeu ; les longueurs et quantités des segments sont calculées pour ce module fixe.

## Interface et validation

« Importer / Exporter » propose désormais deux modules natifs de test. Le test 02 est sélectionné par défaut. La destination reste choisie par session. `POST /api/blueprints/test` accepte un identifiant de module dans une liste fermée, et garde le test 01 comme valeur compatible pour les anciens appels. Le plan courant de l’atelier n’est pas converti par ces commandes.

`tests/check_native_connected.py` vérifie la sérialisation/relecture, les 14 acteurs et 19 composants, les recettes, les connexions convoyeur réciproques, la coïncidence des extrémités avec les ports natifs mesurés, les bornes et caches de câbles. Des cas négatifs déplacent un endpoint de convoyeur ou de câble, cassent une référence réciproque et demandent un module inconnu : ils sont refusés. Les tests du premier export natif et du serveur restent réussis.

Le fichier a été écrit depuis l’interface Chrome, puis relu depuis le dossier SANDBOX. Le reçu `32-native-test02-receipt.json` décrit le fichier réellement publié et ses empreintes. **Ces contrôles ne remplacent pas le test de placement, de passage des lingots et d’alimentation dans le moteur du jeu.**
