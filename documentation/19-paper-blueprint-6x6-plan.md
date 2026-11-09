# Créateur sur plan — 6 × 6 fondations

19 octobre 2026. Périmètre actuel : obtenir un projet propre dans notre éditeur, sans condition de chargement ou de placement dans Satisfactory. Cette priorité remplace le verrou d'export/validation en jeu du document 18 pour la première version.

## Gabarit de départ

Interprétation retenue : **6 × 6 fondations de 8 m**, soit **48 × 48 m**, sur un niveau. Les six cases par côté et les dimensions en mètres sont affichées. Le déplacement peut utiliser une grille plus fine que les fondations ; une machine n'est pas limitée au centre d'une case. Le gabarit est un réglage du projet, pas une dépendance à un Designer ou à sa progression en jeu.

## Première version utile

1. **Scène vide** : grille 6 × 6, sauvegarde/réouverture du projet local, annuler/rétablir.
2. **Placement** : palette courte de machines, coffres et poteaux ; déplacer, tourner de 90°, dupliquer, supprimer.
3. **Raccords** : choisir une sortie puis une entrée ; convoyeur d'abord droit, puis trajet orthogonal simple. Câbles électriques entre connecteurs compatibles.
4. **Vérification sur plan** : objets dans le gabarit, absence de chevauchement interdit dans notre modèle, ports occupés/compatibles, cohérence de recette et bilans de débit avec les capacités connues.
5. **Lisibilité** : vue de dessus principale ; aperçus et propriétés simples ; afficher où se trouve un problème et permettre de le corriger.

Le projet est d'abord enregistré dans notre format JSON. Lecture de blueprints existants, export `.sbp`, validation dans le jeu, fusion et génération de dispositions sont des étapes ultérieures. Aucun de ces sujets ne bloque la première scène éditable.

## Ce que signifie « propre sur papier »

- Les positions, rotations, dimensions et liaisons sont enregistrées de façon déterministe.
- Les objets et références restent cohérents après déplacement, duplication, suppression et annulation.
- Un lien reste attaché aux ports après déplacement ; si son trajet devient invalide, il est signalé plutôt que conservé comme raccord valide.
- Les distances et empreintes utilisées sont explicites ; les dégagements peuvent être représentés séparément de l'emprise au sol.
- Le calcul distingue capacité théorique, besoin de recette et flux non affecté. Une ligne dessinée n'est pas un débit observé.
- La validation porte sur les règles supportées par notre modèle. Les dimensions et ports encore schématiques restent identifiés comme tels ; ils ne sont pas présentés comme une preuve de constructibilité dans le jeu.

Les messages restent compacts : objet hors zone, chevauchement, port occupé, raccord incompatible, débit insuffisant. Les détails sont consultables sur l'objet concerné.

## Premier scénario d'essai

Sur la grille vide : poser deux machines, les tourner, les raccorder par convoyeur, ajouter un poteau et leurs câbles, enregistrer puis rouvrir le projet. Vérifier ensuite les corrections après déplacement, duplication et suppression. Le scénario réussit dans l'éditeur ; il ne demande pas d'ouvrir le jeu.

## Première tranche à développer

**Une grille 6 × 6 éditable avec quelques objets, sélection, déplacement, rotation et sauvegarde locale.** Les convoyeurs et les câbles viennent ensuite en petites tranches. La lecture/réécriture du format natif ne précède plus le placement manuel.
