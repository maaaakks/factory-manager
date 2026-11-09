# 61 — Façades principales M05, relief et charpente

Le kit ne se limite plus à varier les fenêtres d’une enveloppe tramée. Il compose une façade principale avec des pièces natives issues des blueprints JazzFrank, à leurs dimensions d’origine. Les autres faces peuvent rester sobres.

## Trois compositions

- **Verrière en proue · M3/M4** : deux travées vitrées de 8 m, retours latéraux, auvent incliné, montants et grandes diagonales. Elle privilégie une saillie lorsque le terrain le permet, puis un couronnement pour casser la ligne du toit.
- **Portique industriel · M2/M4** : véritable porte industrielle de 16 × 8 m provenant de M4, double auvent incliné, bandeau orange, ventilations et charpente oblique.
- **Galeries obliques · M5/M6** : vitrages verticaux sur plusieurs registres, deux auvents vitrés inclinés et ossature déportée. La profondeur des galeries se lit dans la façade.

La largeur de 16 m est obtenue par assemblage de deux panneaux natifs de 8 m. Les toits, vitrages et portes ne sont pas mis à l’échelle. Les poutres H utilisent le réglage natif de longueur ; les longues traverses sont fractionnées à 16 m maximum. Les pièces et leur attribution sont décrites dans `data/m05-facade-library.json`, généré à partir des sources conservées dans `data/m05/`.

Les grandes façades peuvent accueillir deux compositions latérales supplémentaires, espacées du motif principal. Elles ne sont ajoutées que si leurs volumes ne se chevauchent pas et ne touchent pas la production ou ses trajets. Il ne s’agit pas d’une répétition forcée sur toutes les faces.

## Placement et contraintes

Le générateur cherche une place devant l’enveloppe, un volume libre intégré à celle-ci, ou un couronnement dans la hauteur encore disponible. La verrière préfère le couronnement au retrait intérieur pour modifier aussi la silhouette du toit. Une toiture existante complètement comprise dans le nouveau volume peut être remplacée ; le générateur peut intégrer un lanterneau au nouveau couronnement plutôt que d’empiler deux toitures.

Les travées remplacées et leurs petits cadres sont retirés. Les murs fixes ne sont pas raccourcis artificiellement. Les membres traversant la zone sont conservés. Les fondations de production, les machines, les recettes et les connexions ne sont pas déplacées par le style.

Les limites XYZ du projet et les volumes des machines sont vérifiés. Les convoyeurs utilisent les trajets physiques disponibles, y compris les courbes natives échantillonnées, avec un dégagement conservateur. Si aucun volume ne convient, une **charpente compacte** peu profonde en poutres peintes remplace le grand motif. Si même cette charpente ne passe pas, aucun motif n’est forcé. Le format n’est pas agrandi et aucune marge décorative n’est réservée dans le placement compact.

La protection porte sur les volumes décrits par l’outil et sur les maillages schématiques des pièces. Ce n’est pas une garantie contre toutes les différences entre ces enveloppes et les collisions exactes du moteur du jeu.

## Atelier

Dans **Design → Façades → M05 · Kit procédural**, **Variante** et **Rafraîchir les murs** changent aussi la composition principale. Aucun nouveau grand panneau de réglages n’a été ajouté. L’orientation suit l’accès piéton explicitement choisi, ou la face avant en mode automatique. La vue initiale et son bouton de réinitialisation regardent cette face ; une rotation manuelle reste conservée pendant les changements de variante.

Les poutres ont désormais leur profil en H dans l’aperçu, au lieu d’être représentées comme des convoyeurs carrés de 1 m. La porte industrielle de M4 est visible dans l’aperçu des modules originaux également. L’aperçu ajuste son cadrage aux limites réelles des nouveaux volumes.

Les couleurs et les substitutions de matières compatibles sont appliquées aux acteurs sources clonés lors de l’export. La peinture des vitrages reste indépendante de celle des panneaux pleins, même lorsqu’un vitrage remplace un panneau dans le calcul de couverture de façade.

## Vérification

- 36 compositions : trois formats 4×4/5×5/6×6, trois motifs et quatre orientations. Pièces à taille native, limites XYZ, volumes occupés, peinture indépendante, limites des maillages et longueur des poutres contrôlés.
- Une grande façade reçoit trois compositions distinctes, sans chevauchement de leurs volumes réservés.
- Un cas sans profondeur ni hauteur libre revient à la charpente fine.
- Trois variantes sur la chaîne fonctionnelle 60 minerais/min → 5 plaques renforcées/min en 4×4 : objets de production et objectifs conservés, 54 convoyeurs et 21 élévateurs natifs inchangés.
- 41 scènes en parité JavaScript/Python ; 40 exports natifs et réouvertures binaires. Le cas d’obstacle synthétique est un test de géométrie uniquement.
- Suites JavaScript existantes et tests natifs des surfaces et familles M05 contrôlés.
- Vérification dans un navigateur isolé : chaîne fonctionnelle 4×4 et grande façade de démonstration, affichage opaque et compositions visibles. Le projet utilisateur sur le port 8765 n’a pas été remplacé.

Aucun fichier n’a été écrit dans les dossiers de blueprints du jeu pendant ces tests. Les nouvelles compositions restent à tester en jeu. Elles constituent une grammaire de façade inspirée des modules, pas une reproduction intégrale de toutes les constructions de JazzFrank.
