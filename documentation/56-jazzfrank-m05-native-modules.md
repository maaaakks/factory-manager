# M05 · Entrepôt modulaire — modules de JazzFrank

## Changement

Une catégorie **M05 · Entrepôt modulaire** apparaît en premier dans Design → Façades. Elle est distincte de l’ancienne famille « Entrepôt modulaire », qui reste une création indépendante dans Industrie.

Cette catégorie assemble les pièces réellement présentes dans les blueprints publics de [JazzFrank](https://satisfactoryblueprints.com/author/jazzfrank). Les douze sources C1/C2, M1–M6, IN1/IN2 et IC1/IC2 ont été téléchargées et analysées : **3 509 acteurs**. Fichiers originaux, auteurs, identifiants et SHA-256 sont conservés dans `external-tool/data/m05/manifest.json` et les fichiers `.sbp` voisins.

La génération automatique utilise actuellement **C1/C2, M1–M6 et IN1**. IC1/IC2 et IN2 sont conservés pour étude, sans être ajoutés automatiquement : les angles rentrants et l’ascenseur nécessitent une intégration supplémentaire.

## Assemblage

- Trame réelle de **40 × 40 m**, sans étirement ni réduction des modules.
- Quatre angles orientés correctement ; façades intermédiaires complémentaires sur les faces opposées ; modules IN1 pour remplir le toit intérieur.
- Six compositions déterministes et symétriques. Les variantes changent les modules C/M, pas seulement une palette.
- Les coursives, garde-corps, poutres, ventilateurs, fenêtres, portes, auvents et décrochements proviennent des positions et orientations sources.
- Terrain minimum : **80 × 80 m**, hauteur disponible d’au moins 40 m. L’application réserve au moins 48 m de hauteur lors de l’adaptation. À 80 × 80 m, seuls les quatre angles sont nécessaires ; les façades M apparaissent lorsqu’un axe atteint 120 m, IN1 à partir de 120 × 120 m.
- Sur les dimensions non multiples de 40, l’assemblage est centré et laisse le reliquat en marge. Limite actuelle : 64 modules pour contenir le coût du rendu.
- Une bande périphérique de 24 m est réservée aux modules. La chaîne de production est centrée et le terrain agrandi lors de l’application du style ; opération annulable. Les sols du projet restent dans le cœur utile, sans doubler les plateformes de façade.
- Le volume utile de production est limité à **30,6 m**, sous les poutres et coursives hautes des modules originaux. Une chaîne plus haute est refusée explicitement.

Dans le calculateur, choisir M05 adapte aussi le nouveau plan avant son ouverture. Les autres styles et les projets existants conservent leur comportement.

## Aperçu et export

Le navigateur n’a pas les modèles Unreal du jeu. L’aperçu utilise donc des géométries schématiques détaillées : profils de poutres, ossatures et diagonales de verre, disques de ventilation, garde-corps, marches et pentes. **Les classes, positions, quaternions et propriétés exportés sont ceux des sources natives**, et non ces maillages de substitution. L’aperçu utilise une palette représentative orange/anthracite ; l’export conserve les personnalisations des sources, dont le rendu peut dépendre des nuanciers du jeu.

Les acteurs et leurs composants sont clonés avec des identifiants uniques. Les références externes à la source sont nettoyées. Les câbles internes des modules sont reconstruits à leurs extrémités mesurées ; ils restent indépendants de l’alimentation des machines. La vérification compare leurs ports à la géométrie source, vérifie les références réciproques et la capacité de chaque connexion, y compris les raccords muraux doubles.

La vue opaque utilise le cache GPU ; les milliers de faces M05 n’exigent plus des milliers de nœuds SVG temporaires. Les bornes de la scène sont calculées sans expansion d’un grand tableau dans `Math.min`/`Math.max`, qui provoquait un dépassement de pile. Sans GPU, un rendu logiciel borné remplace le partitionnement récursif sur les grandes scènes.

## Vérification

- Suite JavaScript existante et nouveau test M05 : compositions, symétrie, poses finies, erreurs de dimensions, marge, adaptation sans mutation et persistance.
- Parité JavaScript/Python des poses, assemblages et sols ; empreintes des douze sources.
- Six compositions natives sur **120 minerais/min → 10 plaques renforcées/min**, conservant **54 convoyeurs, 21 élévateurs et 24 câbles de production**.
- Export/relecture binaire et vérification des ports pour chaque composition ; rejet d’un câble décoratif déplacé artificiellement.
- Régression des familles précédentes, dimensions libres et chaîne compacte native.
- Vérification depuis l’interface via le bouton de prévisualisation native, sans écriture dans le dossier du jeu.

**Limites :** compositions actuellement rectangulaires sur la trame des modules, bien que leurs façades et volumes soient en relief ; pas encore d’angles rentrants automatiques, d’ascenseur IN2 ou d’empilage de modules en hauteur. Les formats XL et les dégagements réels doivent encore être validés en jeu. Aucun test n’a modifié une sauvegarde ou installé un blueprint dans le jeu.
