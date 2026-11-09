# Design et habillage natif

19 octobre 2026.

## Utilisation

- **Construction** regroupe les machines, convoyeurs, câbles et réglages réseau. « Réseau & capacités » est repliable sous les outils électriques.
- **Design** comporte trois catégories : Sols, Peinture et Façades. La perspective occupe l’espace principal. Le petit bouton **Élévation** ouvre ou referme Face/Côté ; « Vue 3D ↗ » reste uniquement dans Construction.
- **Peinture** enregistre les couleurs des bâtiments exportés. Les schémas de construction et la 3D gardent leurs couleurs de lecture, indépendantes des couleurs noires ou foncées choisies pour le jeu. Appliquer une palette par catégorie désactive l’ancienne peinture globale.
- **Sols** propose béton FICSIT, béton brut, béton ciré, asphalte et tôle antidérapante. Béton ciré et tôle utilisent les variantes natives de 1 m. Dans le module compact, les étages peuvent passer de cadres ajourés à des dalles ; les tuiles occupées par les élévateurs restent ouvertes. La base reste pleine. Le choix de matière s’applique aux dalles ; un cadre reste un cadre.
- **Façades** : Atelier béton, Industriel FICSIT, Verrière. Rythme des fenêtres, variation déterministe, piliers natifs de 2 m aux coins ou sans piliers, couronnement contrasté ou sobre. Les anciens choix de piliers schématiques de 30/50/100 cm sont présentés comme piliers natifs de 2 m ; aucun redimensionnement artificiel d’acteur.
- **Toitures plates** : goudron, FICSIT, verrière ou terrasse avec puits de lumière. Les variantes inclinées ne sont pas proposées dans cette première intégration.
- Animations brèves des vues, catégories, panneaux, menus et navigation. Respect de la préférence système de réduction des animations ; transitions de navigation enrichies lorsque le navigateur les prend en charge.

## Export réel

Les façades ne bloquent plus l’export au motif « aperçu uniquement ». Les murs, fenêtres, piliers, bandeaux et panneaux de toit sont ajoutés au `.sbp`, avec leurs classes et recettes natives et leurs coûts de construction. Le `.sbpcfg` conserve l’icône de sortie et précise la présence de l’habillage. Les machines, connexions et débits conservent leurs contrôles existants.

Les règles déterministes de `WorkshopDesign.envelope` sont reproduites dans `native_design.py`. Les tests comparent leurs listes de pièces avant de vérifier les fichiers sérialisés. Le serveur recalcule lui-même les pièces : le client ne peut pas injecter une classe arbitraire.

Les pièces proviennent des définitions de la version installée du jeu (`CommunityResources/Docs/en-US.json`). Les classes et recettes d’architecture sélectionnées ont également été observées dans une lecture de sauvegarde. Elles utilisent la représentation native commune des bâtiments légers, sans inventaire, composant réseau, référence mondiale ni échelle artificielle. Le repère natif des murs est au pied du mur, leur largeur suit l’axe local Y ; les toits plats et petits piliers utilisent un repère centré.

Le contour reste à l’intérieur du format 4×4, 5×5 ou 6×6. Une grande ouverture est conservée au rez-de-chaussée. Les travées qui intersectent les volumes des bâtiments sont omises ; cet habillage ne déplace pas automatiquement les machines pour fermer toutes les façades. Les plafonds suivent la hauteur des bâtiments, avec des murs de 4 m puis des compléments de 1 m. Exemple compact 4×4 : plafond à 31 m et toit de 50 cm dans le volume de 32 m. Un dépassement est refusé avant modification du projet ou export.

L’aperçu reste une représentation schématique : les fenêtres sont indiquées par cadres et panneaux, les matériaux par couleurs. Il ne reproduit pas les textures et maillages du jeu. Le contenu débloqué reste une sélection manuelle, pas une lecture de la progression de partie.

## Vérification et limites

- 18 suites JavaScript : calcul, sélection, formats, stockage temporaire, routage, flux, styles et matériaux.
- Parité des pièces aperçu/serveur pour cinq variantes, trois styles, quatre toitures et cinq matières de sol.
- Export puis relecture de cinq blueprints compacts et d’un blueprint générique ; classes, recettes, positions, rotations, ingrédients, absence de références externes et limites vérifiés. Écriture complète `.sbp` + `.sbpcfg` testée dans un dossier isolé, sans modification de sauvegarde ou de blueprint du jeu.
- Quatre variantes natives antérieures sans façades restent exportables.
- Vérification dans Chrome : panneau d’élévation, transparence/opacité GPU, peinture indépendante, changement de matière et navigation entre vues.

Les fichiers ont été contrôlés localement ; **le nouvel habillage n’a pas encore été placé en jeu**. Le test en SANDBOX doit vérifier aspect, orientation des matériaux et démontage/coûts. Les autres limitations d’export restent explicites : repères entrée/sortie schématiques, trajets manuels à points de passage et gaines personnalisées non calibrées ne deviennent pas des raccords natifs par l’ajout d’une façade.
