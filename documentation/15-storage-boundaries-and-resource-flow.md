# Entrées → intermédiaires → sorties vers coffre

18 octobre 2026. Précision demandée par l'utilisateur : une ressource ne compte en sortie que lorsqu'elle peut atteindre un coffre. Le contenu redistribué après ce coffre appartient à une autre liaison. Ce document actualise les pourcentages et la présentation du document 14 ; les zones de densité sont conservées.

## Diagnostic en un clic

Cliquer sur une pastille de zone ouvre son périmètre et une fiche compacte en trois étapes. Les lignes donnent le nom, le pourcentage théorique et un débit résumé. Les hypothèses, besoins et coffres identifiés sont dépliables.

- **Entrées requises** : ressources consommées sans production interne calculable. Leur besoin est affiché ; le pourcentage reste « à confirmer » sans débit externe établi. Trois mineurs Mk.2 ne suffisent pas à établir la capacité : pureté, cadence et acheminement comptent aussi.
- **Ressources intermédiaires** : ressources à la fois produites et consommées. Le pourcentage est le minimum entre la couverture du besoin interne et la part de production affectable en interne ou à un coffre. Un surplus exportable vers coffre ne le pénalise pas.
- **Sorties vers un coffre** : uniquement les ressources pour lesquelles un débit théorique positif est affectable à un premier coffre. Le pourcentage compare cette affectation au disponible après les besoins internes. Un intermédiaire exporté peut donc apparaître à la fois comme intermédiaire et comme sortie.
- **À diagnostiquer** : production sans coffre identifié et sans affectation interne complète. Ce n'est pas automatiquement une sortie ni la preuve d'un blocage réel.

Le résumé global précédent est supprimé au profit des indications par ressource. Les recettes non calculables et les membres disparus rendent les pourcentages incomplets. Les directions ou transports inconnus sont indiqués comme parcours partiel, sans conclure à un blocage.

## Chemins et affectation

Pour chaque machine productrice, l'outil suit les sorties connues, traverse seulement les convoyeurs/ascenseurs et répartiteurs/fusions ordinaires pris en charge, puis s'arrête à la première machine ou au premier coffre. Les coffres peuvent être hors de l'enveloppe spatiale. Il ne traverse pas un coffre pour créditer sa sortie à la chaîne précédente.

Une allocation par ressource relie producteurs et consommateurs accessibles. Les besoins internes sont servis en premier par un calcul de flux maximal, limité par les productions et consommations théoriques des recettes. Le disponible restant est ensuite affecté aux coffres accessibles. Les volumes sont conservés dans chaque allocation ; un même surplus n'est pas compté plusieurs fois sur plusieurs coffres. Une production proche mais sans chemin vers le consommateur ne couvre plus arbitrairement son besoin.

Exemple synthétique de régression : 340 fils produits, 240 consommables en interne, 100 affectables à un coffre ; 360 lingots produits, 330 consommables en interne, 30 vers coffre. Intermédiaires et sorties : 100 % sous ces hypothèses. Sans chemin vers un coffre, les 100 fils et 30 lingots restent des débouchés non identifiés. Les chiffres seuls fournis par l'utilisateur ne prouvent pas que ces chemins existent dans la sauvegarde sélectionnée.

Ce calcul décrit des affectations possibles, pas un débit mesuré. Il ne limite pas encore les capacités des convoyeurs, n'applique pas de règles de partage avancées, ne propage pas les déficits aux recettes aval, ne simule pas l'énergie ou le remplissage des coffres. Les sorties vers coffre supposent qu'il peut accepter les ressources. Aucun pourcentage d'efficacité réelle ou d'optimisation globale n'est annoncé.

## Tests

`node tests/check_storage_flows.cjs` : besoins internes prioritaires ; surplus vers coffre ; arrêt au premier coffre même si un autre est connecté après ; entrée externe indéterminée ; absence de sortie sans coffre ; production déconnectée exclue de l'alimentation interne.

`node tests/check_metrics.cjs` : murs, calculs de couverture et détection de densité. Les tests Python de persistance restent isolés dans une base temporaire. Le navigateur vérifie les zones cliquables, leurs changements de proximité et la fiche d'une zone cuivre avec ses coffres terminaux.

## Suite

Établir les capacités d'extraction et de chaque convoyeur, puis propager les limitations le long de la chaîne. Une fois ces contraintes intégrées et le périmètre de référence confirmé, on pourra estimer le débit atteignable plutôt que les seules affectations théoriques.
