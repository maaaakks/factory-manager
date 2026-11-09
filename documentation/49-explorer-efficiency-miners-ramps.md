# Exploration : rampes, mineurs et efficacité

Le bouton **Visualisation 3D** ouvre le panneau d’inspection. Il apparaît avant le nom et les informations de l’usine. Les mineurs et les convoyeurs amont reliés sont ajoutés à la vue, même hors du périmètre. Le calque **Mineurs reliés** permet de les masquer sans changer l’usine enregistrée.

## Géométrie

Les rampes de fondation descendent selon le +X local et leur pivot est au centre de leur hauteur. Les rampes inversées ont un dessus horizontal et un dessous incliné. Les transformations natives (quaternion et échelle, y compris négative) sont conservées.

La direction a été vérifiée sur les jonctions de rampes de `jojo_autosave_2.sav` en lecture seule : 327 jonctions exactes avec une pente négative, contre une seule avec une pente positive. Les dimensions et le pivot centré correspondent aux données du jeu installé. Les toits ordinaires conservent leur correction précédente, validée séparément. Il s’agit de volumes schématiques, pas des modèles du jeu.

## Efficacité visible

- Pour chaque ressource produite : part affectable aux machines, aux coffres ou à une sortie du périmètre. Une exportation utile ne pénalise pas ce ratio.
- Pour les entrées minières : potentiel des mineurs connectés, prenant en compte leur type, cadence et pureté. Les besoins utiles sont propagés en amont lorsque le modèle converge : 360 lingots théoriques dont seulement 330 sont utilisés demandent 330 minerais utiles, soit 91,7 % d’un potentiel de 360.
- La pureté vient d’un éventuel remplacement enregistré dans la sauvegarde, sinon de la table locale du monde, après concordance de la position à moins de 30 m. Une pureté inconnue n’est pas remplacée par « normale ».
- Une source partagée, un réseau partiel ou une propagation non convergente affichent une borne « Jusqu’à », et non une utilisation certaine. La propagation est bornée à 16 passes ; elle n’exécute pas une simulation du jeu.

## Couleurs sur la carte et dans la 3D

Vert : capacité suffisante pour les besoins identifiés. Orange : perte positive jusqu’à 20 %. Rouge : perte supérieure à 20 %. Les réseaux inconnus restent gris en 3D ; les éléments architecturaux conservent leur couleur de catégorie.

Pour identifier une limitation de convoyeur, le calcul compare le réseau physique au même réseau avec des convoyeurs de capacité illimitée, en conservant les mêmes demandes et destinations. Seules les coupures de capacité qui réduisent le débit utile sont signalées. Les demandes internes sont traitées avant les sorties. Une branche de manifold pleine qui sert tous ses consommateurs ne devient donc pas un goulot. Les machines privées d’alimentation sont également signalées.

Ces résultats sont des capacités théoriques depuis les recettes et connexions enregistrées. Ils ne mesurent pas les arrêts réels, les stocks pleins, l’alimentation électrique ou le débit instantané en jeu. Les couleurs sont calculées à la sélection d’une usine et réutilisées pendant la navigation ; aucune recherche de flux n’est faite à chaque image.

## Vérification

Tests dédiés : `check_factory_diagnostics.cjs` et `check_extraction.py`. Ils couvrent manifold saturé sans perte, vrais goulots internes et sortants, seuils de couleur, surplus, capacité extérieure, besoin minier utile, export utile, mineurs hors périmètre, pureté inconnue et surchargée, rampes ordinaires/inversées et transformations natives. La sauvegarde de référence fournit 33 mineurs dont la pureté est identifiée.

Les sauvegardes du jeu et les projets ne sont pas modifiés. La modification de l’adaptateur invalide automatiquement les anciens instantanés analysés pour recalculer les informations minières.
