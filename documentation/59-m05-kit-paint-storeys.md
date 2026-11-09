# 59 — Kit M05, peinture des façades et réorganisation par étages

## Deux approches M05

La catégorie M05 contient désormais un **Kit procédural** et les **Modules de JazzFrank** existants. Les modules complets conservent leur géométrie d’origine, leur trame de 40 m et leur réservation périphérique. Les anciens projets ne sont pas convertis automatiquement.

Le kit est une nouvelle grammaire procédurale : travées de 8 m, vitrages de même référence native que le M05, poutres acier H à longueur native réglable et ventilations clonées depuis le module M5 avec leurs propriétés d’origine. Il ne réduit pas les modules de 40 m. Les baies, retraits, terrasses et toits s’adaptent à l’emprise occupée et à la hauteur réelle des machines. Les variations réutilisent les composants sur des terrains petits, rectangulaires et sur plusieurs étages. Les façades impossibles près d’une machine restent ouvertes et signalées, comme les autres styles.

## Peinture et matière

L’onglet Peinture propose séparément murs, poutres et cadres, vitrages, toits, ainsi que les catégories de production existantes. L’habillage prévisualise les couleurs ; les machines gardent leur coloration de lecture dans la vue 3D. Les couleurs sont inscrites dans les objets exportés. Les panneaux de bardage ajustés par poutres gardent le rôle « murs » pour la peinture.

La matière des panneaux pleins peut rester celle du style, devenir FICSIT ou béton brut. Les références de classe et les recettes de construction sont remplacées réellement dans le fichier natif ; il ne s’agit pas uniquement d’une couleur. Les vitrages, les portes, les panneaux spéciaux et l’ossature conservent leurs fonctions et leurs références. Les mêmes réglages s’appliquent au kit et aux panneaux compatibles des modules M05 originaux.

## Formats et étages

Les dimensions libres demandent un nombre d’étages plutôt qu’une hauteur totale en mètres. La hauteur disponible est dérivée automatiquement ; la hauteur de chaque niveau reste calculée selon les machines et la logistique.

Si le format réduit ferait déborder l’implantation actuelle, l’application propose **Réorganiser en X × Y**, un nombre d’étages et un bouton pour reconstruire machines et réseaux. Le projet précédent est conservé si le calcul échoue ; une réussite reste annulable. Un changement d’étages dans les dimensions libres suit le même chemin.

Les formats explicitement demandés ne sont plus agrandis pour donner la priorité à l’habillage : ils donnent la priorité à la production. Les façades utilisent ensuite les espaces réellement disponibles. Le M05 complet reste incompatible avec un petit terrain ; choisir le kit permet de conserver ce terrain.

## Vérification

- Test réel dans le navigateur : import d’une chaîne 60 minerais de fer → 5 plaques renforcées en 5 × 5 / 2 étages ; demande 4 × 4 ; proposition de 3 étages ; calcul via le Worker et l’API de modules compacts ; résultat 4 × 4 / 3 étages. Application du kit, peinture bleue des murs et matière béton, rechargement et prévisualisation native réussie.
- Réseau du plan réorganisé : 54 convoyeurs, 21 élévateurs ; entrées et sorties conservées. Projet source, nom, tampon et réglages de peinture conservés par les tests de réorganisation.
- Neuf scènes de kit sur petits terrains et rectangles, trois variations par format ; parité exacte entre JavaScript et Python, export des ventilations sources et réouverture binaire.
- M05 original peint et changé en béton : parité aperçu/export, bonnes classes de murs natives et réouverture du fichier.
- Suites JavaScript existantes et tests natifs des six compositions M05 et des familles de styles passés.

Ces vérifications ne sont pas un essai en jeu. Aucun blueprint n’a été écrit dans les dossiers du jeu pendant les tests. La réorganisation dépend des recettes et des contraintes de la chaîne ; tous les produits ne disposent pas de modules compacts calibrés.
