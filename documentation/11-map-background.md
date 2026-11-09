# Fonds de carte — 18 octobre 2026

Le sélecteur « Fond » de la barre de carte permet de passer de « Grille sombre » à « Carte du monde » sans recharger la sauvegarde. Les deux vues utilisent le même repère, le même zoom, la même sélection et les mêmes filtres. Le choix du fond est mémorisé localement par le navigateur ; les navigateurs qui bloquent le stockage gardent la fonctionnalité sans persistance.

Le raster 5000 × 5000 (environ 2,1 Mo) est installé dans `external-tool/dist/assets/world-map.jpg` et servi par le serveur local. Il n'y a pas de requête vers le wiki pendant l'utilisation. Le serveur autorise explicitement cette seule ressource supplémentaire, sans exposer les autres fichiers du projet.

Provenance : https://satisfactory.wiki.gg/images/Map.jpg . Documentation et attribution distinctes de la licence du code : `external-tool/dist/assets/README.md`. Les coordonnées géoréférencées de l'image entière sont décrites dans ce fichier. Le fond aide au repérage ; il n'ajoute pas un modèle de terrain/collision ou d'altitude au calculateur.

Vérification : image locale décodée et inspectée ; JavaScript vérifié par Node --check ; carte réellement chargée sous les 2 098 constructions de la sauvegarde de test dans le navigateur. Bascule carte → grille après sélection d'un convoyeur : fiche identique et échelle affichée identique. Aucun changement de coordonnées d'objet n'est effectué par le changement de fond.
