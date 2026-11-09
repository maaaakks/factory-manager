# Toits composés et recherche du terrain minimal

## Comportement

- Le kit procédural M05 retrouve quatre compositions natives : lanterneau panoramique, verrière à double pente, sheds industriels et pavillon technique. « Rafraîchir le toit » alterne ces compositions puis leur orientation.
- Une composition repose sur une ou deux cellules de toiture adjacentes, avec des poteaux et traverses continus. Les façades flottantes ne sont pas réintroduites.
- Les anneaux périphériques répétés sont supprimés. Si la place ou la hauteur manquent, le toit conserve ses verrières et au maximum une ventilation discrète.
- La recherche Auto essaie les petites emprises avant la taille du projet ouvert. Réorganiser un projet 7×7 peut donc réellement le réduire.
- La réserve d’habillage reste distincte de l’espacement des machines. Compact conserve ses espacements compacts même lorsque cette réserve est cochée. Un terrain imposé reste une contrainte stricte.

## Cas vérifié

60 minerais de fer/min → 5 plaques renforcées/min, recettes standard, Compact et Bas : huit machines sur un seul étage. Placement trouvé en **5×5 sans réserve** et **6×6 avec réserve et façades complètes**, à partir d’un projet 7×7. Les dimensions de placement des fonderies et assembleurs suivent désormais leur encombrement natif. Les entrées et sorties sont conservées.

Ces résultats valident le placement et son réseau schématique. **L’export natif du nouveau placement dense sur un étage reste bloqué sur certains raccords par le routeur de convoyeurs.** Aucun contrôle de collision n’a été désactivé ; le refus d’export reste explicite. Les profils compacts natifs étagés existants constituent un chemin distinct.

## Vérifications

- Suite JavaScript : 39 contrôles ; placement, conservation du projet initial, réserves, terrain imposé, géométrie des toits et appuis.
- Quatre compositions avec toit actif/inactif : huit cas, parité JavaScript/Python, construction native et relecture des fichiers SBP dans des dossiers temporaires.
- Façades et profils natifs existants : contrôles de construction et relecture ; aucun fichier écrit dans les dossiers du jeu.
- Contrôle visuel du plan 6×6 dans un onglet local de test. Aucun remplacement du projet ouvert dans le navigateur de l’utilisateur. Aucune validation en jeu de ces nouveaux toits.

## Utilisation

Recharger l’application, puis utiliser **Réorganiser** avec Terrain Auto pour recalculer la taille. Rafraîchir le toit change uniquement l’habillage. Les projets existants ne sont pas réorganisés automatiquement au rechargement.
