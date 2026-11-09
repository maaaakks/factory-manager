# Sélection multiple dans l’atelier

En mode Sélectionner / déplacer (F), glisser depuis une partie vide du plan ou sa marge dessine un rectangle. Les objets dont l’enveloppe touche l’intérieur du rectangle sont sélectionnés, dans les deux sens de tracé. Seuls les objets de la tranche d’étage affichée sont concernés.

Shift+clic ajoute ou retire un objet. Shift+glisser sur le vide ajoute une zone à la sélection existante. Un clic simple sur un objet extérieur à la sélection remplace celle-ci ; un glissement depuis un objet déjà sélectionné déplace tout le groupe. Un clic simple sur le vide efface la sélection.

Le déplacement applique le même décalage XY à tous les objets choisis, en conservant les distances relatives. Les collisions sont vérifiées sur le projet complet : la position libérée par un objet du groupe peut être occupée par un autre. Si un membre dépasse le volume ou heurte un objet tiers, aucun déplacement n’est appliqué. Les liaisons conservent leurs références et leur tracé est recalculé comme auparavant.

Suppr, Retour arrière hors des champs de saisie ou « Supprimer la sélection » retire les objets et les liaisons qui leur sont attachées. Ctrl+Z annule le déplacement ou la suppression en une seule opération et restaure la sélection. La sélection et l’étage courant sont conservés dans le brouillon local. Les anciens brouillons à sélection unique restent lisibles.

Shift est désormais réservé à la sélection et ne tourne plus les machines. R conserve la rotation, y compris avant la pose. Rotation et duplication restent limitées à un seul objet dans cette tranche.

Validation automatisée : rectangle dans les deux sens, filtrage par étage, déplacement atomique à travers les anciennes positions du groupe, refus des collisions et débordements, suppression et nettoyage des liaisons. Suites atelier, formats, assistance et calculateur réussies.

Validation navigateur : rectangle sélectionnant deux constructeurs, déplacement collectif d’un mètre, annulation, ajout puis retrait d’un troisième avec Shift+clic, refus d’un déplacement sur les assembleuses, suppression de deux objets (14 → 12), annulation (12 → 14), sauvegarde et restauration de la sélection. Les positions finales de l’exemple ont été rétablies avant sauvegarde.
