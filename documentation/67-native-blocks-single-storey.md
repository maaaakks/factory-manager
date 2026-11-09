# Blocs natifs et collecte haute sur un étage

## Première chaîne intégrée

Le Calculator et « Réorganiser l’usine » utilisent maintenant un profil par blocs natifs pour **minerai de fer → plaques renforcées**, en **Compact / Rectangle / Bas**, de 0,2 à 5 plaques/min. À 5/min, l’entrée est 60 minerais/min.

- 2 fonderies, 2 constructeurs de plaques à 75 %, 1 constructeur de barres à 100 %, 2 constructeurs de vis à 75 %, 1 assembleur à 100 %.
- Un seul étage de production ; répartiteurs bas et fusions hautes, avec les élévateurs internes des blocs.
- Coffre de sortie et raccordement électrique complet : 4 prises murales, 11 câbles.
- 23 convoyeurs physiques et 13 élévateurs ; Mk.1 suffisant pour chaque liaison du cas 60 → 5.
- Terrain Auto : 5×5 sans réserve, 6×6 avec réserve d’habillage. Un 4×4 imposé est refusé sans modification du projet initial.
- Les recettes, débits, ports, chemins et capacités sont vérifiés avant le retour du profil depuis l’API. La vue native utilise ces mêmes chemins ; aucun nouveau routage approximatif à l’export.

L’organisation reprend les blocs de la référence `exemple_60mineraix5plaquesrenfor`. Sa liaison provisoire depuis l’entrée des vis vers l’assembleur est remplacée par une collecte depuis la fusion des vis. La sortie de l’assembleur est prolongée vers un coffre, au-dessus de son volume. Les machines de la référence sont correctement configurées pour le débit demandé.

## Bibliothèque réutilisable

Les sources SMELTERX2, SMELTERx3, CONSTRUCTORx2, CONSTRUCTORx3 et l’exemple sont copiées dans les données locales, avec empreintes SHA-256. Aucun original n’est modifié. `native_blocks.instantiate` applique une rotation/translation rigide à l’ensemble d’un bloc, conserve ses splines et têtes d’élévateurs, recrée les connexions internes et laisse les interfaces externes libres. Les recettes et cadences sont paramétrables.

Les blocs 2× et 3× passent les rotations 0/90/180/270°, les contrôles de raccords et la sérialisation SBP. **Le choix automatique entre 2× et 3× pour des chaînes arbitraires n’est pas encore branché.** Le profil sur un étage utilise actuellement les blocs 2+2+1+2 de la référence. Les autres chaînes conservent leur générateur ; le profil étagé existant reste distinct.

La référence récente utilise un encodage de propriétés natif plus récent que les gabarits de l’exporteur. Sa géométrie est reconstruite sur les gabarits pris en charge ; les métadonnées binaires de versions différentes ne sont pas mélangées.

## Validation

- 40 contrôles JavaScript réussis, dont l’intégration Calculator, la persistance, la réserve, les interfaces et le refus atomique d’un terrain trop petit.
- 16 tests de blocs 2×/3× : rotations, extrémités, écriture et relecture SBP.
- Quatre exports complets sur un étage (5×5/6×6, 0,2 et 5 plaques/min) : débits équilibrés, vrais raccords, écriture/relecture SBP ; une modification détachant un module est refusée.
- Export et relecture des projets Calculator avec habillage M05 en 5×5 et 6×6.
- Les profils natifs étagés et les quatre nouvelles compositions de toit restent validés.
- Dans l’interface de test : génération via le Calculator puis « Vérifier et voir les convoyeurs natifs » affiche « Réseau natif prêt pour l’export ».

Aucun fichier écrit dans les blueprints du jeu pendant ces contrôles. Fonctionnement et dégagements en jeu restent à vérifier par placement réel.

## Utilisation

Recharger l’application, choisir Compact, Rectangle et Bas puis recalculer ou réorganiser le plan. Le brouillon existant n’est pas remplacé automatiquement. Utiliser la vérification native avant l’enregistrement SBP habituel.
