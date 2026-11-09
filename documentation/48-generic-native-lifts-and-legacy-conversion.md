# Export des élévateurs personnalisés et conversion des anciens plans

## Élévateurs génériques

L’exporteur générique matérialise désormais un lien entre étages muni d’un `via` en deux convoyeurs et un élévateur natif. Les six rangs sont disponibles, en montée comme en descente. Un élément Élévateur explicitement relié par une entrée et une sortie est également accepté. Un élévateur ne sert jamais de répartiteur : chaque liaison reçoit ses propres ports et, si nécessaire, sa propre colonne dans la zone réservée.

Le corps et les propriétés sérialisées proviennent de l’élévateur natif déjà utilisé par le test vertical. L’origine porte ConveyorAny0 ; mTopTransform définit la translation positive ou négative vers ConveyorAny1 et l’orientation de la tête de sortie. Les références sont réciproques et les extrémités des splines doivent coïncider avec les ports après écriture/relecture.

Le routeur cherche les accès aux vrais ports, évite les enveloppes dures et les convoyeurs déjà placés et peut réserver une voie supérieure avec deux élévateurs de service. Une recherche bornée qui échoue n’est pas une preuve d’impossibilité universelle. Les tracés manuels à points de passage restent hors du périmètre de cet export.

Les entrées/sorties schématiques deviennent des extrémités libres de convoyeurs à raccorder en jeu. Les coffres restent des bâtiments physiques. Des dalles entières sont omises lorsqu’une colonne traverse un plancher ; ce ne sont pas encore des traversées de sol natives percées à la taille du convoyeur. Les cadres ajourés sont exportés comme cadres. Le volume dur du constructeur utilise les 6 m décrits par les Docs locales ; les dégagements souples ne sont pas assimilés à une boîte dure de 8,5 m.

## Préparation dans l’interface

Importer / Exporter → Vérifier et voir les convoyeurs natifs appelle un précontrôle sans écriture dans le dossier du jeu. En cas de succès, la 3D montre les trajectoires physiques, les colonnes et les réservations de plancher effectivement exportées. Modifier le projet invalide cet aperçu. Les erreurs disposent d’un détail repliable par trajet ; le conseil imposant les modules compacts est supprimé.

## Ancien projet signalé par l’utilisateur

La copie JSON du projet ouvert contient 26 objets, quatre gaines partagées et 29 liens logiques. Ses objectifs sont **120 lingots de fer/min**, et non 120 minerais, vers **10 plaques renforcées/min**, en 4×4. Certains raccords ne trouvent pas de passage dans cette implantation après matérialisation. Le code ne transforme pas ces liens en convoyeurs traversant les bâtiments.

Le précontrôle propose alors Convertir le plan en réseau natif. La première conversion automatique prend en charge minerai ou lingots de fer → plaques renforcées, de 0,2 à 10/min, avec les recettes standard et le rapport 12:1. Les autres recettes bénéficient des élévateurs génériques mais pas de cette reconstruction automatique spécialisée.

La conversion remplace l’implantation des machines et réseaux par des modules à raccords calibrés, conserve objectifs, format, identifiant, nom, couleurs, habillage et tampon et passe par l’historique normal : Annuler restaure le plan initial. Le brouillon de l’utilisateur n’est pas remplacé tant qu’il ne clique pas ce bouton. Le calculateur prend aussi en charge directement les lingots pour ce profil, sans ajouter de fonderies inutiles.

Résultat validé sur la copie exacte : 4×4, 12 machines, 43 convoyeurs, 17 élévateurs, 18 câbles, coffre de sortie, 40 fondations avec trémies, 59,88 MW théoriques. Le réseau conserve 120 lingots/min → 10 plaques renforcées/min. L’entrée native se trouve sur le répartiteur des lingots au niveau logistique ; elle doit être raccordée en jeu.

## Validation et limites

Tests Python : montée/descente, rangs 1–6, liens logiques simples et élévateurs explicitement connectés, extrémités libres, cadres, trémies, rejet d’élévateurs orphelins et de capacité insuffisante, évitement d’un obstacle par voie supérieure, conservation des sources, références natives et relecture binaire. HTTP : protection locale, précontrôle sans accès au dossier Blueprint, conversion et sauvegarde/relecture en répertoire temporaire. Régressions de l’export générique, compact et architectural ; 23 suites JavaScript.

Chrome sur instance isolée : import de la copie exacte, diagnostic puis conversion, passage de 26 à 51 objets, annulation à 26 puis rétablissement à 51, précontrôle natif réussi et vue 3D. Le projet réel ouvert sur le port principal est conservé.

Les tests n’ont écrit aucun nouveau blueprint dans le dossier du jeu. La validité du fichier et de son graphe ne prouve pas encore le fonctionnement en jeu de cette nouvelle conversion ou les limites universelles de courbure des convoyeurs.
