# Créateur manuel de blueprints — première version

**Priorité actualisée :** commencer sur un plan de 6 × 6 fondations, sans prérequis d'export natif ni de test en jeu. Voir [le périmètre actuel](19-paper-blueprint-6x6-plan.md). Les validations dans le jeu décrites ci-dessous sont reportées.

19 octobre 2026. Périmètre demandé : 1. ouvrir et visualiser ; 2. exporter une copie ; 2.2 créer machines, convoyeurs et câbles ; 2.3 vérifier le fonctionnement. Document de planification : aucune génération de blueprint n'est encore validée en jeu.

## Résultat visé

Une page « Créateur de blueprint » : partir d'un projet vide ou ouvrir un blueprint existant, poser des fondations et machines, choisir leurs recettes, tracer les convoyeurs, raccorder les câbles électriques, puis exporter un blueprint fonctionnel dans Satisfactory.

La fusion, l'agencement automatique et l'édition en direct sont reportés après cette première version. La création manuelle depuis une page vide fait bien partie de la cible : elle ne se limite pas à déplacer des modules préassemblés.

## Premier périmètre supporté

- Un niveau, grille et rotations par quarts de tour ; gabarit cible explicite, initialement Designer Mk.1.
- Fondation, fonderie, constructeur, coffre simple et poteau électrique de référence.
- Recettes solides prises en charge ; réglage des cadences après validation de la création des machines.
- Convoyeurs Mk.1 entre ports compatibles, d'abord droits puis avec un virage simple.
- Câbles électriques entre machines et poteau ; alimentation externe du poteau raccordée après placement en jeu.
- Déplacer, dupliquer, tourner, supprimer, annuler/rétablir et sauvegarder/rouvrir le projet local.

Les autres machines, ascenseurs, fluides, pentes complexes et bâtiments moddés seront ajoutés famille par famille. Mineurs et source électrique restent externes à la première scène d'essai.

## Étapes petites et testables

| Étape | Fonction livrée | Critère de passage |
| --- | --- | --- |
| 1 — Ouvrir | Lire un petit `.sbp` et sa configuration ; afficher objets et gabarit | Types, positions et rotations comparés au modèle de référence ; version inconnue signalée |
| 2 — Copier | Réexporter sous un autre nom sans édition | Relecture correcte ET copie chargée/placée en jeu avec ses liaisons ; original intact |
| 2.1a — Projet vide | Poser des fondations dans un gabarit | Déplacement, rotation, duplication et suppression fiables ; projet local rouvrable |
| 2.1b — Machines | Ajouter une machine depuis la palette, choisir sa recette et la dupliquer | Identités propres ; composants présents ; machine exportée et placée en jeu avec recette correcte |
| 2.2a — Convoyeur droit | Relier une sortie à une entrée | Géométrie et références réciproques valides ; transport réel d'objets en jeu |
| 2.2b — Virage simple | Tracer un raccord avec un point de passage contraint | Extrémités et courbe valides ; trajet impossible signalé ; transport vérifié en jeu |
| 2.2c — Électricité | Poser un poteau et câbler les machines | Connecteurs/réseau corrects ; machines alimentées après raccordement externe |
| 2.3 — Ligne complète | Exporter une petite ligne créée depuis la page vide | Placement, recettes, énergie, circulation et production attendue vérifiés en jeu |

La copie fidèle est le premier verrou : un écrivain binaire présent dans le code ne garantit pas encore un fichier accepté par le jeu. Chaque étape a sa propre vérification ; les tests ne sont pas repoussés à la fin.

## Scène d'acceptation

**Coffre de minerai → fonderie → constructeur → coffre de produit**, avec un poteau alimentant les deux machines.

La recette du constructeur consomme le produit de la fonderie. Les cadences et ressources initiales seront fixées pour rendre le résultat attendu calculable. Le poteau sera branché à une alimentation externe après placement.

Pour accepter la première version :

1. Le blueprint apparaît et se place dans le jeu, dans le gabarit prévu.
2. Les machines sont présentes, orientées et configurées correctement.
3. Les convoyeurs sont connectés aux ports et les objets atteignent le coffre final.
4. Les machines sont alimentées après branchement du poteau.
5. La production correspond aux recettes et cadences choisies, après stabilisation des tampons.
6. Sauvegarder puis recharger la partie conserve le fonctionnement.

Une relecture réussie par notre parseur ne prouve pas la compatibilité en jeu. Une prévisualisation correcte ne prouve pas la connexion ou l'alimentation.

## Interface

- **Gauche :** palette courte — fondation, fonderie, constructeur, coffre, poteau, convoyeur, câble.
- **Centre :** vue de dessus pour placer et raccorder ; aperçu en volume disponible.
- **Droite :** propriétés de l'objet sélectionné — position, rotation, recette, cadence supportée, ports et erreurs utiles.
- **Actions :** nouveau/ouvrir, sauvegarder le projet, annuler/rétablir, vérifier, exporter.

Pour un raccord : cliquer sur le connecteur de départ, puis sur celui d'arrivée ; les connecteurs compatibles sont mis en évidence. « Vérifier » distingue erreurs bloquant l'export, avertissements et points à vérifier en jeu. L'export utilise un nouveau nom et affiche le résultat et l'emplacement du fichier.

## Difficultés techniques à traiter séparément

**Machine :** créer ses objets et composants avec des valeurs cohérentes, pas seulement un type et une position. Les premiers adaptateurs s'appuieront sur de petits exemples vanilla construits en jeu, avec leur version enregistrée. Ces exemples sont des modèles techniques d'objet ; l'utilisateur peut les placer individuellement dans une scène vide.

**Convoyeur :** construire sa géométrie et ses références vers les deux ports. Un trait visuel ne suffit pas. Les segments droits précèdent les virages et ascenseurs.

**Câble électrique :** reconstruire les connecteurs et la cohérence du réseau. Test séparé avant la ligne complète.

**Placement :** disposer de dimensions et dégagements fiables pour les objets supportés. Les boîtes schématiques actuelles ne garantissent pas la constructibilité. Tester également dépassement de gabarit, port occupé, chevauchement et cohérence des identités après duplication/suppression.

## Réutilisation et dépendances

L'atelier partage catalogue, transformations, graphes et aperçu avec l'explorateur, mais conserve son propre modèle de projet. L'export est une action distincte ; aucune écriture dans les sauvegardes `.sav` n'est nécessaire.

Le parseur embarqué possède déjà `parseBlueprint`, `resaveBlueprint`, `parseBlueprintConfig` et `resaveBlueprintConfig` dans `external-tool/vendor/sat_sav_parse/sbp_parse.py`. Existence vérifiée dans le code ; aucun export du créateur n'est encore validé en jeu.

Les premières étapes restent externes : pas de passerelle en jeu ni d'Unreal Editor requis pour développer cet éditeur de fichiers. Les validations finales demandent le jeu et des références de versions compatibles. Une interface schématique suffit ; les modèles et textures du jeu ne sont pas nécessaires pour ce premier périmètre.

## Suite après la première version

Davantage de machines et de transports, puis fusion de blueprints, répétition de rangées et propositions de dispositions. Ces évolutions ne conditionnent pas la réussite du créateur manuel.

## Sources

- Parseur local embarqué : `sbp_parse.py` et README. [Versions de l'auteur](https://github.com/GreyHak/sat_sav_parse/releases).
- [Blueprints : format et placement](https://satisfactory.wiki.gg/wiki/Blueprint).
- [Designer : gabarits et restrictions](https://satisfactory.wiki.gg/wiki/Blueprints).

Ce document organise le travail ; cette étape ne lance pas l'implémentation du créateur ni des modifications dans la partie en cours.
