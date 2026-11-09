# Auto : préférer le montage adapté au débit

Le projet exporté depuis le navigateur présentait bien 60 minerais → 5 plaques, Compact, Rectangle, Étages Auto et terrain Auto. Il utilisait le profil étagé 120 → 10 à demi-cadence : quatre fonderies et deux assembleuses à 50 %, dix constructeurs, trois niveaux. Le profil sur un étage de la version 67 n’était sélectionné qu’avec Bas.

En Compact/Rectangle, jusqu’à 5 plaques renforcées/min depuis le minerai de fer, avec **étages Auto et terrain Auto**, le générateur essaie désormais le profil à huit machines avant le profil étagé surdimensionné. Le réglage affiché reste Auto ; le résultat choisit un seul étage de production.

- Sans réserve d’habillage : 5×5, deux fonderies à 100 %, cinq constructeurs, un assembleur à 100 % pour 60 → 5.
- Avec réserve : 6×6 et façades complètes.
- Bas garde le même comportement natif vérifié.
- Un terrain 4×4 explicitement imposé avec Auto conserve le profil étagé existant. Haut et les demandes supérieures à 5/min conservent également leur profil existant. Cette correction ne crée pas un nouveau module étagé à huit machines.

Les 40 contrôles JavaScript passent. Le test d’intégration couvre maintenant Bas et Auto, avec/sans réserve, la conservation du projet initial et le terrain imposé. Le cas ouvert dans le navigateur a été exporté avant réorganisation dans `outputs/before-auto-68.factory-blueprint.json`.

Le serveur lit les fichiers statiques à chaque requête avec Cache-Control: no-store ; aucun changement backend ni redémarrage nécessaire pour cette correction de sélection. Aucun enregistrement dans les fichiers du jeu effectué.
