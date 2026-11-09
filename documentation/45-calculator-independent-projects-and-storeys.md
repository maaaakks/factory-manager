# Calculateur : nouveaux projets et préférences d’étages

## Parcours

Le calculateur est élargi à 1 000 px sur grand écran. Entrées/sorties viennent avant les préférences d’implantation. Les ressources utilisent les icônes SVG locales. Changer de sens vide la ressource et le débit en cours de saisie ; les lignes déjà ajoutées restent présentes.

Un brouillon du calculateur conserve ses objectifs séparément du projet ouvert. Le format du calculateur ne redimensionne plus les objets existants. Une génération réussie crée un nouvel identifiant, un nom issu des sorties, un tampon vide et un design sans habillage ni palette héritée. Le projet précédent reste accessible par Annuler. Les projets nommés de la bibliothèque ne sont pas remplacés.

La génération ferme le calculateur et ouvre directement Design ; elle n’ouvre plus le dialogue Vue 3D. L’habillage se fait ensuite dans l’Atelier.

## Implantation

- **Auto** cherche une implantation dans le volume disponible ; les modules calibrés sont privilégiés pour leur chaîne compatible.
- **Compact en hauteur** essaie d’utiliser plusieurs étages, dans la limite indiquée.
- **Un seul étage** impose un niveau ; un format plus large peut être nécessaire.
- **Limiter les étages** impose un plafond, pas un nombre exact de niveaux.

La hauteur minimale suit les enveloppes des machines au lieu d’utiliser la hauteur de l’assembleuse pour chaque étage. La limite verticale du blueprint reste celle de son format. Le choix de hauteur 8/10/12/16 m est un minimum, soumis à ces dégagements.

L’ancien champ Couloir de placement est retiré. Il imposait une marge uniforme de 4 à 8 m à toutes les machines. Le nouveau placement réserve une bande logistique et des marges selon le style, puis vérifie les chemins. Un échec est décrit comme un échec du placement automatique, avec nombre de machines, format, plafond d’étages et éventuellement trajet bloqué ; cela ne constitue pas une preuve qu’aucune implantation manuelle n’existe.

## Réseaux

Le nouveau chemin de génération classique produit des interfaces d’entrée, un coffre de sortie, des répartiteurs/fusions et des liens `belt`. Les chemins sont vérifiés avant de modifier le projet ouvert. Les changements de niveau ont un élévateur dédié au lien et un trajet continu en trois dimensions. Les objectifs n’aboutissent plus à des liens pointillés `planned` dans ce parcours.

Ces tracés classiques restent schématiques : la grille de routage ne valide pas tous les rayons natifs, croisements, collisions entre convoyeurs ou ports physiques distincts de chaque machine. Les élévateurs classiques et repères d’entrée restent soumis aux limites de l’export générique existant ; leur présence n’est pas une validation d’export en jeu. Les anciens calculateurs purs et leurs projets conservent leur comportement pour compatibilité.

## Cas natif fer → plaques renforcées

Le profil de paires calibrées supporte désormais de 0,2 à 10 plaques renforcées/min, en adaptant proportionnellement les cadences et débits. Il conserve les mêmes 16 machines : le profil 5/min utilise donc davantage de machines sous-cadencées qu’un placement classique de huit machines. Ce choix réutilise des raccords connus plutôt que de prétendre minimiser le nombre de bâtiments.

**60 minerais/min → 5 plaques renforcées/min en 4×4** : trois niveaux, 54 convoyeurs, 21 élévateurs, raccords électriques et coffre. Les rangs économiques sont recalculés après adaptation des débits. Entrée et sortie sont aussi renseignées dans le modèle d’interfaces partagé. Une limite stricte inférieure à trois étages utilise le placement classique au lieu d’ignorer la préférence.

Validation locale : contrôle des raccords et enveloppes par `native_compact.build_project`, débit de sortie calculé 5/min, objectif couvert à 100 %. Aucun nouveau placement dans le jeu ni écriture dans les dossiers de blueprints pendant ce développement.

## Vérifications

- 21 suites Node : compatibilité antérieure, nouveaux trajets, une/deux strates, interfaces, premier coffre, visibilité du dernier étage en hauteur minimale, bilan matière et persistance.
- Profils natifs 60→5 et 120→10 : construction/export en mémoire, capacités et géométrie contrôlées.
- Chrome : projet 6×6 existant conservé pendant la configuration 4×4 ; sélection Entrée/Sortie remise à zéro ; nouveau projet compact ouvert dans Design sans dialogue modal ; variante classique 6×6 sur un étage générée avec 19 liens.
