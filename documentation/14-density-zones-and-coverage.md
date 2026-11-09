# Zones de concentration et couverture interne

18 octobre 2026. Cette étape remplace le pourcentage d'équilibrage décrit dans le document 13 ; la correction de l'orientation des murs est conservée.

## Correction du score

Le précédent ratio `min(production, besoin)/max(production, besoin)` pénalisait tout surplus intermédiaire. Cela ne représente pas une inefficacité si ce surplus est exporté ou consommé hors du périmètre. Le résultat de 81 % ne permettait donc pas de conclure que l'usine de l'utilisateur fonctionnait à 81 %.

La jauge s'appelle désormais **Couverture du bilan interne**. Pour chaque produit fabriqué ET consommé dans le périmètre, elle calcule `min(1, production/besoin)`, puis fait la moyenne à poids égal. Un surplus ne pénalise plus la couverture. Sans intermédiaire, ou avec une recette non calculable ou des membres absents, le score reste indisponible. Les sources externes sont supposées suffisantes.

Régression fournie par l'utilisateur : fil 340 produits / 240 demandés, lingots 360 / 330. Couverture = 100 %, sorties nettes potentielles = 100 fils/min et 30 lingots/min. Ce résultat est un calcul sur ces valeurs, pas une vérification de leur routage dans la sauvegarde. La jauge affiche séparément **Optimisation globale : non déterminée**. Elle ne valide ni débit réel, ni convoyeurs, ni énergie, ni consommation effective des surplus. Le chiffre n'est pas un taux d'utilisation des machines.

## Usines proposées par densité

Le chargement d'une sauvegarde détecte automatiquement les groupes d'au moins quatre machines possédant une recette enregistrée. Une méthode de regroupement par densité avec voisinage spatial (type DBSCAN) est appliquée, à 28 m par défaut. La distance verticale compte double pour limiter le regroupement d'ateliers superposés. Le voisinage est indexé par cellules spatiales. Les mineurs, machines sans recette, murs et longues liaisons ne servent pas de pont entre les groupes.

Chaque groupe forme une enveloppe de ses machines, avec marge XY de 10 m et marge Z de 8 m. Les constructions non-machines dont l'origine se trouve dans cette enveloppe sont ajoutées. Les autres machines ne sont pas ajoutées arbitrairement par la boîte. Ce périmètre est une proposition ; deux ateliers proches peuvent être regroupés, et un atelier étendu peut être séparé. Il ne reconnaît pas encore les volumes fermés par les murs.

La colonne gauche propose quatre proximités (20/28/36/50 m), l'affichage des zones et une vue d'ensemble. Sur la carte, une pastille **Zone N · X machines** ouvre en un clic la fiche avec : périmètre, couverture du bilan, entrées requises, sorties potentielles et détails des connexions. La détection est indépendante des calques visibles ; l'altitude sélectionnée filtre les pastilles. Le bouton Délimiter une usine conserve son fonctionnement manuel et masque temporairement les pastilles pendant le dessin.

Les connexions aux machines et stockages externes restent des frontières. Une remontée des convoyeurs ordinaires affiche les sources amont trouvées, sans calculer le débit d'extraction à partir du seul nombre de mineurs. Le débit dépend de la pureté, de la cadence et de l'acheminement. Les routages non pris en charge ne sont pas supposés connus.

Les zones ne sont pas automatiquement enregistrées. L'utilisateur peut nommer et enregistrer une proposition ; la définition conserve sa source `density`. Réouvrir une zone de même groupe de machines réutilise la définition enregistrée. Une nouvelle détection de contour ne remplace pas silencieusement les périmètres sauvegardés.

## Vérification

- Régression des valeurs 340/240 et 360/330 : couverture 100 %.
- Couverture de 50 % si une production interne de 120 doit alimenter un besoin de 240 ; surplus sans pénalité.
- Détection : deux groupes éloignés, groupe sur un autre étage, bruit isolé, éléments non productifs exclus, ordre d'entrée indépendant et effet du réglage de proximité.
- Jojo autosave 0 : 11 zones proposées avec le réglage 28 m. Le nombre ne prouve pas qu'il existe exactement 11 usines.
- Navigateur : clic sur une pastille, périmètre et bilan affichés, réglage de proximité et enregistrement/restauration vérifiés localement.

Commande : `node tests/check_metrics.cjs`. Les tests de persistance Python utilisent une base temporaire.

## Prochaine tranche

Valider le périmètre de l'usine cuivre décrite par l'utilisateur (trois mineurs Mk.2), puis calculer l'affectation des flux et les capacités de chaque liaison. Ajouter ensuite un indicateur séparé de débit atteignable par rapport au débit cible. La couverture agrégée seule ne doit pas devenir un verdict d'optimisation.
