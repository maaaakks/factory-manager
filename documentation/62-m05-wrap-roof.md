# 62 — M05 sur quatre faces et détails de toiture

Le kit M05 compose désormais les quatre orientations. La face principale conserve son couronnement et, sur les grandes façades, deux accents supplémentaires. Les trois autres faces recherchent d'abord un volume en retrait : verrière, portique ou galeries obliques. Leurs variantes sont coordonnées avec la graine du style. Si le volume manque, une charpente fine est essayée ; aucun élément n'est forcé dans la production.

L'emprise, les machines, les étages et les connexions restent identiques. Répliquer un motif ne rend pas sa profondeur gratuite : chaque face dispose de son propre contrôle XYZ, des machines, des entrées piétonnes, des trajets connus et des motifs déjà posés. Les faces secondaires ne créent pas de couronnements supplémentaires. Le relief reste dans les limites du projet.

## Toit

Les cellules horizontales pleines peuvent recevoir une ventilation native JazzFrank M3. Deux, trois ou quatre ventilations forment un groupe ; les grandes toitures peuvent en recevoir deux groupes espacés. Des arceaux en poutres peintes encadrent les ventilations. Les vitrages, pentes et volumes de façade existants sont protégés.

Les angles convexes reçoivent des corniches en quart de cercle à deux niveaux, avec montants. Chaque arc est constitué de six segments de poutres natives réglables : c'est un arrondi facetté, pas une nouvelle pièce courbe de mur. Le rayon et les groupes varient avec la graine du toit. La dalle et les murs sous la corniche conservent leur forme actuelle.

Les détails sont omis si la hauteur ou le support manque. Désactiver la toiture supprime aussi ces détails. Les boutons existants **Murs ↻** et **Toit ↻** suffisent ; aucune nouvelle option n'est ajoutée.

## Vérifications

Tests de composition sur quatre faces, limites XYZ, supports pleins, invariance de la production, déterminisme et variantes du toit. Parité exacte entre JavaScript et Python, construction et relecture de fichiers SBP en répertoire temporaire. Les poutres et ventilations sont exportées, pas seulement dessinées dans l'aperçu.

Le rendu reste schématique. Les enveloppes de collision décrites par l'outil ne remplacent pas une vérification dans le moteur du jeu. Cette version n'a pas encore été testée en jeu.
