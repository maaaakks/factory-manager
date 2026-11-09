# Priorité actuelle : outil externe local

Voir [le plan externe](08-external-tool.md) et le dossier external-tool à la racine du projet. Les documents Unreal ci-dessous restent une référence pour un éventuel mod futur.

# Satisfactory factory tools — project documentation

Planning baseline: 18 October 2026. Les documents 01 à 07 décrivent le projet de mod initial. Le prototype externe local est maintenant utilisable ; son état et ses vérifications sont décrits dans les documents 08 à 16. Le document 16 décrit l'interface actuelle. Aucun mod en jeu n'est livré.

## Read in this order

1. [Vision and roadmap](01-vision-and-roadmap.md) — the five modules and their common development sequence.
2. [Shared foundation](02-shared-foundation.md) — data model, boundaries, tracing, geometry, and service responsibilities.
3. [Compact player interface](03-player-interface.md) — user journeys, wireframes, controls, and usability criteria.
4. [Dependencies and setup](04-dependencies-and-setup.md) — tools, runtime dependencies, version records, and technical investigations.
5. [Small implementation milestones](05-foundation-backlog.md) — ordered slices, acceptance criteria, and testing fixtures.
6. [Decisions and evidence](06-decisions-and-sources.md) — assumptions, open questions, and documentation sources.

## First deliverable

Open the tool, aim at one vanilla conveyor, select it, and see its name, direction, capacity if accessible, and immediate connections. Highlight the selected object. Close the tool and return to normal play cleanly.

This deliberately stops before automatic factory discovery, live measurement, optimization, and building placement. Each will be added as a separately testable feature.

## Product principles

- Every feature must be usable and testable through the game interface; console output is supporting evidence.
- Show a useful compact summary first; reveal details when requested.
- Distinguish connected, calculated, observed, unknown, partial, and outdated information.
- Never silently expand a selection to an entire connected factory network.
- Let the player edit a proposed line boundary before accepting it.
- Begin with inspection; add suggestions, previews, and explicit application later.
- Keep game-version-specific access behind adapters so the shared model survives API changes.

## Initial support envelope

Windows development; single-player first; vanilla solid-item conveyors, lifts, simple storage, ordinary splitters/mergers, and simple manufacturers added incrementally. Initial tests use uncomplicated recipes and fixed clock settings. Unsupported actors are visible stopping points, never silently skipped.

Pipes, trains, vehicles, drones, smart routing, exact historical flow, automated building, style recognition, and complex optimization are later work. Multiplayer-aware architecture is planned, but multiplayer support requires its own verification milestone.

## Document status convention

**Decision** means a proposed project baseline. **Verified documentation** means a capability is described by a linked source. **Prototype required** means implementation feasibility or behavior remains unproven. No version or dependency is considered locally installed merely because it appears in these docs.

## Implementation progress

[Environment inventory and F00 setup status](07-environment-status.md).



[Résultats de vérification du prototype externe](09-external-tool-test-results.md).


[Usine de référence, calques architecturaux et rôles proposés](10-factory-reference-and-roles.md).


[Fond de carte et bascule de vue](11-map-background.md).

[Usines enregistrées, architecture lightweight et estimations théoriques](12-persistence-lightweight-estimates.md) — état actuel, utilisation et limites.

[Orientation des murs et jauge d'équilibrage](13-wall-orientation-and-balance.md) — définition du pourcentage et prochaine tranche.

[Zones de concentration et couverture interne](14-density-zones-and-coverage.md) — remplace le pourcentage précédent et ajoute l'analyse d'une zone en un clic.

[Frontières aux coffres et pourcentages par ressource](15-storage-boundaries-and-resource-flow.md) — état actuel du diagnostic entrées, intermédiaires et sorties.

[Tableau simple, guidage par murs et aperçu en volume](16-simple-dashboard-walls-and-volume.md) — interface actuelle et vérification des chemins d'entrée.

[Atelier de blueprints — plan proposé](17-blueprint-workshop-plan.md) — lecture, copie fidèle, assemblage, fusion et raccords avant la génération de layouts.

[Créateur manuel de blueprints — première version](18-manual-blueprint-creator-plan.md) — périmètre prioritaire : ouvrir, exporter, créer machines/convoyeurs/câbles et valider une ligne en jeu.

[Créateur sur plan — 6 × 6 fondations](19-paper-blueprint-6x6-plan.md) — priorité actuelle : éditeur manuel et vérifications sur plan ; export natif et tests en jeu reportés.

[Atelier 6 × 6 — première tranche livrée](20-workshop-first-slice.md) — placement, manipulations, vérification géométrique et sauvegarde du projet JSON.


[Atelier : objectifs, étages et liaisons](21-workshop-flows-levels-and-assistance.md) — navigation commune, import des objectifs cuivre/fer, débits, Shift, hauteur et premières propositions de convoyeurs et poteaux.


[Formats et sélection](22-workshop-formats-and-selection.md) — formats 4×4, 5×5 et 6×6, refus des débordements et retour à la sélection par F ou clic hors cadre.


[Onglet Calculateur et import par lien](23-calculator-tab-and-link-import.md) — choix produit/débit, lien SCIM sans JSON et ouverture dans l’atelier.


[Sélection multiple dans l’atelier](24-workshop-multiple-selection.md) — rectangle, Shift+clic, déplacement et suppression du groupe avec annulation.


[Implantation, dégagements, sols et thèmes](25-workshop-clearances-floors-and-themes.md) — couloirs, gaines, réseau logique et limites du routage physique.


[Tampon et interface de l’atelier](26-workshop-buffer-and-editor-ui.md) — prises, rotations, stockages temporaires, objectifs centraux et messages intégrés.


[Entrées limitées, tampon sur grille et capacités](27-input-budgets-buffer-grid-and-capacities.md) — maximum par ressources, MW théoriques, recherche et couleurs de saturation.


[Gel au démarrage dans Chrome](28-chrome-startup-freeze.md) — boucle sans machines corrigée, bilan léger et démarrage de secours sans effacer le brouillon.


[Ordre des étages de production](29-production-floor-order.md) — fonderies en bas, dépendances vers le haut et signification du fond coloré.


[Apparence neutre et personnalisation globale](30-neutral-blueprint-appearance.md) — teintes désactivées par défaut et couleur commune facultative.


[Premier blueprint natif dans SANDBOX](31-native-blueprint-first-test.md) — deux fondations et une fonderie, écriture directe et procédure de vérification en jeu.


[Deuxième test natif : chaîne de plaques](32-native-connected-test.md) — fonderie, convoyeur raccordé, constructeur et réseau électrique interne.


[Troisième test natif : deux étages](33-native-vertical-test.md) — élévateur de 12 m, gaine ouverte, convoyeurs et réseau électrique entre niveaux.



[Test 04 : plaques renforcées 4×4](34-native-reinforced-plates-test.md) — 120 minerais → 10 plaques renforcées/min vers un coffre, trois étages en béton et traversées de sol natives.


[Export natif du projet Atelier](35-workshop-native-project-export.md) — exporter les bâtiments et connexions physiques du projet courant, avec contrôles et erreurs explicites.


[Patterns compacts : références kouyère](36-compact-layout-patterns.md) — mesures natives, paires face à face, colonne centrale et logistique en hauteur ; un poteau par machine dans l’atelier.

[Vue 3D et Calculator dans l’atelier](37-workshop-preview-and-calculator.md) — aperçu en lecture seule, sélecteur avec recherche et débits automatiques conservés.

[Modules compacts et export physique](38-compact-native-workshop.md) — profil 120 fer → 10 plaques renforcées, paires natives, trois niveaux, élévateurs et exemple SANDBOX.

[Navigation 3D et commandes simplifiées](39-workshop-3d-navigation.md) — rotation/zoom à la souris, boutons Face/Côté et Entrée/Sortie, aperçu après calcul et retour à l’atelier.

[Factory Manager : Design et layouts](40-factory-manager-design-and-layouts.md) — vues Construction/Design, styles procéduraux, hauteurs minimales, planchers, convoyeurs économiques et icônes de sortie.

[Construction : interfaces, trajets et GPU](41-construction-interfaces-and-gpu.md) — entrées/sorties dédiées, recettes collectives, tracé des convoyeurs, moteur de flux commun et aperçu opaque accéléré.

[Design et habillage natif](42-native-architecture-and-design.md) — matières de sol, façades exportables, toitures, palette indépendante de la 3D et panneaux animés.


[Réseau automatique Entrée → machines → Sortie](43-automatic-transport-network.md) — chaîne guidée par les recettes, répartiteurs/fusions, aucun contournement des transformations et erreurs sans modification partielle.

[Exploration et flux physiques](44-explorer-navigation-and-physical-flows.md) — carte épurée, inspection repliable, sélection des usines, aperçu GPU et limites des convoyeurs.
[Calculateur et préférences d’étages](45-calculator-independent-projects-and-storeys.md) — nouveau projet indépendant, format libre, génération sans habillage, réseaux et cas natif 60→5.

[Exploration : calques, sorties et cache](46-explorer-layers-boundaries-cache.md) — panneaux simplifiés, sorties de périmètre, géométrie des toitures et conservation locale de la sauvegarde.

[Atelier : calques, convoyeurs et variantes](47-workshop-layers-procedural-roofs.md) — réseaux en volume, aération contrôlée, toits procéduraux et gestion réversible des projets.

[Élévateurs natifs génériques et anciens plans](48-generic-native-lifts-and-legacy-conversion.md) — export des élévateurs, précontrôle 3D, conversion annulable et apport direct de lingots.

[Exploration : efficacité, mineurs et rampes](49-explorer-efficiency-miners-ramps.md) — utilisation des filons, diagnostic sans faux goulots de manifold, sources amont en 3D et géométrie des rampes.

[Toits composés, poutres et marges](50-composed-roofs-native-framing-and-margins.md) — icônes du jeu hors ligne, verrières groupées, baies encadrées, contreventements natifs, angles en retrait et chaînes centrées.

[Références de façades, accès et lisibilité](51-architecture-references-access-and-readability.md) — neuf exemples de blueprints, quatre designs, portail piéton, séparation des surfaces et couleurs 3D par catégorie.

[Familles de styles et variations procédurales](52-style-families-and-procedural-variations.md) — quatre catégories, huit familles dont Entrepôt modulaire, trames natives, palettes, portiques et variations enregistrées.

[Habillage, silhouettes et priorité Architecture](53-cladding-silhouettes-and-architecture-priority.md) — calque commun, 11 familles, volumes en L/U/croix, lanterneaux et sheds, marges et styles sur un étage.

[Façades en relief et raccords d’angle](54-modular-facades-and-corner-junctions.md) — volumes saillants, galeries, gradins, terrasses, vitrages M05 et jonctions à montant unique.

[Dimensions libres et emprise adaptée](55-free-dimensions-and-occupied-footprints.md) — largeur, profondeur et hauteur indépendantes ; contours autour des bâtiments ; export natif XL expérimental.

[Modules natifs M05 de JazzFrank](56-jazzfrank-m05-native-modules.md) — catégorie dédiée, sources mesurées, assemblages C/M/IN1, aperçu détaillé et export natif.

[Calculateur et design simplifiés](57-simple-calculator-and-design.md) — intentions visuelles, dimensions automatiques, réorganisation des machines et réseaux en arrière-plan, sols et calques regroupés.

[Raccordement natif des réseaux complets](58-native-network-routing.md) — accès et élévateurs réservés, recherche à plusieurs virages, cache des exports vérifiés et limites connues.

[Kit M05, peinture et réorganisation par étages](59-m05-kit-paint-storeys.md) — composants procéduraux sur petits terrains, murs peints et matières natives, passage 5×5/2 vers 4×4/3.

[Petites façades M05 et collection JazzFrank](60-m05-small-jazzfrank.md) — compact sans réserve décorative, motifs sélectifs M3/M4/M6 et inventaire des 12 modules sources.

[Façades principales M05 et charpente](61-m05-front-compositions.md) — verrière en proue, portique industriel, galeries inclinées et couronnements à taille native.

[M05 : quatre faces et toiture](62-m05-wrap-roof.md) — compositions en retrait, ventilations groupées et corniches arrondies en poutres natives.

[M05 : compositions et appuis corrigés](63-m05-supported-compositions.md) — façades basses, suppression des fragments sur le toit, pieds de toiture et bardage natif des angles.

[Terrain et réserve pour l’habillage](64-terrain-cladding-reserve.md) — Auto, formats imposés, marges pour des façades complètes et refus sans modifier le plan.

[Toits composés et terrain minimal](65-roofs-compact-sizing.md) — Quatre toits M05, appuis, suppression des anneaux et correction du placement compact ; limites du routage natif détaillées.

[Blocs natifs sur un étage](67-native-blocks-single-storey.md) — Collecte haute, 60 minerais → 5 plaques en 5×5, réseau natif exportable et bibliothèque de blocs 2×/3×.

[Choix des blocs en Auto](68-auto-native-block-choice.md) — Huit machines pour 60 → 5 avec terrain libre, sans duplication de matériel à demi-cadence.

[Blocs natifs dans les trois densités](69-native-blocks-density.md) — Huit machines en Normal/Aéré aussi ; bus physiques adaptés à l’espacement.

[WebGL opaque et transparent](70-webgl-transparent.md) — Cache GPU pour les mouvements de caméra dans les deux modes, opacités et repli SVG.
