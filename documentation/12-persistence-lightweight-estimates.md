# Usines enregistrées, architecture et premières estimations

État vérifié localement le 18 octobre 2026. Ce document actualise les limitations des étapes 09 et 10. L'application reste un outil externe local, sans modification des sauvegardes du jeu.

## Nom et périmètre persistants

La fiche propose **Enregistrer cette usine** ; Entrée dans le nom effectue aussi l'enregistrement. Le statut distingue les modifications en attente et le périmètre enregistré. Le sélecteur **Usines enregistrées** permet de retrouver une définition. Après chargement d'une sauvegarde, la dernière définition enregistrée de cette partie est restaurée.

Les définitions sont stockées dans `external-tool/data/factories.json` : nom, identifiant, membres, rectangle et origine manuelle/automatique. Le monde est identifié par une empreinte de mapName, sessionName et saveIdentifier ; les autosaves 0 et 2 de jojo ont la même identité lors du test. Renommer la partie peut changer cette identité. Les définitions ne sont pas ajoutées au fichier `.sav`. Sauvegarder ce fichier JSON avec le projet pour conserver les noms.

L'écriture est atomique. Un renommage met à jour la même définition. Si une construction a disparu d'une nouvelle sauvegarde, son absence est signalée et elle est exclue du calcul. Aucun rapprochement arbitraire avec une autre construction n'est effectué.

## Pourquoi les murs manquaient

Le premier lecteur ne parcourait que les acteurs classiques. Une grande partie de l'architecture est sérialisée dans `FGLightweightBuildableSubsystem`. L'adaptateur lit maintenant ces enregistrements avec position et rotation et les classe dans les calques existants.

Sur `jojo_autosave_0.sav` : **7 838 constructions**, dont **5 740 lightweight**, **1 939 murs/fenêtres**, **3 599 fondations/rampes** et **83 toitures**. Les identifiants lightweight sont dérivés du type et de la transformation, indépendamment de l'ordre de la liste ; des doublons exactement superposés peuvent rester indiscernables. Les murs sont des segments schématiques de 8 m et les dalles des rectangles schématiques : les dimensions réelles de chaque variante ne sont pas encore reproduites. Les filtres d'altitude continuent de s'appliquer.

## Proposition locale d'usine

1. Cliquer sur une machine ou la rechercher par sa recette, par exemple « cuivre ».
2. Cliquer sur **Proposer une usine autour de ce bâtiment**.
3. Examiner le périmètre, les recettes, les connexions de frontière et le bilan.
4. Donner un nom puis **Enregistrer cette usine**.

La proposition parcourt les connexions physiques locales, avec un rayon réglable de 10 à 300 m, par défaut 60 m. Les stockages arrêtent la traversée. Depuis une machine à recette, les machines sans recette sont des frontières ; depuis une recette à un ingrédient, les recettes à plusieurs ingrédients sont aussi des frontières. La traversée est plafonnée à 350 objets de production. L'architecture voisine est ajoutée dans l'enveloppe XY avec une plage verticale limitée.

Il s'agit d'une heuristique à confirmer, pas d'une reconnaissance exacte du bâtiment. Elle ne partitionne pas encore toute la carte et ne permet pas encore d'éditer individuellement les membres. Pour un autre périmètre, ajuster le rayon ou tracer une sélection manuelle. Les murs ne sont pas encore utilisés comme volumes fermés et les liens physiques ne prouvent pas quels objets circulent.

## Entrées, sorties et bilan

Les liens qui traversent le périmètre sont distingués des ports ouverts. Les objets possibles sont déduits des recettes accessibles à l'intérieur, en gardant les ambiguïtés ; ce n'est pas une lecture des objets réellement transportés.

Le catalogue local provient des fichiers officiels `CommunityResources/Docs` de l'installation du jeu : noms français, ingrédients, produits, durée et vitesse des machines. Génération avec `build_catalog.py --docs CHEMIN_DOCS --build NUMERO_BUILD`. Aucun téléchargement ou service distant n'est nécessaire.

Pour les recettes solides compatibles, la cadence théorique est calculée à partir de la durée, de la vitesse de machine, du potentiel courant et du multiplicateur de production. Une valeur absente est supposée à 1× et signalée. Les besoins et excédents sont les sommes nettes des recettes calculables. Ils ne valident pas le routage, les capacités de chaque convoyeur, l'alimentation électrique, les blocages ou les arrêts. Mines, générateurs et recettes avec fluides ne sont pas simulés.

Le catalogue installé est build **513885** ; jojo est build **463028**. L'écart est affiché et les chiffres restent à confirmer. Cette étape n'attribue aucun score d'optimalité.

## Vérifications

- Import réel : architecture lightweight, identifiants uniques, recette cuivre calculable, identité commune entre deux autosaves et empreinte du `.sav` inchangée.
- Tests Python : renommage sans doublon dans une base temporaire, validation des identités, calcul avec cadence/bonus, rejet des fluides et machine incompatible.
- Navigateur : enregistrement puis rechargement du nom et périmètre ; nouvelle proposition conservant la même définition.
- Secteur cuivre testé : 171 objets, 4 fonderies de lingots et 6 machines à tôles ; 2 connexions entrantes et 2 sortantes ; besoin théorique de 120 minerais/min, excédent de 60 tôles/min, sous les hypothèses affichées. Ce secteur n'est pas confirmé comme celui entouré par l'utilisateur.

Tests reproductibles depuis `external-tool` : `python tests/check_foundation.py`, puis éventuellement `python tests/check_foundation.py --save CHEMIN_SAV`. Le test de persistance utilise exclusivement un dossier temporaire.

## Prochaine tranche

Confirmer le secteur de référence avec l'utilisateur, permettre la correction des membres/frontières puis vérifier chaque liaison et sa capacité. L'optimisation doit attendre cette validation ; un bilan net équilibré ne garantit pas un réseau réalisable.
