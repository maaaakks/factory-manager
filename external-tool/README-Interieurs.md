# Intérieurs habitables — première passe

Dans l’atelier : **Design → Intérieur → Aménager l’intérieur**, puis **Coupe intérieure** pour examiner le résultat. L’action conserve machines, recettes, horloges et réseaux, et peut être annulée. Après un déplacement de machine, un changement de terrain ou d’étage, l’ancien aménagement est retiré : utilisez à nouveau Aménager l’intérieur. L’export refuse les parcours périmés.

## Escaliers et enveloppe

Les éléments CatwalkStairs de la source native montent de 4 m sur une avancée de 4 m. Atlas utilise maintenant trois volées jointives pour atteindre sa galerie à 13 m ; Sylva en utilise deux pour sa terrasse à 9 m, puis deux autres avec des paliers protégés pour rejoindre les terrasses à 13 et 17 m. Leurs trémies suivent la longueur du bâtiment. Les ouvertures de terrasse et les paliers ont été déplacés en conséquence. L’aperçu utilise le même pas de 4 m.

La hauteur automatique d’Atlas et de Sylva dépend du haut des machines, avec une marge de 2,5 m et un minimum de 17 m pour la halle. Des cours de mur de 4 m sont retirés ou répétés ; aucun panneau natif n’est étiré. Sur l’usine témoin de huit machines, les sommets descendent à environ 21,6 m et 21,5 m. La couronne et la toiture remontent avec les étages nécessaires.

Pour plusieurs étages, une cage de circulation prend une bande libre de 8 m à gauche. Des escaliers de 4 m, des rampes de 2 m et, si nécessaire, quatre marches natives en poutres pour le dernier mètre rejoignent des paliers et passerelles. La bande de plancher correspondante devient une trémie. Une porte remplace le panneau de façade au passage du palier. Le confort exact de ces raccords reste à confirmer dans le jeu.

## Parcours, inspection, couleur et lumière

L’aménagement cherche un parcours continu avec un dégagement de 2,4 m et 2,7 m de hauteur, hors enveloppes des machines, structure et trajets logistiques connus. Il choisit des postes de visite proches des machines. Les postes sans accès possible sont signalés ; le calcul ne certifie pas la navigation réelle du personnage ni l’accès à chaque panneau de commande.

Les huit créations ont une palette de sol distincte, des zones d’inspection et des guides natifs affleurant le sol. Les guides utilisent des poutres peintes intégrées dans le plancher, avec leur dessus à 1 mm au-dessus de sa surface, et des longueurs limitées à 16 m. Les couleurs de plancher sont identiques dans l’aperçu et dans le SBP.

Les projecteurs existants d’Atlas sont réutilisés ; les autres créations reçoivent des projecteurs natifs. Des raccords muraux forment un circuit relié au réseau existant si un raccord est libre. Les positions électriques sont calculées depuis les extrémités mesurées dans les SBP sources, et les raccords sont vérifiés après export. La valeur de 6 MW par projecteur provient du powerInfo de la pièce source ; elle est incluse dans les consommations affichées. L’aperçu reste schématique et ne simule pas l’éclairage rendu par Unreal.

## Vérification

Huit cas à un étage : huit machines inspectables sur un parcours connecté, sans changement de production. Deux cas à deux étages : neuf postes, paliers et cage d’escalier. Parité JavaScript/Python de l’enveloppe, des circulations, des couleurs et des planchers pour les dix scènes. Atlas et Sylva : SBP construits et relus, escaliers au pas de 400 cm, circuit électrique réciproque, 23 convoyeurs et 13 élévateurs conservés.

Les fichiers locaux fournis sont des prototypes à replacer pour un contrôle en jeu. Les bâtiments déjà posés ne sont pas modifiés automatiquement.
