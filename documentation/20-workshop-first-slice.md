# Atelier 6 × 6 — première tranche livrée

19 octobre 2026. Accès local : `http://127.0.0.1:8765/atelier`, ou bouton « Atelier 6 × 6 » depuis l'explorateur.

## Fonctions disponibles

- Plan 48 × 48 m représentant six fondations de 8 m par côté, graduations et grille de placement de 1 m.
- Palette : fonderie, constructeur, assembleuse, coffre et poteau.
- Pose par choix dans la palette puis clic dans le plan ; sélection et déplacement par glisser-déposer.
- Rotation par quarts de tour, duplication avec recherche d'une place libre et suppression.
- Propriétés éditables : nom, centre X/Y, largeur, profondeur et orientation.
- Refus des emprises qui sortent du cadre ou chevauchent une autre emprise. Les bords peuvent se toucher.
- Annuler/rétablir, jusqu'à 100 modifications dans la session.
- Projet nommé enregistré dans le navigateur, brouillon conservé automatiquement, liste des projets et restauration après rechargement.
- Export/import du projet JSON de l'atelier. Ce format n'est pas un blueprint natif `.sbp`.

## Utilisation

1. Choisir une machine dans la palette et cliquer sur le plan. La pose reste active pour répéter le même objet.
2. Revenir en sélection avec Échap ou « Sélectionner / déplacer ».
3. Glisser un objet ou modifier ses coordonnées à droite, puis appliquer les propriétés.
4. Utiliser R pour tourner, D pour dupliquer, Suppr pour effacer ; les boutons donnent les mêmes actions.
5. Nommer et enregistrer. Exporter un JSON pour conserver un fichier indépendant du navigateur.

R tourne l'objet en sélection, ou la prochaine pose lorsque la palette est active. Le bouton de rotation des propriétés agit sur l'objet sélectionné. Ctrl+Z annule ; Ctrl+Y ou Ctrl+Maj+Z rétablit ; Ctrl+S enregistre.

## Données et limites

Les empreintes de départ sont provisoires et indiquées comme telles dans la palette ; elles sont modifiables. La validation porte sur ces rectangles et le cadre du plan, pas sur les collisions exactes du jeu ou les dégagements de maintenance. Le pourcentage d'emprise représente l'aire des objets divisée par celle du plan ; ce n'est pas un score d'optimisation.

Les convoyeurs, câbles, ports, recettes, débits, niveaux et export natif restent les tranches suivantes. Le présent outil permet de poser et manipuler les objets sur papier ; aucune liaison fonctionnelle n'est encore créée.

Les données navigateur sont propres à cette origine et à ce profil. Elles peuvent disparaître si le stockage du navigateur est effacé ; le JSON constitue la copie transportable. Les clés utilisées sont `factoryTools.workshop.library.v1` et `factoryTools.workshop.draft.v1`. La bibliothèque est enregistrée explicitement ; l'historique annuler/rétablir ne survit pas au rechargement.

Le JSON est limité à 1 Mo à l'import, à 300 objets et au schéma Atelier version 1. Les valeurs incohérentes, identifiants dupliqués, types inconnus et emprises invalides sont refusés avant de remplacer le projet. Les projets et les sauvegardes du jeu restent des données distinctes.

## Vérifications effectuées

`node tests/check_workshop.cjs` : limites du cadre, chevauchements, bords adjacents, rotation modifiant l'emprise, copie à une place valide, relecture JSON et rejet de données incompatibles.

Dans l'interface :

- Pose d'une fonderie, d'un constructeur, d'une copie, d'un coffre et d'un poteau.
- Rotation à 90° ; duplication, annulation, rétablissement, suppression et restauration.
- Glisser-déposer de la copie de (18,16) vers (36,12).
- Pose de coffre chevauchant un constructeur refusée ; modification hors du cadre refusée.
- Enregistrement « Essai cuivre — atelier 6×6 » ; restauration des cinq objets après rechargement.
- Nouveau plan vide puis ouverture du projet enregistré.
- Export du fichier JSON par l'interface puis réimport du fichier dans un plan vide, avec conservation des cinq objets et de leurs transformations.

Ces vérifications concernent uniquement le créateur sur plan. Aucun chargement dans le jeu n'a été réalisé ou requis.

## Organisation du code

- `dist/workshop.html`, `workshop.css`, `workshop.js` : interface autonome servie par le serveur local existant.
- `dist/workshop-model.js` : géométrie et validation du modèle, partageables avec les tests Node.
- `tests/check_workshop.cjs` : tests du modèle ; Node n'est requis que pour les tests, pas pour utiliser l'atelier.

Prochaine tranche : déclarer des ports sur les objets supportés et tracer un premier convoyeur logique entre une sortie et une entrée, avec comportement défini lors des déplacements.
