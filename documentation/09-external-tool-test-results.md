# E01 — résultats de vérification du 18 octobre 2026

## État

Prototype local v0.1 opérationnel. Aucun build Unreal nécessaire. Serveur lié à 127.0.0.1 ; interface sans CDN ni requête externe. Lancement : `external-tool/Ouvrir Factory Tools.cmd`.

## Vérifications réalisées

| Vérification | Résultat |
| --- | --- |
| Syntaxe Python et JavaScript | Python py_compile et Node --check : succès |
| Page locale et ressources | HTTP 200 et affichage réel dans le navigateur |
| Sauvegarde format 52 / build 463028 | 2 098 constructions, 2 565 ports convoyeurs |
| Cohérence des références dans cet instantané | 0 références non résolues ; liens déclarés connectés réciproques |
| Directions | 60 inconnues, 0 conflit détecté ; inconnues conservées comme telles |
| Sauvegarde format 60 / build 495413 | Lisible, aucun bâtiment construit ; état vide affiché correctement |
| Import de fichier binaire via API locale | Sauvegarde réelle lue correctement, même nombre de constructions |
| Fichier invalide | Rejet HTTP 422 avec message |
| Origine étrangère / en-tête local absent | Rejet HTTP 403 |
| Accès à un fichier source via URL | Rejet HTTP 404 |
| Intégrité des deux sauvegardes originales | SHA-256 avant/après identiques |
| Recherche et inspection dans le navigateur | Convoyeur retrouvé par identifiant, deux ports et voisins affichés |
| Tracé aval | 2 bâtiments ; arrêt au générateur biomasse, frontière à 1 entrée |
| Tracé amont | 14 bâtiments ; arrêt au constructeur, frontière à 1 entrée / 7 sorties |

Les nombres de frontière décrivent la sélection obtenue par le code et visible dans l'UI ; aucune validation physique en jeu ni comparaison manuelle exhaustive de ces 14 bâtiments n'a encore été réalisée.

## Limites de cette vérification

- Le sélecteur de sauvegardes et le parcours recherche/fiche/tracé sont testés dans le navigateur. L'import binaire est vérifié par HTTP ; le dialogue système de sélection d'un fichier n'a pas été testé de bout en bout.
- Aucun débit réel mesuré, aucun calcul de capacité, aucune simulation de recettes.
- Les directions déduites sont cohérentes avec les ancres et règles prises en charge, mais demandent un prochain test croisé sur une petite ligne connue dans le jeu.
- Courbes issues des splines, glyphes de machines schématiques ; pas d'empreinte ou collision validée.
- Pas de test sur sauvegarde de 64 Mo, de charge multi-utilisateurs ou de nombreux mods tiers.
- Les originaux sont restés en lecture seule ; aucun export .sav disponible.

## Prochain petit test utilisateur

1. Ouvrir une sauvegarde contenant une petite ligne bien connue.
2. Retrouver un convoyeur via la carte et cliquer ses voisins.
3. Comparer entrée/sortie et tracé avec le jeu.
4. Noter les ports manquants, directions inconnues ou courbes incorrectes avant d'ajouter le calcul de production.
