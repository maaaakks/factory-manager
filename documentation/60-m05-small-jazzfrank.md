# 60 — Petites façades M05 et collection JazzFrank

## Collection source complète

Le catalogue public de [JazzFrank](https://satisfactoryblueprints.com/author/jazzfrank), consulté le 21 octobre 2026, présente 12 blueprints. Les 12 sources étaient déjà téléchargées dans `external-tool/data/m05/`. Leur présence, leur empreinte SHA-256 et leur nombre d’acteurs natifs ont été vérifiés à nouveau. Aucun nouveau téléchargement n’a été nécessaire.

| Module | Source locale | Acteurs | SHA-256, préfixe |
| --- | --- | ---: | --- |
| [C1](https://satisfactoryblueprints.com/blueprint/12c74a4a-c97e-4ad3-b256-ac3606ef8e0e) | `C1.sbp` | 460 | `423969a9490e` |
| [C2](https://satisfactoryblueprints.com/blueprint/85e2c777-c25c-413f-af92-f1233aa8477e) | `C2.sbp` | 447 | `73f22047cbb6` |
| [M1](https://satisfactoryblueprints.com/blueprint/f92bbb4b-6f78-4f54-ae50-46c3aa404924) | `M1.sbp` | 300 | `e38908f29fd4` |
| [M2](https://satisfactoryblueprints.com/blueprint/22a87086-8189-4ae2-9831-ce11789a00bd) | `M2.sbp` | 276 | `d88ab4cbe193` |
| [M3](https://satisfactoryblueprints.com/blueprint/f5aed4ec-e644-40e5-86dc-4e8773dadc17) | `M3.sbp` | 311 | `9ea3a3ecedd6` |
| [M4](https://satisfactoryblueprints.com/blueprint/1b46b980-a3ac-4a10-9178-6f5c51a5753c) | `M4.sbp` | 266 | `60b11e41aea0` |
| [M5](https://satisfactoryblueprints.com/blueprint/c255f7b1-4337-4197-b6f6-56223b05e4a1) | `M5.sbp` | 289 | `4cc3094d3bcf` |
| [M6](https://satisfactoryblueprints.com/blueprint/72feb1aa-c54a-4aa5-92fe-779b98d3dd8e) | `M6.sbp` | 302 | `ab23d6749031` |
| [IN1](https://satisfactoryblueprints.com/blueprint/0d9eb2cf-7d8a-4f90-a315-f18abd310b8b) | `IN1.sbp` | 100 | `e126974aaacb` |
| [IN2](https://satisfactoryblueprints.com/blueprint/0042882e-40de-4713-baa6-a64a3a26295c) | `IN2.sbp` | 158 | `e179028cc982` |
| [IC1](https://satisfactoryblueprints.com/blueprint/deffb913-201d-4b84-9575-26aeb5d03ad7) | `IC1.sbp` | 284 | `1f1c3b4d7e9f` |
| [IC2](https://satisfactoryblueprints.com/blueprint/c4ae7a98-699a-4aab-af31-61f99cfd71f0) | `IC2.sbp` | 316 | `f20020d3fad3` |

Le manifeste `manifest.json` contient les descriptions des pièces et leurs poses ; `catalog.json` contient les liens et les empreintes complètes. Les fichiers SBP originaux restent intacts et attribués à JazzFrank. La collection compte 3509 acteurs.

## Ce qui est utilisé par le générateur

- **Modules de JazzFrank** : l’ancien assemblage natif complet C1/C2 + M1–M6 + IN1, sans réduction des dimensions. IC01/IC02 et IN02 sont bien présents dans la bibliothèque mais ne sont pas encore assemblés automatiquement.
- **Kit procédural** : grammaire adaptée aux terrains 4×4, 5×5, 6×6 et rectangulaires. Ce sont des compositions inspirées des motifs, pas des copies miniatures des modules complets. Les vitrages utilisent leurs classes natives ; les ventilations sont clonées depuis les véritables M3/M4/M6.

Le kit choisit une façade accentuée ou deux voisines. M3 emploie une baie centrale en retrait et des bandeaux ; M4 une tour vitrée et des épaules en retrait ; M6 des galeries sur deux registres. Les coins vitrés et certains retraits supérieurs rappellent C1/C2. Les autres faces gardent un rythme plus sobre. Les retraits modifient le contour réel, avec fermeture des terrasses et des sous-faces ; une cellule occupée par une machine ou traversée par la logistique est conservée.

**Variante** change la famille du motif et ses faces. **Rafraîchir les murs** renouvelle sa composition. Aucun de ces boutons ne déplace les machines. Les détails originaux ne sont pas encore tous convertis en règles procédurales : posséder les 12 sources ne signifie pas que leurs 12 grammaires sont intégralement reproduites.

## Compact sans réserve décorative

Le placement compact donne la priorité à la production même si le plan porte un style architectural. Les dimensions automatiques peuvent commencer à 32 m au lieu du minimum précédent de 40 m. La chaîne calibrée fer → plaques renforcées essaie explicitement son emprise 32×32 avant les formats plus grands.

Les dégagements physiques du réseau, les vrais ports, les courbes et les élévateurs restent vérifiés. Un terrain explicitement plus grand conserve sa taille ; le noyau calibré de 32 m peut donc y laisser de l’espace inutilisé. Cela ne constitue pas une réserve obligatoire pour les façades. Un style qui nécessite une façade profonde doit s’adapter aux espaces libres ; il ne pousse pas implicitement les machines vers le centre. Les modules JazzFrank complets restent une option distincte, avec leur trame et leur réservation originales.

## Import d’un blueprint existant

L’import utilisateur de l’atelier accepte actuellement le **projet JSON Factory Manager**. L’export `.sbp` est disponible, mais l’import générique `.sbp` n’est pas branché. Le lecteur utilisé pour les 12 sources est une brique technique, pas un import complet de machines/réseaux arbitraires. Pour décorer un blueprint natif, il faudra conserver ses acteurs et leurs connexions, reconstruire un volume d’occupation, puis ajouter l’habillage sans déplacer la production.

## Vérifications

- 12 sources : empreintes complètes, lecture binaire et nombre d’acteurs.
- 18 petites scènes, 3 formats × 6 variantes : retraits réels, une/deux faces accentuées, cellules occupées conservées, fermeture des terrasses et sous-faces, parité exacte JavaScript/Python et réouverture binaire.
- Chaîne fer 60/min → plaques renforcées 5/min : compact automatique 4×4/3 étages avec et sans habillage, production identique ; 54 convoyeurs et 21 élévateurs natifs conservés.
- Chaîne cuivre 60/min → lingots 60/min : compact automatique 4×4 avec un réseau natif validé.
- Suites JavaScript existantes, anciennes surfaces M05, 36 variantes de familles natives et chaîne calibrée 120→10 : vérifiées.
- Navigateur isolé : import JSON d’une scène 4×4, affichage opaque, passage de la variante 2 à la variante 3. Le projet ouvert sur le port 8765 n’a pas été remplacé.

Ces contrôles ne sont pas un essai en jeu. Aucun fichier n’a été écrit dans les dossiers de blueprints du jeu pendant les tests.
