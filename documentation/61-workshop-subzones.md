# 61 — Atelier : sous-zones de production lisibles

La génération et « Réorganiser » utilisent `subzones-v1`. Chaque sous-zone contient une ou deux machines de même recette, alignées dans la même direction et sur le même étage. Les paires de fonderies et de constructeurs partagent cette règle, y compris dans les chaînes d'assemblage. La recette standard des rotors provient du catalogue local du jeu et devient disponible dans le calculateur de l'atelier.

Chaque paire dispose de sa distribution et de sa collecte locales. Les raccordements entre sous-zones relient ces interfaces. Les étapes de fabrication se suivent, avec des allées entre rangées. Le mode Auto agrandit le terrain et privilégie un seul étage. Le choix explicite « hauteur » conserve les paires sur un même étage et répartit les étapes sur les étages autorisés. Les dimensions fixes trop petites sont refusées sans modifier le projet.

Le générateur ne sélectionne plus automatiquement l'ancien noyau calibré 32×32/3 étages pour les plaques renforcées. Les anciens projets et leur export calibré restent lisibles. Pour obtenir la nouvelle implantation d'un projet existant, utiliser « Réorganiser » ; aucun projet stocké dans le navigateur n'est remplacé automatiquement.

L'export natif essaie les raccordements directs des machines au lieu d'imposer une voie haute. Si un croisement exige des élévateurs, il essaie d'abord une voie locale à deux mètres au-dessus des ports, avec les contrôles existants des collisions, courbes et raccords. Les voies entre étages gardent leurs niveaux distincts. La politique concerne seulement les nouveaux plans `subzones-v1`.

## Vérifications reproductibles

Depuis external-tool :

- `node tests/check_workshop_subzones.cjs` génère 17 scènes dans `data/subzone-scenes.json` (ou le dossier `SUBZONE_OUTPUT`). Paires homogènes, dégagements, routage de toutes les liaisons, Auto à plat, étages explicites, formes, conservation des objectifs et refus atomique.
- `python tests/check_native_subzones.py` lit ces scènes (ou `SUBZONE_SCENES`), contrôle chaque chemin logique dans le graphe physique et réouvre le binaire `.sbp` écrit dans un répertoire de test temporaire. Vérifie également les croisements bas des plans à un étage.
- Régressions : `check_workshop_capacity.cjs`, `check_workshop_network.cjs`, `check_simple_planning.cjs`, `check_free_dimensions.cjs`, `check_native_project.py`.

Ces contrôles ne mesurent pas la production en jeu. Aucun fichier de sauvegarde ou dossier de blueprints du jeu n'est modifié. Les usines occupent davantage de terrain : c'est le compromis pour conserver des sous-zones et des accès lisibles.
