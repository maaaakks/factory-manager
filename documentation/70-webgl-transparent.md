# WebGL pour les deux modes de la vue 3D

L’atelier utilise désormais `PreviewGPU` pour le mode transparent comme pour le mode opaque, dans Design et dans la fenêtre 3D. Le visualiseur de l’explorateur garde son utilisation existante du même moteur, opaque par défaut.

- Opaque : profondeur matérielle, faces cachées masquées.
- Transparent : mélange alpha, profondeur désactivée pour conserver une lecture rayon X de l’intérieur ; faces, arêtes, éléments logistiques et détails M05 sont pris en charge. Ce rendu schématique ne prétend pas calculer une transparence physiquement réaliste.
- Les opacités des sols, machines, vitrages, détails et lignes sont conservées dans les couleurs des sommets GPU.
- Une scène est envoyée au GPU lors d’un changement du projet, du thème, des calques ou du mode. Les rotations et le zoom mettent ensuite à jour la projection ; ils ne recréent pas la géométrie SVG.
- Le cache distingue opaque et transparent : changer de mode ne réutilise pas les mauvaises opacités. Les états de profondeur et de mélange sont rétablis à chaque dessin.
- Si WebGL est indisponible, le transparent garde le SVG existant et l’opaque son rendu de secours.

Vérification : 41 contrôles JavaScript réussis, dont un nouveau test des opacités, des deux modes, du cache pendant les mouvements et du repli sans WebGL. Dans le navigateur de test, le rendu est identifié comme `webgl` dans les deux modes. Sur une scène avec habillage M05, rotation et zoom n’augmentent pas le nombre d’envois de géométrie. Vérification visuelle de la visibilité intérieure et du changement de mode.

Aucune mesure de FPS réalisée sur le navigateur de l’utilisateur. Aucune modification du projet ouvert ou des fichiers du jeu. Recharger l’application suffit à charger cette amélioration de rendu ; aucun recalcul du blueprint nécessaire.
