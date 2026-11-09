# Correction du gel de Chrome au chargement de l’atelier

19 octobre 2026.

## Cause reproduite

Le brouillon du navigateur externe contenait 120 lingots de fer/min en entrée ET en sortie. L’ancien affichage appelait `calculate()` automatiquement pour présenter un bilan, même sans action de génération. Ce calcul ne produisait aucune machine, donc aucun étage. La génération de logistique essayait alors d’ajouter un étage à partir d’une liste vide (`Math.max(...[])`), puis rappelait récursivement le placement avec une altitude invalide. Cela bloquait le thread de la page, y compris après rechargement puisque le même brouillon était restauré.

Une reproduction dans un processus Node isolé expirait après 1,2 seconde avant correction. Après correction, la même entrée se termine immédiatement par une erreur explicite.

## Correction

- `calculate()` refuse les entrées et sorties identiques pour une ressource, ainsi que les objectifs ne générant aucune machine.
- La génération de logistique vérifie la présence d’étages valides avant tout placement.
- Le bilan d’affichage utilise `demand()` pour développer les besoins sans recalculer toute l’implantation.
- Les trajets schématiques et la disposition du tampon sont conservés par version de projet au lieu d’être recalculés à chaque mouvement de souris.
- `/atelier?secours=1` ouvre une session dont le brouillon est stocké dans une clé distincte. Le brouillon normal et les projets enregistrés restent conservés ; un bouton permet d’exporter le brouillon habituel.

Le brouillon Chrome a été exporté par l’interface dans `C:/Users/YOUR_USER/Downloads/brouillon-atelier-sauvegarde.json` avant restauration normale. Aucun stockage navigateur n’a été effacé. Un nouvel onglet Chrome normal a repris les deux bâtiments et les objectifs d’origine avec le correctif.

## Validation

Tests de régression ajoutés à `tests/check_workshop_capacity.cjs` : cas exact entrée/sortie identiques et sortie minerai sans machine. Les tests de capacités, implantation, assistance et calculateur passent.

Dans Chrome externe : ouverture normale du brouillon, message d’erreur explicite après « Calculer et placer », clic dans la palette toujours actif, puis rechargement normal sans gel. Un onglet déjà pris dans la boucle de l’ancienne version peut nécessiter d’être fermé ; l’onglet nouvellement ouvert charge le code corrigé.
