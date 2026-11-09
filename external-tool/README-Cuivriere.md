# Cuivrière

Création extérieure ajoutée le 6 novembre 2026 depuis `kouyère_autosave_0.sav`, bâtiment Copper.

850 pièces architecturales natives et six panneaux LED ambre près de l’entrée dans le format original 104 × 88 m : murs, triangles, vitrages, toiture, fondations, piliers et circulations. Les positions sont recentrées, avec une translation verticale de 6 m pour placer la base à zéro. Les finitions cuivre et caterium sont conservées dans l’export ; les couleurs de l’aperçu sont schématiques. Machines, convoyeurs, réseau électrique et panneaux de signalétique ne font pas partie du template.

Largeur 104–136 m, longueur 88–120 m par travées centrales de 8 m. Chaque pièce garde ses dimensions et son quaternion. Le template est une maquette autonome à télécharger puis importer dans l’atelier. Il ne réorganise pas automatiquement une chaîne de production existante.

Source architecturale éditable : `data/cuivriere-source.json`. Régénération : `python tools/build_cuivriere.py`, puis `python tools/build_architecture_catalog.py`.

Vérifications : `node tests/check_cuivriere.cjs <external-tool> <proof.json>`, puis `python tests/check_native_cuivriere.py <external-tool> <proof.json>`. Les 25 formats sont comparés entre JavaScript et Python ; trois exports natifs sont écrits et relus hors du jeu. La fiche et son changement de largeur ont été vérifiés dans le navigateur. Placement et rendu final restent à vérifier dans Satisfactory.

Le contrôle historique `check-creation-fitting.cjs` échoue sur Compact de façon identique avant et après ce changement ; ce problème préexistant ne concerne pas Cuivrière.

Correction du 6 novembre : verre des verrières distinct de la finition cuivre des cadres, transparence avec occultation correcte par les panneaux triangulaires, six panneaux LED ambre encadrant l’entrée. Les poses des 850 pièces sources et les finitions de l’export restent conservées.
