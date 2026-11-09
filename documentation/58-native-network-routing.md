# 58 — Raccordement natif des réseaux complets

Le routeur réservait uniquement les bâtiments déjà présents. Une liaison pouvait couper l’accès à un port ou traverser l’emplacement d’un élévateur encore à construire, ce qui bloquait une liaison ultérieure vers un fusionneur ou une assembleuse.

## Correction

- Pour les chaînes de quatre machines ou plus, calcul avec réservation préalable des accès et des colonnes d’élévateurs. Les machines restent à leurs positions et gardent leurs recettes et horloges.
- Colonnes limitées à leur étage, recherche par pas de 25 cm, plusieurs niveaux de service disponibles, sélection des directions selon la destination.
- Recherche bornée de chemins à plusieurs virages lorsque les couloirs simples ne suffisent pas. Le tracé retenu passe encore par la validation des courbes natives et des collisions.
- Voies entre étages recherchées autour du milieu du trajet ; les ouvertures de planchers suivent les élévateurs réellement créés.
- Pour M05 : la bande de 24 m des modules et le plafond intérieur de 30,6 m restent protégés. Les nouveaux ajustements M05 prévoient 6 m supplémentaires de marge de production par côté avant d’arrondir aux modules de 40 m. Un ancien M05 trop serré doit réserver de nouveau sa marge ; l’export ne redimensionne pas silencieusement le projet.
- Deux résultats réussis sont gardés en mémoire, avec une empreinte du projet complet. L’aperçu puis l’export du même projet utilisent exactement les mêmes raccordements. Les valeurs retournées sont copiées pour protéger ce résultat.

## Validation

Le test `tests/check_native_network_routing.py` contrôle des chaînes fer → plaques renforcées sur un et deux étages et deux compositions M05. Il vérifie chaque liaison logique jusqu’à son raccordement physique, la conservation du projet, les limites M05, les références natives et la réouverture du fichier binaire. Un cas de passages alternés vérifie la recherche à plusieurs virages. Les tests existants couvrent les élévateurs Mk.1 à Mk.6, les dimensions rectangulaires, les matériaux et les six compositions M05.

L’endpoint HTTP d’écriture est testé avec le dossier des blueprints remplacé par un dossier temporaire. Aucune sauvegarde ou installation de blueprint dans le jeu pendant ces vérifications.

## Limites

Le routage reste une recherche bornée : un refus ne démontre pas l’absence mathématique de tout trajet possible. Un grand ancien plan générique 120 minerais → 10 plaques renforcées, allongé sur un seul étage, reste un cas de recherche non résolu. Les modules natifs calibrés pour ce débit restent pris en charge. Les tests binaires et les aperçus ne remplacent pas un essai en jeu ; `inGameValidated` reste faux.
