# Formats et retour à la sélection

Formats de travail disponibles : 4 × 4 (32 × 32 × 32 m), 5 × 5 (40 × 40 × 40 m), 6 × 6 (48 × 48 × 48 m). Le sélecteur est dans la barre du plan. Ces volumes servent à la conception sur plan ; aucune validation native en jeu n’est ajoutée.

Le changement conserve les positions, orientations, recettes et débits. Une réduction est bloquée si une enveloppe dépasse en X, Y ou Z. Un bandeau indique les objets concernés ; le format courant reste sélectionné et aucun objet n’est supprimé. Les contacts exacts avec la limite sont permis. Agrandissement et réduction acceptés peuvent être annulés avec Ctrl+Z.

Grille, graduations, cadrage, étages, emprise, routage et génération assistée prennent en compte le format courant. Un calcul qui ne tient pas échoue sans remplacer le plan. Le format est conservé dans les projets et exports JSON ; les anciens projets de 48 m restent compatibles.

Un clic dans la marge extérieure du blueprint quitte le mode de pose et revient à Sélectionner / déplacer. F ou Échap fait la même chose ; F ne s’applique pas pendant la saisie dans un champ. Aucun objet n’est posé par ce clic extérieur.

Vérifications : tests du modèle de débordement XYZ, refus sans mutation, limites exactes, sauvegarde JSON, génération selon le volume. Dans le navigateur : refus du passage du cuivre de 6×6 à 4×4 avec les noms des trois objets en débordement ; format 4×4 valide, pose d’une fonderie, conservation après sauvegarde/rechargement ; retour à la sélection par F et par clic dans la marge, sans ajout d’objet. Les tests existants de l’atelier et des assistants passent.
