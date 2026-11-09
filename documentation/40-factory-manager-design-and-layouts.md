# Factory Manager : Construction, Design et variantes de layout

19 octobre 2026.

## Interface disponible

Le nom public est **Factory Manager**. La navigation partagée propose Explorateur / Design. `/atelier` reste une adresse compatible ; `/design` ouvre le même éditeur. Les clés de stockage, identifiants JSON et marqueurs de propriété des anciens exports sont conservés : le renommage ne migre ni ne supprime les projets. Un lanceur `Ouvrir Factory Manager.cmd` est ajouté ; les anciens lanceurs restent utilisables.

La bannière « Session de secours » est retirée. Le paramètre `?secours=1` conserve néanmoins son stockage de brouillon séparé pour les essais.

- **Construction** : outils de machines et réseaux à gauche, plan éditable et petit inspecteur contextuel uniquement lorsqu’une sélection existe.
- **Design** : aperçu 3D en lecture seule au centre, outils à gauche avec quatre icônes : Sols, Peinture, Réseau, Façades. Aucun panneau permanent à droite. La caméra, les vues Face / Côté et le mode opaque sont partagés avec la fenêtre d’aperçu.
- **Calculator**, immédiatement après `+` : format, layout, hauteur, planchers et politique des convoyeurs avant les objectifs d’entrée/sortie.
- **Mes projets** : cartes illustrées par les sorties (plusieurs produits si nécessaire), nom et débits. Les illustrations SVG sont schématiques, locales et indépendantes des ressources graphiques du jeu. Une sortie finale peut être déduite des recettes pour les projets sans objectif explicite.
- **Icône en jeu** : les futurs exports `.sbpcfg` utilisent aussi la ressource principale de sortie. Pour 10 plaques renforcées/min, l’identifiant du catalogue d’icônes du parseur local est 207. Une relecture du fichier contrôle cet identifiant. L’affichage effectif dans le jeu reste à vérifier.

## Génération et hauteur

Trois intentions de layout sont disponibles : **Super compact**, **Équilibré**, **Aéré**.

Pour le profil natif 120 minerais de fer → 10 plaques renforcées/min, les trois intentions réutilisent les paires mesurées, les manifolds, raccords muraux et chemins physiques. Elles ajoutent respectivement 0, 1 ou 2 m de dégagement à chaque étage. Elles ne changent pas encore la disposition XY interne des paires. Pour les autres chaînes, le placement classique réserve des couloirs d’au moins 4, 6 ou 8 m ; ses liaisons logiques restent à router avant export.

La hauteur **Minimale** respecte les machines, leurs antennes et la logistique calibrée. Les choix 8 / 10 / 12 / 16 m sont des minimums, jamais une permission de chevauchement. Le profil natif minimal conserve les étages à Z=0 / 10,8 / 18,8 m. Équilibré ajoute 1 m par transition ; Aéré en ajoute 2. Le volume du format est vérifié : une variante trop haute est refusée avec une invitation à agrandir le format ou diminuer la hauteur.

Les réglages demandés pour le prochain calcul sont distincts des paramètres des modules déjà générés (`generation` / `nativeSettings`). Modifier un réglage n’altère pas silencieusement les prototypes utilisés lors de l’export du plan ouvert.

Pour les autres chaînes, les enveloppes génériques ont des hauteurs conservatrices (8,5 m pour fonderies/constructeurs, 10,75 m pour assembleuses). L’ancien cas générique 10 plaques renforcées/min ne doit plus être tassé artificiellement dans un 4×4 avec des machines de 6 m : les paires natives traitent ce cas compact, tandis que le placement classique demande davantage de place.

## Planchers, peinture et convoyeurs

Les étages peuvent rester en cadres ajourés ou employer des dalles. Dans le profil compact, les dalles sont de 1 m ; les passages d’élévateurs sont réservés en omettant les dalles de 8×8 m concernées. Ce sont de grandes trémies ouvertes, pas encore des traversées de fondation ajustées au diamètre de chaque élévateur. Les fondations conservées sont exportées avec leur recette et leur matière (béton, métal, asphalte).

La peinture peut être commune à tout le projet ou distincte pour les machines, la logistique, l’électricité et les sols. Les couleurs par catégorie sont conservées dans le JSON et appliquées à l’export natif. Revenir au neutre retire aussi la palette par catégorie. Les convoyeurs restent colorés par diagnostic dans l’éditeur pour préserver la lecture des capacités.

**Convoyeurs économiques** choisit le plus petit rang suffisant : 60, 120, 270, 480 ou 780 objets/min. Le profil natif applique aussi cette règle aux vrais élévateurs et à leur recette de construction. Les jonctions sans convoyeur restent des raccords directs. Un débit supérieur au Mk.5 demande plusieurs lignes ; le mode économique ne passe pas implicitement au Mk.6.

## Première base de façades procédurales

Trois styles prédéfinis sont disponibles : **Atelier béton**, **Industriel FICSIT**, **Verrière**. Leur générateur décompose le périmètre en travées, allèges, linteaux, montants, angles et toiture facultative. Les ouvertures, la largeur des angles et la variation sont modifiables. Un même style et une même variation produisent les mêmes composants.

La disponibilité des packs Béton / Métal / Verre est déclarée manuellement, par projet. Un style demandant un pack désactivé est verrouillé. Ce filtre ne prétend pas refléter automatiquement les achats du magasin AWESOME ou les paliers du joueur.

Depuis une usine sélectionnée dans l’explorateur, **Adapter son style dans Design** recense les classes de murs observées et suggère une famille architecturale. Le style est transmis localement, avec la liste de ses pièces source, puis peut être édité dans Façades. Il s’agit d’une suggestion de famille ; les modèles exacts, dimensions des variantes, couleurs et textures ne sont pas copiés. La source reste consultable dans le projet.

**Limite explicite :** les façades sont des volumes schématiques de conception, enregistrés dans le projet JSON. Elles ne sont pas encore exportables dans le jeu. Un export natif avec un habillage actif est bloqué, pour ne pas produire un blueprint amputé de son habillage. Désactiver l’habillage permet d’exporter le réseau et les bâtiments existants. Les intersections décor / machines / trajets ne sont pas encore résolues automatiquement.

## Étapes suivantes pour des styles constructibles

1. Calibrer un petit catalogue natif : mur plein 8×4, fenêtre, angle, porte, toiture, raccord électrique mural. Mesurer transformations, points d’attache, dégagements et recettes.
2. Décrire les styles par une grammaire : socle → travées → bandeau → toit, avec choix de composants compatibles et interfaces d’angle.
3. Transformer les limites d’usine et les entrées de convoyeurs en contraintes : passages, portes, collisions, accès aux machines, hauteur sous toiture.
4. Ajouter les achats/paliers effectivement lus dans la sauvegarde au catalogue de composants autorisés. Une progression inconnue doit rester « non déterminée », jamais assimilée à « tout débloqué ».
5. Exporter un premier style de quatre murs et une porte, puis vérifier en jeu avant d’étendre aux variantes et aux toits.
6. Depuis l’explorateur, capturer un véritable style éditable : composants natifs, palette et proportions, plutôt qu’une seule suggestion de famille.

## Vérifications

- Suite Node existante réussie, plus tests de génération déterministe, limites XYZ, verrouillage des packs, variantes de murs, palette et persistance.
- Quatre variantes natives créées, sérialisées puis relues en `.sbp` dans l’espace de travail de test : compact ajouré 4×4 ; compact avec dalles 4×4 ; équilibré avec dalles 5×5 ; aéré avec hauteur 12 m en 6×6. Contrôle des raccordements, géométrie, conservation des débits, rangs Mk.1/Mk.2 des convoyeurs et élévateurs, refus de dépassement. Ces fichiers ne sont pas déposés dans le dossier du jeu par ces tests.
- Icône de sortie : configuration relue avec l’identifiant 207 pour les plaques renforcées.
- Chrome : génération depuis le calculator, passage Construction / Design, mode opaque, caméra au clavier, palettes par catégorie, ouvertures et angles, sauvegarde/rechargement du projet et cartes avec icône de sortie. Essais de génération réalisés sur une instance isolée au port 8766.
- Transfert Explorateur → Design vérifié sur une proposition d’usine de cuivre de la sauvegarde kouyère : classes de murs conservées (7 murs 8×4, 2 triangles orange, 6 angles orange), source visible et éditable dans Façades. Aucun périmètre d’usine n’a été enregistré par cet essai.

Les variantes de hauteur et de dalles n’ont pas encore été testées dans le jeu. La réussite des contrôles de fichiers et de géométrie ne remplace pas ce test.
