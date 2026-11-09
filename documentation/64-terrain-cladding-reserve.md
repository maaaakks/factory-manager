# 64 — Terrain imposé ou automatique et réserve d'habillage

Le terrain est désormais dans le panneau **Design → Implantation**, au-dessus de la densité. Le sélecteur de la barre supérieure est retiré. Il propose Auto, 4×4, 5×5, 6×6 et Sur mesure (largeur/profondeur en fondations). Le calculateur expose aussi son choix de terrain directement dans les options d'implantation.

**Auto** autorise le générateur à chercher un autre terrain. Lors d'une réorganisation avec réserve, il essaie d'abord les dimensions actuelles puis les candidats automatiques, par pas d'une fondation. **Un format choisi est une contrainte** : le générateur ne peut pas l'agrandir silencieusement. Une proposition impossible laisse le projet ouvert intact. Le format imposé et la réserve sont conservés dans le JSON après une réorganisation réussie.

## Garder de la place pour l'habillage

Cette case est activée lorsqu'on choisit Aéré ; Compact la désactive. Elle reste modifiable indépendamment pour le calcul suivant. La réserve s'applique au placement, pas seulement au rendu des murs : priorité aux marges, enveloppe attachée au terrain prévu, contrôle des bâtiments et des trajets disponibles près des limites, puis absence d'ouvertures imposées par la production dans l'habillage actuel. Sans style actif, une enveloppe de contrôle est utilisée sans ajouter l'habillage au projet.

Si la réserve ne suffit pas, Auto continue avec un terrain plus grand. En terrain imposé, il faut agrandir explicitement, changer l'implantation ou décocher la case. L'option protège les façades du style calculé avec les enveloppes schématiques de l'outil ; elle ne garantit pas toutes les collisions visuelles du moteur du jeu, ni la place nécessaire à tout futur style.

Le terrain choisi ne désactive plus implicitement les marges. Les modules natifs compacts peuvent aussi demander une réserve : ils quittent alors le 4×4 si nécessaire. En compact sans réserve, le comportement de production maximale est conservé.

Les changements se calculent avec **Réorganiser l'usine**. Le choix du terrain ne redimensionne pas immédiatement le projet ouvert. Le nombre et la disposition des étages restent réglés séparément.

## Validation

- Cas réel : 120 minerais de cuivre/min vers 120 lingots/min, Aéré sur un étage : un terrain initial 5×5 devient 6×6 en Auto, avec façades complètes.
- Même cas en 5×5 imposé : refus sans modifier le projet initial. En 6×6 imposé : réussite et conservation de la contrainte dans le JSON.
- Chaîne native fer → plaques renforcées : 4×4 compact sans réserve conservé ; 4×4 avec réserve refusé ; Auto avec réserve agrandit et conserve le réseau natif.
- Construction et relecture des deux SBP de référence en répertoire temporaire, vérification des connexions. Aucun fichier du jeu n'est écrit pendant ces tests.
