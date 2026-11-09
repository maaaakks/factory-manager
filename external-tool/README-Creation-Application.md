# Appliquer les créations dans Design

Les huit créations peuvent habiller le blueprint ouvert depuis Design > Façades.

- **Appliquer la création** conserve les positions relatives de toute la production, des machines et des réseaux. Une translation globale et un changement de terrain peuvent être nécessaires.
- **Adapter l’usine à cette création** recherche une implantation compacte sur un seul niveau. Machines et réseaux sont réorganisés ; les recettes et la somme des horloges par recette sont conservées, ainsi que les entrées/sorties, le nom, le tampon et les peintures du projet. Cette action ne réorganise pas les profils natifs calibrés.
- **Examiner la création** ouvre toujours sa maquette indépendante.

L’application est annulable dans l’atelier. La recherche utilise les compositions natives existantes : largeur 64–96 m et profondeur 48–80 m, par travées de 8 m. Les pièces ne sont pas étirées. Les hauteurs, annexes et facettes restent celles des créations. Si aucune implantation compatible n’est trouvée, le projet reste intact.

Les planchers intégrés sont enregistrés dans design.studyFloors ; les deux interpréteurs vérifient leurs limites et leurs collisions avec la composition. Les projets de référence sans studyFitted conservent leurs restrictions et leur géométrie précédentes.

Contrôles de cette première version : huit intégrations rigides, huit adaptations d’une usine de moteurs, conservation du projet source et des recettes/débits, refus des cas impossibles, parité géométrique JavaScript/Python et parité des planchers pour seize projets. Un export natif adapté a été construit et relu en local. L’application et Annuler/Rétablir ont été vérifiés dans l’interface sur le brouillon Moteur. Cela ne constitue pas une validation du placement ou des collisions dans le jeu.

Les contrôles spécifiques acceptent le chemin absolu d’external-tool et un fichier intermédiaire :

```powershell
node tests/check-creation-fitting.cjs $PWD work-proof.json
python tests/check_native_creation_fitting.py $PWD work-proof.json
```
