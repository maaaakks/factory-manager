# Navigation dans l’aperçu 3D et commandes simplifiées

19 octobre 2026.

- Dans **Perspective**, glisser avec le bouton gauche pour tourner autour du blueprint ; la molette règle le zoom. L’inclinaison et le zoom sont bornés pour éviter les vues inversées ou perdues. Le bouton ↺ rétablit la vue initiale.
- La caméra utilise une projection orthographique centrée sur le volume du projet. Les gestes modifient seulement son état temporaire, sans toucher aux objets, recettes, connexions ou sauvegardes. Les déplacements de souris sont regroupés par trame et seule la perspective est redessinée pendant le mouvement. Les courbes physiques déjà calculées restent en cache.
- La perspective peut aussi recevoir le focus : flèches pour tourner, + / − pour zoomer, Home pour recentrer.
- **Face / Côté** sont deux boutons avec état actif visible, sans menu déroulant ni noms d’axes.
- Dans Calculator, **Entrée / Sortie** sont également deux boutons côte à côte. Modifier une ligne existante sélectionne son sens automatiquement.
- Un calcul et placement réussi ouvre directement la vue 3D et recentre sa caméra, aussi bien pour les modules compacts natifs que pour le placement logique classique. Une erreur ou une confirmation annulée ne l’ouvre pas.
- **Retour à l’atelier**, en bas de l’aperçu, ferme la fenêtre comme la croix. Échap reste disponible. Fermer annule également la prise souris et les rendus de caméra en attente.

Le passage d’un profil compact à un calcul classique retire les anciennes métadonnées natives : le nouveau plan logique ne conserve pas une fausse indication d’export physique calibré.

## Affichage opaque

La case **Éléments opaques**, au-dessus des deux vues, remplace les volumes transparents par des surfaces pleines légèrement ombrées. Décochée par défaut, elle agit uniquement sur l’aperçu et ne modifie ni le projet ni son export. Les planchers à ossature restent ouverts.

Les faces et les segments de convoyeurs/câbles sont découpés par plans dans l’espace puis affichés du fond vers l’avant. Les éléments derrière un volume sont ainsi masqués pendant la rotation ; les découpes de calcul n’ajoutent pas d’arêtes visibles.

Vérification Chrome sur l’exemple compact : transparence initiale, opacité des deux projections, retour à la transparence, Face / Côté, rotation et zoom au clavier. Aucun message d’erreur dans la console. Capture : `outputs/workshop-opaque-preview.png` dans l’espace de travail Codex.

Vérifications dans Chrome, session de secours séparée : rotation par glissement et zoom par molette confirmés par les coordonnées SVG ; changement Face / Côté et états actifs ; boutons Entrée / Sortie et modification de ligne ; ouverture automatique après calcul compact puis classique ; croix et Retour à l’atelier ; restauration de l’exemple compact enregistré. Aucun export vers le jeu pendant ces essais et brouillon habituel conservé. Contrôles existants des objectifs Auto et de la persistance des scènes natives réussis.
