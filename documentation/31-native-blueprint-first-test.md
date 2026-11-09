# Premier export natif pour test en jeu

19 octobre 2026.

## Fichier prêt

Nom : `FT_TEST_01_Fonderie`. Destination autorisée : `C:/Users/YOUR_USER/AppData/Local/FactoryGame/Saved/SaveGames/blueprints/SANDBOX/`.

Deux fichiers sont écrits directement dans ce dossier : `.sbp` (module natif) et `.sbpcfg` (description et icône). Le nom de session SANDBOX a été confirmé par lecture de l’en-tête de `SANDBOX_autosave_1.sav` (build 513885). Aucun fichier de sauvegarde `.sav` n’est modifié.

Contenu fixe : deux fondations de 1 m, côte à côte, et une fonderie centrée dessus. Recette lingots de fer, cadence par défaut 100 %, inventaires vides. Sans convoyeur ni câble : brancher l’électricité et fournir le minerai manuellement pour le premier essai. Résultat attendu selon la recette standard : 30 minerais de fer/min → 30 lingots/min, 4 MW en fonctionnement. Ce débit doit être vérifié en jeu.

## Utilisation

Dans SANDBOX, quitter au menu puis recharger la partie après l’écriture. Chercher `FT_TEST_01_Fonderie` dans les blueprints, éventuellement dans la catégorie non définie. Vérifier d’abord l’aperçu et le placement des deux fondations et de la fonderie. Après placement, vérifier la recette et la cadence, brancher le courant, fournir du minerai puis observer la production.

Les blueprints PC sont rangés par session sous un dossier racine commun. Le dossier existant nommé Global ne suffit pas à prouver que le jeu le traite comme une bibliothèque commune. La destination de ce premier essai est SANDBOX, choisie par l’utilisateur. Référence : [Blueprint, wiki officiel](https://satisfactory.wiki.gg/wiki/Blueprint).

## Interface et périmètre

Dans « Importer / Exporter », la section « Premier test dans le jeu » sélectionne une session et propose « Enregistrer le test dans le jeu (.sbp) ». L’écriture est directe et automatique à cet emplacement lors du clic, sans téléchargement à déplacer. Il ne s’agit pas d’un enregistrement périodique, ni de l’export natif du plan courant : seul ce petit module fixe est pris en charge à ce stade. Le JSON de l’atelier demeure séparé.

L’API locale `GET /api/blueprints` expose les destinations et le module ; `POST /api/blueprints/test` exige le même contrôle Host/Origin et l’en-tête local que les autres écritures de l’application. Aucune destination arbitraire n’est acceptée. SANDBOX peut être créé ; les autres choix doivent déjà exister sous le dossier des blueprints. Les noms traversant un dossier et les liens symboliques vers l’extérieur sont refusés. Les fichiers de test existants sont copiés dans `external-tool/data/native-backups/` avant remplacement. Les autres blueprints sont conservés.

## Construction et limites

L’export utilise le parseur/écrivain GPL-3.0 [GreyHak/sat_sav_parse](https://github.com/GreyHak/sat_sav_parse), déjà présent dans le projet. Les gabarits natifs proviennent d’acteurs isolés de blueprints vanilla locaux de l’utilisateur : une fonderie et une fondation. Les liaisons externes sont retirées, les identifiants et références internes sont régénérés. Les coordonnées sont en centimètres : fondations à Z=50 (surface à Z=100), fonderie à Z=100. L’emprise tient dans un designer 4×4. Le format de sérialisation du gabarit est conservé (version de sauvegarde 52), sans prétendre convertir son en-tête en format plus récent.

Les deux fichiers sont générés en temporaire puis relus avant publication. La validation contrôle trois acteurs, huit composants, unicité et résolution des références, absence de câbles et configuration native lisible. Le parseur relit également les fichiers réellement déposés dans SANDBOX. Le reçu `31-native-test-receipt.json` conserve les tailles et empreintes à la sortie.

Tests : `tests/check_native_blueprint.py` (écriture/relecture native, références, chemins, rejet de cible inconnue) et `tests/check_foundation.py` réussis. L’écriture directe a été exécutée depuis Chrome et confirmée sur disque. **La présence, le placement et le fonctionnement dans le moteur du jeu restent à vérifier par l’utilisateur.**
