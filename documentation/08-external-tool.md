# Nouvelle priorité : outil externe local

Décision du 18 octobre 2026 : commencer par l'analyse de sauvegardes avec une application locale, plutôt que le mod en jeu. Le chantier Unreal F00 est suspendu comme voie d'implémentation ; ses fichiers sont conservés. Le nouvel outil ne dépend ni d'Unreal, ni de Wwise, ni de SML.

## Première tranche livrable

`external-tool/` : serveur Python standard + interface HTML/CSS/JavaScript locale + parseur GreyHak GPL-3.0 figé. Pas de publication ni service externe. Ouvrir un fichier .sav, afficher les constructions, sélectionner un convoyeur, lire ses liens enregistrés, puis suivre un chemin de transport simple.

Le modèle commun reste réutilisable : objets, ports, connexions, sélection logique, géométrie et provenance. L'adaptateur de sauvegarde remplace l'adaptateur de lecture du jeu. Aucun débit réel déduit de l'instantané.

## Nouvel ordre

1. E01 : import local, carte schématique, inspection et liens physiques.
2. E02 : rendre les règles de direction/ports robustes sur de petites usines connues ; tests croisés avec le jeu.
3. E03 : sélectionner/éditer une ligne, définir les arrêts, persister la sélection hors du .sav.
4. E04 : enveloppe spatiale puis empreintes/étages avec données de dimensions validées.
5. E05 : recettes et production théorique/capacités avec catalogue lié à la version du jeu.
6. E06 : suggestions et aperçus d'agencement, convoyeurs et architecture.
7. E07 : envisager l'export d'une copie de sauvegarde uniquement après validation dédiée du round-trip ; aucun export dans E01.

## Expérience

Carte centrale, calques/recherche à gauche, fiche compacte à droite. Afficher le nom, la version et la date de la sauvegarde. Fenêtre d'attente pendant l'import ; message clair pour format invalide, fichier trop grand, sauvegarde sans bâtiment et lien non résolu. Les résultats représentent la sauvegarde choisie, pas la partie courante.

La dernière sauvegarde trouvée peut être vide ; ce n'est pas une erreur de lecture. Les sauvegardes plus anciennes peuvent contenir l'usine utile. Ne jamais mettre les .sav personnels dans Git.

## Preuves attendues

Parsing de deux versions de sauvegardes réelles, contrôle du hash avant/après, import d'un fichier invalide, vérification HTTP du serveur local et test de l'interface. La cohérence des connexions sauvegardées ne prouve pas encore le débit ni la fidélité visuelle des symboles/empreintes.
