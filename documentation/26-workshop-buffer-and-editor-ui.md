# Atelier : tampon, prise d’objets et interface centrée sur le plan

## Organisation

La barre de document comporte Nouveau (+), un menu Importer / Exporter, le nom du blueprint immédiatement avant Enregistrer, puis Mes projets en haut à droite. Les projets restent locaux au navigateur et les anciens projets restent lisibles.

Les gestes utiles apparaissent dans une infobulle intégrée à l’app au survol ou au focus de l’icône (i). La palette gauche est consacrée aux objets, regroupés en Transformation, Logistique et Électricité. La commande de liaison électrique reste dans ce groupe.

Les entrées et sorties sont au-dessus du plan. « Modifier l’objectif » permet d’ajouter/modifier les débits, puis « Calculer et placer » calcule les recettes, les cadences et le placement avec les recettes standard prises en charge. Le remplacement d’un plan existant demande une confirmation intégrée à l’app ; il conserve le tampon. Cette action explicite évite de détruire un arrangement manuel à chaque frappe d’un débit.

Le panneau droit se limite à la sélection, aux actions rapides, au réglage manuel facultatif des recettes et aux sections repliées de structure/raccordements. Position, taille, orientation et altitude ne sont plus des champs visibles. Les anciennes valeurs des projets sont conservées. R pilote l’orientation ; l’étage se choisit sur le plan. Le bloc Vérification du plan est retiré de la vue ; les refus géométriques continuent à s’appliquer.

## Prise, rotation et dépôt

Glisser une sélection la prend en main : les originaux et leurs liaisons disparaissent temporairement de l’affichage. L’aperçu représente la sélection transportée. Les données du projet ne changent qu’au dépôt valide.

R tourne les objets pris de 90° autour du centre du groupe. La rotation n’est pas bloquée pendant la prise ; le dépôt effectue ensuite les vérifications de cadre, de chevauchement et de plancher. Les positions originales sont retirées de cette vérification pour éviter une collision avec soi-même. R fonctionne aussi sur la sélection au repos ; pour un groupe, la rotation est atomique.

Échap annule la prise et restitue l’état original. Un dépôt invalide conserve les objets à leur origine ou dans le tampon. Un dépôt dans le blueprint replace les objets ; un dépôt hors du blueprint ET hors du tampon les supprime. La suppression reste annulable avec Ctrl+Z.

## Tampon

La zone Tampon est située à côté du plan, physiquement hors du volume du blueprint. Le dépôt y conserve les objets, recettes, dimensions et rotations, et détache leurs liaisons. Une carte peut être glissée du tampon vers le plan ; elle prend comme base le niveau affiché. Les objets d’un groupe stocké sont présentés individuellement.

Le tampon est conservé dans le brouillon, les projets enregistrés et les exports JSON, par un tableau buffer optionnel du format v2. Les anciennes versions sans ce champ sont lues avec un tampon vide. La limite de 300 objets inclut le plan et le tampon. Les identifiants doivent être uniques entre les deux.

Les objets du tampon ne participent pas aux collisions ou à l’emprise du blueprint. Un recalcul de placement génère des identifiants distincts pour ne pas entrer en conflit avec des objets mis de côté. Une nouvelle génération conserve le tampon du projet courant ; Nouveau ou l’ouverture d’un autre projet remplace l’ensemble après protection du brouillon.

## Messages

Les notifications sont des cartes dans le thème de l’app. Elles ne masquent pas les commandes du haut et restent limitées à un message à la fois. Une modification propose Annuler ; Ctrl+Z reste disponible après disparition du message. Les confirmations utilisent un dialogue HTML stylé, avec Annuler/Continuer et fermeture par Échap. Aucune fenêtre native confirm() n’est utilisée dans l’atelier. Les erreurs de débit et de propriétés passent par les notifications plutôt que les bulles natives de validation de formulaire.

## Validation

Tests de modèle : transfert au tampon, détachement des liaisons, sauvegarde/relecture JSON, retour atomique, refus sans perte, rotation d’un groupe en main, absence de collision avec l’ancienne position, suppression du tampon, identifiants dupliqués et import ancien. Suites existantes atelier, sélection, implantation, formats, assistance et calculateur réussies.

Dans le navigateur : dépôt d’une fonderie du plan de référence dans le tampon, retour au plan puis annulation des deux opérations pour rétablir ses liaisons et coordonnées ; suppression d’un constructeur hors cadre et annulation ; rotation puis stockage d’un constructeur à 90°, sauvegarde et rechargement ; refus d’un dépôt sur une fonderie en gardant l’objet stocké, puis retour sur une place libre ; confirmations intégrées annulées et acceptées ; objectif central 10 plaques renforcées/min donnant 14 machines sur 4 étages ; recalcul avec un tampon rempli, conservé après sauvegarde/rechargement. Les transformations pendant une prise sont couvertes par les tests de modèle ; la séquence souris maintenue + R n’a pas fait l’objet d’un test navigateur automatisé dans cette passe.

Les liaisons proposées restent un réseau logique et des réservations : cette refonte ne fournit pas la validation physique des courbes, élévateurs et raccords du jeu.
