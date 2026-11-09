# Orientation des murs et jauge d'équilibrage

18 octobre 2026 — prototype local.

## Murs

Le segment représente maintenant l'axe local Y transformé par le yaw enregistré, et non l'axe X. Vérification sur jojo : 1 335 paires de murs parallèles, à la même altitude et espacés de 8 m, sont alignées perpendiculairement à leur axe X. C'est une vérification de cohérence du plan de sauvegarde, pas une comparaison visuelle en jeu.

Le trait indique la largeur ; un petit repère indique la face locale +X lorsque le zoom est suffisant. Au survol, l'angle du trait est affiché. La fiche donne cet angle modulo 180° (0° vers la droite, 90° vertical) et la rotation +X modulo 360°. La sélection utilise désormais le segment de mur. Les variantes de largeur, pentes et formes restent schématiques ; le repère +X ne désigne pas nécessairement la face décorative de chaque modèle.

## Pourcentage visible

La carte d'usine affiche **Équilibrage des recettes** en haut de sa fiche, avec jauge et détail par produit intermédiaire. Pour chaque objet produit ET consommé par les recettes calculables du périmètre : `min(production, besoin) / max(production, besoin)`. Le score est la moyenne de ces ratios à poids égal, en pourcentage.

Exemple : 120 lingots/min produits et 120 consommés donnent 100 %. Produire 120 pour un besoin de 60, ou produire 60 pour un besoin de 120, donne 50 % pour cet intermédiaire. Matières premières uniquement consommées et produits finaux uniquement fabriqués sont exclus. Un export volontaire d'un intermédiaire peut abaisser le score : il faut alors interpréter le résultat selon les frontières choisies.

Le score est indisponible si des recettes ne sont pas calculables, des membres enregistrés ont disparu, ou aucun intermédiaire n'est calculable. Une cadence/bonus supposé ou un écart de version entraîne la mention « estimation provisoire ». Un 100 % ne valide ni les connexions, ni les capacités des convoyeurs, ni l'énergie, ni le débit réel, ni l'occupation de l'espace. Aucun score d'optimisation globale n'est annoncé.

Le secteur cuivre enregistré donne 100 % sur son unique intermédiaire : 120 lingots produits pour 120 consommés. Les 120 minerais entrants et 60 tôles sortantes figurent dans le bilan séparé, sous les hypothèses précédemment documentées.

## Vérification et prochaine tranche

`node tests/check_metrics.cjs` vérifie axes/endpoints de mur, équilibre parfait, sous-alimentation, surcapacité et absence de score avec recettes incomplètes. Le navigateur vérifie la jauge sur la partie réelle et la fiche d'un mur.

La prochaine tranche utile est un diagnostic des capacités des liaisons convoyeurs : charge requise par liaison, capacité disponible, première limitation identifiée et détail des hypothèses de répartition. Après validation des frontières et des routes, un indicateur séparé de capacité de chaîne pourra être ajouté. La compacité et l'usage vertical devront garder leurs propres mesures plutôt qu'être mélangés à ce premier pourcentage.
