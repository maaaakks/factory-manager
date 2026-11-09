# 63 — Compositions M05 reliées au bâtiment

Les captures en jeu ont révélé une erreur de composition : une façade trop basse pouvait recevoir un motif de 12 m à partir de Z = 8 m, ou un motif initialement réservé à la façade pouvait être utilisé en couronnement sur le toit. Plusieurs fragments indépendants se retrouvaient ainsi dans le ciel. Les tests d'export précédents validaient les objets et connexions, pas la continuité architecturale de ces ensembles.

## Règles corrigées

- Les grands motifs de façade restent dans la hauteur des murs. Le placement en couronnement est supprimé pour ces motifs. La toiture possède son propre générateur de détails.
- Les bases des travées correspondent aux niveaux de fondation ou de plancher existants. Les niveaux arbitraires à 8 ou 16 m ne servent plus de secours.
- Trois versions basses complètent les trois compositions hautes : verrière, portique et galerie. Elles assemblent des éléments natifs sans réduire leurs dimensions : deux rangées de vitrages, un auvent adapté et des montants reliés. Les bandeaux et ventilateurs hauts sont omis dans ces versions.
- Les motifs qui ne passent pas sont remplacés par la charpente fine ou ne sont pas posés. Les machines et leurs connexions ne changent pas.
- Les corniches ont des pieds allant jusqu'au dessus de la toiture. Les arceaux des ventilations possèdent aussi leurs pieds ; les décalages de sécurité ne créent plus de structures sans appui.
- Le bardage ajusté des angles utilise des barres peintes de section native, à la place de poutres H superposées comme si elles étaient pleines. Les raccords aux montants tiennent compte des sections réelles. Cela retire les grandes ailettes visibles sur les captures.

## Vérifications

18 nouveaux plans de plain-pied, formats 4×4/5×5/6×6 et six variantes : aucune grande façade au-dessus du toit, versions basses et appuis déclarés. Vérification des pieds sur les surfaces de toiture, des classes de poutres, de l'invariance du projet et des limites natives. Ces scènes complètent les scènes de façade, de production compacte et de variations de toit.

Le JavaScript de l'aperçu et le Python de l'export produisent les mêmes pièces. Les fichiers SBP sont construits et relus dans des répertoires temporaires. La correction n'a pas encore été revue en jeu ; les captures utilisateur démontrent les défauts de la version précédente.

Après mise à jour, recharger l'atelier puis réexporter le projet. Les blueprints déjà placés dans une partie ne sont pas modifiés automatiquement.
