# Huit machines aussi en Normal et Aéré

Le plan observé après le nouveau signalement utilisait **Normal**, terrain Auto et étages Auto. Les corrections 67/68 réservaient encore le profil à huit machines au mode Compact. Le problème n’était pas attribuable au cache : un nouveau calcul Normal sélectionnait le profil étagé à seize machines sous-cadencées.

Le profil natif sur un étage est maintenant disponible dans les trois densités, pour minerai de fer → plaques renforcées jusqu’à 5/min, avec Bas ou Auto et terrain libre. À 60 → 5, il garde deux fonderies, cinq constructeurs et un assembleur.

| Densité | Sans réserve | Avec réserve | Réseau |
| --- | --- | --- | --- |
| Compact | 5×5 | 6×6 | 23 convoyeurs, 13 élévateurs |
| Normal | 6×6 | 6×6 | 26 convoyeurs, 13 élévateurs |
| Aéré | 7×7 | 8×8 | 26 convoyeurs, 13 élévateurs |

Normal ajoute 2 m entre les rangées de blocs et Aéré 4 m. Les réseaux internes des blocs restent rigides. Les bus externes sont reconstruits aux vrais ports, avec des descentes et des raccords explicites. Le nombre de machines ne dépend pas de cette aération. L’enveloppe et le coffre suivent l’implantation.

Un terrain imposé conserve sa contrainte stricte. Auto avec un 4×4 explicitement imposé et Haut utilisent toujours le profil étagé existant ; cette version ne crée pas un nouveau module étagé à huit machines. Les autres produits restent sur leur générateur existant.

Vérifications : 16 transformations/rotations de blocs 2×/3× ; 12 constructions natives et relectures SBP pour les trois densités à 0,2 et 5/min ; intégration Bas/Auto avec et sans réserve ; six exports et relectures avec habillage M05. Aucun fichier du jeu écrit pendant ces contrôles.
