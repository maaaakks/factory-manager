# Calculateur et design simplifiés

## Interface

Le calculateur présente d’abord les entrées/sorties, puis trois choix illustrés :

- **Densité : Compact / Normal / Aéré**.
- **Forme : Rectangle / Allongé / Découpé**.
- **Étages : Bas / Auto / Haut**.

Les ressources existantes restent visibles ; le formulaire d’ajout est replié lorsque des sorties sont déjà définies. Les dimensions sont automatiques par défaut. Les tailles fixes, dimensions sur mesure, limite d’étages, écart entre planchers et règles de génération restent dans **Réglages avancés**. La hauteur personnalisée est explicitement la limite totale du bâtiment ; une fondation représente 8 × 8 m au sol. Aucun habillage n’est appliqué par défaut.

Le design reprend les mêmes intentions dans un onglet **Implantation**. **Réorganiser l’usine** remplace les positions des machines, les étages, les convoyeurs, les élévateurs et les câbles depuis les objectifs du projet. Le nom, l’identité, le tampon, la peinture, les matières et la famille architecturale sont conservés. L’opération est annulable. Il s’agit d’un nouveau placement : les positions manuelles ne constituent pas des contraintes fixes.

L’ancien onglet Sols est remplacé par un bouton **Sols dans la barre du design**, avec matière, planchers intermédiaires et rafraîchissement de matière. Les façades montrent le catalogue et les boutons de variation/rafraîchissement ; les descriptions, déverrouillages et réglages précis passent dans **Détails du style**.

**Éléments opaques** est dans les calques, synchronisé avec le menu de la fenêtre 3D. L’élévation est retirée de l’interface ; la perspective conserve rotation et zoom à la souris.

## Placement et contraintes

Le module partagé `dist/workshop-planning.js` est utilisé depuis un Web Worker. La recherche ne bloque pas la souris ni la vue 3D. Elle essaie au plus quatre formats automatiques et est interrompue après 20 secondes. Les erreurs, annulations et changements concurrents du projet conservent le plan courant.

- Bas impose un seul étage ; Haut répartit la chaîne sur les étages disponibles en conservant l’ordre de transformation ; Auto cherche un réseau complet.
- Allongé utilise une emprise de rapport 2:1 et replace effectivement les machines.
- Découpé réserve une cour vide en L. Le placement des machines, des poteaux et de la logistique, les trajets du plan, les fondations, les variations de façades et le routage natif respectent cette zone. Les formats automatiques prévoient davantage de place pour cette forme.
- Le format manuel est une contrainte stricte ; aucun agrandissement silencieux après son échec. Le format automatique ne dépend pas des machines déjà présentes dans le projet.
- Les réseaux génériques prévoient une seconde colonne logistique si nécessaire, un dégagement pour les virages et une réserve au-dessus des machines. L’encombrement du coffre est celui de l’export natif, 5 × 11 m. Les têtes schématiques des élévateurs sont orientées pour ne plus déboucher dans les répartiteurs voisins.
- Les nouveaux plans génériques ont un sol bas plein. Les dalles intermédiaires reçoivent les réservations nécessaires lors de leur conversion en sols pleins.
- Les identifiants des éléments générés sont renouvelés afin de ne pas entrer en conflit avec ceux des bâtiments conservés dans le tampon.

Les modules de fer vers plaques renforcées restent utilisés pour les formes rectangulaires sur plusieurs étages lorsqu’ils conviennent. La densité ajuste alors les dégagements de ces modules natifs. Les autres implantations utilisent le placement générique.

Le M05 garde ses contraintes réelles de trame et de hauteur. Découpé est désactivé pour une réorganisation M05 ; appliquer M05 à un autre plan remet la forme à Rectangle et adapte le terrain. Une combinaison incompatible avec ses 30,6 m de volume utile est refusée.

## Limite de validation

Le panneau distingue **Réseau natif** et **Réseau estimé**. Un placement générique complet dans l’atelier ne prouve pas que tous ses raccords peuvent être reproduits aux ports du jeu : **Vérifier et voir les convoyeurs natifs** demeure la validation avant export. Les gros réseaux génériques peuvent encore être refusés, en particulier lorsqu’un port ne laisse pas de trajet physique libre. Aucun contournement des erreurs d’export n’est ajouté.

## Vérifications

- Six plans cuivre : Rectangle/Allongé/Découpé × Bas/Haut, dimensions automatiques, un/deux étages, entrées/sorties, convoyeurs et électricité.
- Export natif puis relecture binaire de ces six plans ; vérification des raccords, réservations et trajets hors de la cour.
- Conservation du nom/tampon, absence de mutation de la source et refus atomique d’un terrain impossible ou d’une forme M05 non prise en charge.
- Régression des tests JavaScript, des dimensions libres, des élévateurs génériques et des six assemblages natifs M05.
- Essais navigateur : calcul en arrière-plan ; réorganisation de 120 minerais → 10 plaques renforcées en longueur sur un étage ; calcul rectangulaire Normal sur modules natifs, puis prévisualisation de ses 54 convoyeurs et 21 élévateurs ; changement de matière ; synchronisation des cases opaques ; menus et perspective sans élévation.

Les vérifications ne modifient aucun fichier de sauvegarde du jeu. L’acceptation des formats XL et le fonctionnement en jeu restent à tester en jeu.
