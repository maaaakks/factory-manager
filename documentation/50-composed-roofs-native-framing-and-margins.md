# Toits composés, ossature native et marges de façade

## Icônes du jeu

179 icônes PNG de Satisfactory remplacent les illustrations schématiques dans les ressources, le calculateur, les cartes de projets et la palette de machines/logistique. Elles sont embarquées dans `dist/resource-icons.svg` : le navigateur ne contacte aucun site externe pour les afficher.

Source : [Satisfactory Tools](https://github.com/greeny/SatisfactoryTools), révision et empreinte SHA-256 de chaque image dans `data/game-icons-manifest.json`. Les images sont des éléments graphiques du jeu de Coffee Stain Studios, distincts de la licence du code de Factory Manager. Le dépôt de Satisfactory Calculator n’est pas utilisé pour ces images.

## Compositions de toit

Le toit ne choisit plus indépendamment les dalles vitrées. Il utilise une composition avec au moins un axe de symétrie : un puits central, deux verrières opposées, quatre groupes, trois groupes (alignés en 5×5/6×6, triangulaires en 4×4), une bande longitudinale ou une couronne.

**Composition des verrières** choisit la famille. En Auto, **Rafraîchir le toit** parcourt les familles ; le motif fait aussi varier les dimensions et l’orientation lorsque le format le permet. Les matériaux de couverture restent uniformes au lieu de varier au hasard entre les dalles. Les vitres suivent les mêmes plans de pente que le toit.

Les dimensions restent compatibles avec les pièces natives de 8 m. Un motif incompatible avec les coins retirés devient un puits central cohérent au lieu de perdre ses verrières. Les murs et leurs fenêtres ne changent pas quand on rafraîchit seulement le toit.

## Ouvertures et poutres

Les panneaux qui rencontrent les bâtiments restent omis. Les panneaux manquants contigus d’une même façade sont regroupés en baies industrielles. Le mode **Encadrer les baies industrielles** propose jambages, linteau et traverse basse ; chaque poutre est vérifiée et omise si elle rencontrerait un bâtiment. Le générateur ne masque donc pas les conflits avec un décor qui traverserait les machines.

**Poutres et diagonales** ajoute un rythme de contreventements alternés sur des travées pleines. **Contreventements en croix** propose une ossature plus dense. Les fenêtres conservent leur vitrage. Ces deux modes réservent une profondeur de 1 m aux façades pour placer les poutres devant les panneaux et éviter les surfaces coplanaires. Les grandes traverses sont divisées en segments de 16 m maximum.

Les poutres sont de vraies `Build_Beam_Painted_C` exportées avec `mLength` et une rotation 3D adaptée à leurs extrémités. Le gabarit a été relevé en lecture seule dans le blueprint local `FICSIT Coupon ATM.sbp` ; les deux variantes et leurs recettes sont déclarées dans les Docs du jeu installé. Aucun blueprint du joueur n’a été modifié.

## Forme de l’enveloppe

Le contour **Angles en retrait** retire les coins de 8×8 m qui ne contiennent aucun bâtiment ni logistique, en gardant 1 m de sécurité autour des volumes. Les murs suivent ce contour et le toit couvre exactement les cellules conservées. Les coins occupés restent en place. Le comptage des ouvertures distingue les vrais conflits de façade des retraits volontaires.

Les fondations extérieures sont conservées : elles forment des terrasses. Cette première version crée des retraits de coins ; elle ne génère pas encore librement toutes les formes de bâtiments ni des retraits différents à chaque étage.

## Marge dès la construction

Le module natif compact de 32 m est désormais centré dans les formats plus grands : 4 m de réserve de chaque côté en 5×5 et 8 m en 6×6. Ses raccords internes restent inchangés. Les variations de layout utilisent la même règle.

Quand on agrandit le format, les objets sont décalés ensemble de la moitié de la différence de taille, avec leurs trajets explicites. Le tampon reste séparé. Les ouvertures de plancher sont recalculées pour les élévateurs déplacés, y compris ceux qui passaient auparavant dans la gaine périphérique.

Pour un projet existant déjà en 6×6 mais ancré dans un coin : **Design → Façades → Centrer le plan pour les façades**. Le déplacement conserve les recettes et les connexions et peut être annulé. Il ne réduit pas l’encombrement d’une chaîne qui utilise déjà toute la largeur : il faut alors recalculer une implantation ou conserver des baies.

## Validation

- 108 compositions testées : nombre de groupes, symétrie, déterminisme et formats.
- 43 cas de correspondance exacte entre le générateur JavaScript et l’export Python : décor, retraits, toits et baies.
- Poutres natives : vérification des extrémités, rotations et longueurs, puis sérialisation et relecture binaires dans un dossier temporaire.
- Exports compacts 5×5 et 6×6 avec marges et décor ; non-régression du module natif et des élévateurs génériques.
- Vérification visuelle dans Chrome des icônes, du contour et de la couverture.

La lecture binaire et l’aperçu sont validés localement. Le nouvel habillage doit encore être essayé dans le jeu ; cette vérification ne prétend pas remplacer un test en session.
