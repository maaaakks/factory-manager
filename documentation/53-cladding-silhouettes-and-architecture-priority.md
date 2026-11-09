# 53 — Habillage, silhouettes et priorité Architecture

20 octobre 2026. Vérifications locales, aucun nouveau test en jeu.

## Un seul calque Habillage

Dans l'explorateur (carte et volume 3D), l'atelier et le design, **Habillage** regroupe murs, fenêtres, toitures, éléments décoratifs et structures décoratives. Dans l'explorateur, cela inclut les catégories poutres/passerelles/escaliers existantes. Les sols, machines, logistique, convoyeurs et électricité restent des calques séparés selon la vue.

Les catégories internes restent distinctes pour la couleur, l'analyse et l'export. Les compteurs sont additionnés dans le contrôle commun. Les anciens réglages de calques de l'atelier sont migrés ; une sélection partielle de catégories d'exploration apparaît comme un état intermédiaire du contrôle Habillage.

## Silhouettes réellement différentes

Le catalogue compte **11 familles dans 5 catégories**. La nouvelle catégorie **Volumes & cours** contient :

- **Pavillons en L** : deux ailes et une terrasse.
- **Cour industrielle** : contour en U et cour ouverte.
- **Atelier en croix** : retraits plus profonds aux quatre coins.

Les autres familles alternent aussi entre plusieurs contours et formes de toit. Les variantes font évoluer ces paramètres dans le langage de leur famille, avec leur palette et leurs ouvertures. Le moteur conserve les cellules occupées : il ne retire pas une machine pour imposer artificiellement la forme annoncée. Un plan rempli peut donc limiter ou empêcher les retraits. Les convoyeurs physiques et les courbes natives sont pris en compte pour éviter de couper leur trajet lors de ces nouveaux retraits.

Les découpes suivent la grille de 8 m, avec des angles droits en retrait ; les façades diagonales à 45 degrés ne sont pas encore implémentées. Le contour peut conserver des cellules supplémentaires autour de la production existante.

Les planchers supérieurs suivent le contour effectif afin d'éviter les dalles et cadres flottant au-dessus d'une cour retirée. Le sol du rez-de-chaussée reste une terrasse. Les masques dérivés sont identiques dans l'aperçu et dans l'export ; les données de planchers du projet restent conservées, et retirer le design restaure leur enveloppe complète.

## Des toits distincts

- **Lanterneau surélevé** : bande centrale plus haute de 4 m, parois vitrées verticales, toits plus bas de part et d'autre.
- **Sheds industriels** : pentes orientées dans le même sens et relevés verticaux à chaque travée.
- **Pentes alternées**, terrasse plane et compositions de verrières existantes.

Les nouveaux éléments utilisent les pièces natives déjà prises en charge. Les relèvements sont simplifiés quand la hauteur disponible ne suffit pas. Un style ne peut pas dépasser le volume du designer. Le cache de géométrie architecturale évite de recalculer les façades à chaque mouvement de caméra.

## Marges et priorité de génération

Le calculateur propose **Architecture** ou **Production**.

**Architecture**, sélectionnée par défaut dans l'interface, réserve une bande de 4 m en périphérie avant placement, conserve au moins 4 m entre les machines génériques et espace davantage la logistique. Les coffres de sortie utilisent le côté opposé au rail d'entrée pour dégager les vrais ports. Les trajets schématiques respectent la bande réservée. Le style de l'enveloppe est choisi avant génération et appliqué au résultat.

Le calculateur démarre en 5×5, compatible avec la marge des modules calibrés de 32 m. Les modules 120 minerais de fer → 10 plaques renforcées demandent au moins 5×5 dans ce mode ; le 4×4 reste disponible en priorité Production. Les autres chaînes restent soumises aux limites du placement et du routage.

Sur un projet existant, **Réserver la marge · agrandir si nécessaire** centre le plan puis essaie les formats supérieurs jusqu'à obtenir des façades sans panneaux manquants. Les distances relatives et les réseaux sont conservés. Si le 6×6 ne suffit pas, le projet est gardé et le problème est signalé. Cette action passe par l'historique Annuler.

Il s'agit d'une priorité de place et d'une enveloppe adaptée aux volumes libres. **Le solveur ne remplit pas encore une forme imposée à l'avance.** La prochaine étape serait : choisir un masque architectural, y réserver circulation et gaines, puis placer et router toute la production à l'intérieur, quitte à augmenter les étages ou réduire les débits. Cette distinction doit rester visible dans les promesses du produit.

## Bâtiments sur un étage

Les familles industrielles et vitrées autorisent maintenant du vitrage au rez-de-chaussée sur les volumes bas ; le socle plein ne masque plus systématiquement l'effet du style. Les motifs de bandeaux gardent un niveau vitré lorsque le bâtiment est court.

Les nouvelles générations donnent accès aux familles du catalogue créatif. Pour les anciens projets restreints par leurs packs déclarés, **Tous les styles · bac à sable** est visible à côté du catalogue. La progression réelle de la sauvegarde n'est toujours pas importée automatiquement ; les packs restent un réglage d'auteur.

## Vérifications

- 132 scènes de style : 11 familles, trois formats, plusieurs variantes, bornes, persistance et vitrages des volumes courts.
- 33 scènes JS/Python et exports binaires relus, avec contrôle des masques de planchers ; variantes sur le plan calibré de plaques renforcées conservées.
- Contrôles dédiés L/U/croix, protection des machines et convoyeurs, toits en sheds et lanterneaux, réservation de marge atomique et refus sans mutation quand le 6×6 est insuffisant.
- Génération navigateur : **60 minerais de cuivre/min → 60 lingots/min sur un étage**, priorité Architecture, style Campus vitré, façade complète et entrée.
- Le précontrôle natif a révélé un manque d'espace aux ports du réseau générique. Correction : davantage de dégagement et séparation du rail d'entrée et des coffres de sortie. Le test natif vérifie les convoyeurs, élévateurs de service, géométrie de l'habillage exporté et relecture du fichier.
- Vérification des calques dans la carte, le volume 3D de l'explorateur et le design de l'atelier.

Les exports de test utilisent des dossiers temporaires ; le précontrôle HTTP ne sauvegarde aucun blueprint dans le jeu. La réussite des tests locaux ne remplace pas une validation du rendu et du fonctionnement en jeu.
