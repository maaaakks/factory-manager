# Usine de référence, architecture et rôles

Mise à jour du 18 octobre 2026.

## Ajouts effectifs

- Filtres séparés : murs/fenêtres/portes, fondations/rampes, toitures, décoration/éclairage/panneaux, poutres/passerelles/escaliers. Les supports fonctionnels de convoyeurs et tuyaux ne sont pas traités comme des murs architecturaux.
- Bouton « Délimiter une usine » : glisser un rectangle sur la carte, selon les calques et le filtre d'altitude actuels. Seules les origines visibles dans ce rectangle entrent dans la sélection. Pas de sélection par intersection de volume.
- Fiche nommable : nombre de machines et convoyeurs, connexions de frontière, ports ouverts présents, dimensions du rectangle et recettes enregistrées.
- Bouton « Cadrer cette usine » ; les autres constructions restent visibles en atténué.
- Suggestion de rôle fondée sur les noms des recettes : une matière explicitement nommée, plusieurs matières, fabrication de fils/câbles, production unique ou rôle indéterminé.
- Libellés simplifiés pour les recettes ; traduction de quelques recettes courantes. Les noms internes complets ne sont plus utilisés comme texte principal.

Les rôles sont des propositions. Une recette de fil ne prouve pas une alimentation en cuivre, et un nom contenant Biofuel ne signifie pas pétrole. L'outil ne déduit ni les recettes quantitatives ni les débits de leurs libellés.

## Référence utilisateur

L'utilisateur désigne une usine sur une capture, qu'il considère optimale, et pense qu'elle fabrique du cuivre. Le produit et les limites exactes restent à confirmer. Ne pas transformer cette hypothèse en une vérité technique ni assimiler une zone arbitraire de test à l'usine entourée.

La sélection rectangulaire permet à l'utilisateur de retrouver son périmètre. Dans cette version, elle reste en mémoire et disparaît au rechargement ou à l'ouverture d'une autre sauvegarde. Un convoyeur peut traverser la zone sans être inclus si son origine se trouve dehors. Vérifier les liens de frontière avant d'analyser la production.

## Étape suivante : proposer des ateliers

Pré-découpage automatique non implémenté dans cette mise à jour. Il doit produire des candidats, pas imposer des frontières.

1. Regrouper les machines proches par étage/altitude et continuité locale du transport.
2. Traiter les longues liaisons entre secteurs comme des interfaces candidates, et les stockages comme frontières possibles.
3. Comparer les recettes et les produits pour proposer un rôle et expliquer les indices.
4. Signaler les ambiguïtés : ateliers imbriqués, longues chaînes de convoyeurs courts, stockages partagés, bâtiments superposés, composants non sérialisés.
5. Donner une action « Accepter », puis ajout/retrait d'objets et arrêt explicite. Afficher pourquoi un objet est inclus.
6. Sauvegarder les périmètres hors du .sav avec une identité de sauvegarde et des contrôles de membres manquants.

La distance seule ne définit pas une usine. La connexité seule non plus : un réseau peut relier plusieurs secteurs. Les recettes aident à proposer des rôles, mais la matière réelle et les sorties exigent des données de recettes et des connexions validées.

## Avant l'optimisation

1. Confirmer le périmètre de l'usine connue.
2. Identifier ses produits, recettes, machines et paramètres explicites.
3. Ajouter un catalogue de recettes/capacités lié à la version du jeu.
4. Calculer les consommations/productions théoriques ; demander les hypothèses de valeurs absentes.
5. Comparer aux chiffres attendus de l'utilisateur.
6. Créer un défaut contrôlé dans une copie ou un modèle de test (p. ex. capacité de bande réduite) et vérifier qu'il est détecté.
7. Seulement ensuite proposer des améliorations d'une autre usine.

L'usine de référence n'est pas déclarée optimale par le logiciel. Elle sert d'exemple connu pour vérifier l'explication et les calculs.

## Vérification de cette mise à jour

- Syntaxes JavaScript/Python vérifiées.
- Import réel et contrôles HTTP précédents repassés : 2 098 constructions / 2 565 ports dans le format 52, format 60 vide lu correctement, import binaire et fichier invalide testés, hashes des deux originaux inchangés.
- Les nouveaux filtres sont présents dans le navigateur, y compris avec compteur zéro. La sauvegarde jojo contient 2 objets classés murs, 2 fondations et 19 éléments décoratifs selon les règles actuelles ; pas de promesse de catalogue exhaustif de tous les mods.
- Glisser un rectangle crée une fiche et un périmètre ; test sur 357 objets / 63 machines. Les recettes multiples sont affichées et le rôle reste proposé. Autre zone de test sans recette : rôle indéterminé.
- Les dimensions représentent la zone dessinée, pas l'empreinte des machines.

Le prochain test doit porter sur le rectangle exact de l'usine entourée, validé par l'utilisateur.
