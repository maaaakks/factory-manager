# 51 — Façades, accès piéton et lisibilité 3D

20 octobre 2026. Recherche et implémentation locale ; pas de nouveau test en jeu.

## Références de blueprints

Les descriptions ci-dessous résument les fiches des auteurs. La colonne « pattern » est notre interprétation pour Factory Manager, pas une promesse d'importer ces créations à l'identique.

| Référence | Auteur / contenu observé | Pattern à retenir |
|---|---|---|
| [Futuristic Exterior Wall](https://satisfactory-calculator.com/en/blueprints/index/details/id/2499/name/Futuristic%2BExterior%2BWall) | UltraXan64 ; façade répétable, piliers, fenêtres, panneaux, extensions de coins. Ancien blueprint Update 7. | Façade en relief, hiérarchie entre ossature et remplissage, coins assortis. |
| [Modular Wall](https://satisfactory-calculator.com/en/blueprints/index/details/id/5404/name/Modular%2BWall) | Xeinaemm ; fenêtres Full Frame, poutres peintes et murs, 46 objets. | Travée régulière vitrée, composants réutilisables plutôt que fenêtres dispersées. |
| [On-Grid Sign Walls — flat / inner / outer corner](https://satisfactoryblueprints.com/set/61b6332a-c00f-4fe6-8b4d-c49bb937934b) | Kit de murs de 4 m et panneaux de 0,5 m, angles intérieurs et extérieurs. | Grammaire complète du style : panneau droit + coin intérieur + coin extérieur. |
| [Glass Wall 1x2 Mid](https://satisfactoryblueprints.com/blueprint/a4da37a9-d4d2-4f40-90b3-b7cc0d67caff) | Self_Immolation ; famille de murs vitrés Mid / Edge, éclairage ; sans mods d'après la fiche. | Variantes de centre et de rive cohérentes, rythme de montants. |
| [M05_MODULE — modular warehouse](https://satisfactoryblueprints.com/blueprint/c255f7b1-4337-4197-b6f6-56223b05e4a1) | JazzFrank ; modules de milieu, coins et angles intérieurs, raccords électriques au toit. | Une architecture complète : portes, fenêtres, poutres, ventilation, passerelles, verrières et toiture coordonnées. |
| [9.33 m radius Octagon](https://satisfactoryblueprints.com/blueprint/19a0ec6e-d21f-4572-a3a8-ad27bdb728fc) | sariaz ; kit octogonal, rayon 9,33 m, sans mods d'après la fiche. | Casser la silhouette avec des volumes polygonaux ; piste future, pas encore générée par notre moteur. |
| [Wall Deco — Factory Entrance 1x3](https://satisfactory-calculator.com/fr/blueprints/index/details/id/10242/name/Wall%2BDeco%2B-%2BFactory%2BEntrance%2B1x3) | Gnoneks ; piliers métalliques et panneaux, 19 objets. | Portail assumé, encadrement et signalétique. La liste de pièces ne décrit pas une porte mobile. |
| [NOVA Brick Wall 8x4m](https://satisfactoryblueprints.com/blueprint/7f6dbf12-2079-42ab-871c-5cc7bd37e7f8) | _nova_tech_ ; module à motif de briques, tag FICSMAS. | Varier le remplissage à l'intérieur d'une trame stable ; vérifier le contenu saisonnier avant emploi. |
| [CTP Station Entrance](https://satisfactory-calculator.com/en/blueprints/index/details/id/3677/name/CTP%2BStation%2BEntrance) | Hornslet ; entrée monumentale, petits piliers béton, murs de 1 m, 455 objets. | Portique béton et profondeur de façade ; inspiration à simplifier pour les petits formats. |

Trois fichiers `.sbp` ont été téléchargés dans le dossier de recherche local `outputs/community-wall-references`, sans copie dans les dossiers du jeu. M05 a été parsé : **289 acteurs**, dont 32 poutres horizontales, 10 connecteurs de poutres, 4 murs à porte, plusieurs familles de fenêtres, toits vitrés, ventilation, garde-corps et passerelles. Empreinte SHA-256 dans `survey.json`. Les deux autres fichiers ont des versions de sauvegarde non prises en charge par notre parseur (Glass Wall : 46 ; Octagon : 36). Leurs fiches ont été consultées, leur géométrie n'a pas été validée. Aucun de ces téléchargements n'a été testé en jeu dans cette passe.

## Designs disponibles en un clic

Dans Atelier → Design → Façades :

- **Atelier béton** : angles en retrait quand libres, diagonales, terrasse et puits central.
- **Campus vitré** : trame vitrée, retraits et deux verrières symétriques.
- **FICSIT industriel** : bardage sombre, ossature orange, retraits et verrière longitudinale.
- **Compact fonctionnel** : rectangle, remplissage sobre, pas de poutres décoratives hors portail.

Les packs déclarés débloqués continuent de limiter les choix. Un preset verrouillé n'active pas un pack en cachette. Les réglages détaillés restent dans « Personnaliser murs et toiture ». Les presets sont nos compositions, inspirées de principes communs ; ils ne reproduisent pas les blueprints téléchargés.

Les retraits retirent les coins libres de l'enveloppe. Ils ne déplacent pas les machines et ne créent pas encore des bâtiments arbitraires en L, des ailes polygonales ou un contour différent à chaque étage. Si tout l'espace est occupé, le contour reste rectangulaire.

## Accès piéton, distinct des ressources

Le design cherche par défaut une travée de façade accessible sur le sol du rez-de-chaussée : 8 m de large, 4 m d'approche intérieure, contrôle de hauteur jusqu'à 8 m. Priorité à la façade avant puis aux autres côtés ; position la plus proche du centre de chaque côté. Le choix peut être forcé avant/droite/arrière/gauche, ou désactivé.

Le contrôle utilise les volumes des machines et de la logistique, les polylignes physiques et les courbes Hermite natives échantillonnées des convoyeurs. Un convoyeur en hauteur qui laisse le dégagement passe. Une liaison logique non routée bloque prudemment sa région, plutôt que d'affirmer qu'elle laisse un passage. Une dalle basse absente ou percée ne prouve pas un accès et empêche la proposition.

Le portail est **ouvert**, sans vantail ni porte automatique. Deux panneaux superposés sont remplacés par deux jambages et un linteau natifs en poutres. Ces ouvertures intentionnelles ne sont pas comptées parmi les trous de façade dus aux collisions. Si aucun accès ne convient, le panneau indique « Entrée impossible » ; les bâtiments ne sont pas déplacés et aucune entrée traversant une machine n'est inventée.

La proposition valide une approche locale, pas encore un réseau de circulation intérieur reliant tous les postes ou des escaliers entre étages. Le calculateur n'est pas un solveur de circulation humaine : en format plein il faudra libérer la travée ou agrandir, puis appliquer le design.

## Z-fighting : géométrie et aperçu

La documentation primaire [MDN — polygonOffset](https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/polygonOffset) décrit le décalage de profondeur appliqué avant le test de profondeur. L'aperçu utilisait déjà ce mécanisme pour les faces remplies et leurs contours ; le modifier seul ne corrigerait pas les superpositions exportées dans le jeu.

Règles mises en place :

1. Séparer les plans extérieurs des pièces : pilier à 0 m, bandeau à 0,05 m, poutre à 0,10 m et mur décoré à 0,65 m vers l'intérieur. Les centres et épaisseurs natifs déterminent ces plans. Le retrait est identique en JS et Python.
2. Décaler la seconde diagonale d'une croix de 0,10 m pour éviter deux faces avant coplanaires au croisement.
3. Joindre les jambages de baie aux traverses par leurs extrémités, sans leur faire occuper la même surface avant.
4. Dédupliquer les faces exactement identiques et les lignes identiques lors du chargement GPU. Cela ne résout pas toutes les intersections partielles d'objets arbitraires provenant d'une sauvegarde.
5. Centrer et adapter l'intervalle de profondeur à l'étendue de chaque scène au lieu d'utiliser une échelle fixe de 256 m. Les mouvements de caméra réutilisent la géométrie ; aucun découpage de polygones à chaque image.

Les trois premières règles s'appliquent aux nouvelles façades et à l'export natif. Les deux dernières concernent le visualiseur. Elles ne réparent pas les chevauchements déjà présents dans une sauvegarde extérieure. L'absence absolue de scintillement en jeu n'est pas prouvée par les tests locaux.

## Couleurs de l'explorateur

Les bâtiments retrouvent leur couleur par catégorie : murs, toits, sols, machines, stockage, mineurs et logistique restent distinguables. Les convoyeurs sains ou indéterminés sont gris bleuté ; seuls les blocages estimés sont orange ou rouges. Des contours permettent de distinguer les volumes voisins. Les pourcentages d'efficacité et le diagnostic de flux restent disponibles.

## Vérification

- Vérification navigateur Chrome de l'usine cuivre jojo à 100 % : palette par catégorie et convoyeurs neutres, mineur visible, rotation GPU fonctionnelle.
- Vérification des presets, du portail, du rendu opaque et de la rotation dans l'atelier 6×6 ; aucune erreur console observée.
- Tests des accès obstrués par machines / convoyeurs, convoyeur au-dessus, entrée désactivée, verrous de packs, couleur des diagnostics et déduplication de géométrie.
- Parité de la géométrie JS/Python, extrémités et rotations des poutres natives, exports binaires relus, chaîne compacte 120 minerais → 10 plaques renforcées préservée.
- Aucun dossier de sauvegarde ou de blueprint du jeu écrit. Les projets ouverts de l'utilisateur ne sont pas remplacés.
