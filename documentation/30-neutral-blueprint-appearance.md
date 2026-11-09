# Apparence neutre et couleur globale

19 octobre 2026.

Le plan utilise une apparence neutre par défaut. La teinte décorative du sol n’est plus affichée ; la grille et les réservations restent visibles. Les machines, coffres, éléments logistiques et poteaux utilisent un tracé neutre. Les anciens projets sans personnalisation explicite adoptent ce rendu, même si leur structure contient une ancienne couleur de plancher.

Dans le panneau droit, « Apparence du blueprint » contient une option « Personnaliser les couleurs ». Elle révèle une couleur commune et un bouton « Appliquer à tout le blueprint ». La couleur s’applique à tous les sols et objets, à tous les étages ainsi qu’au tampon ; les objets ajoutés ensuite reprennent ce réglage. « Revenir à l’affichage neutre » désactive la personnalisation. La sélection, les erreurs de placement et le diagnostic des convoyeurs conservent leurs signaux fonctionnels.

Le réglage optionnel `appearance: { enabled: boolean, color: '#rrggbb' }` est conservé dans le brouillon, les projets et les exports. Les projets antérieurs restent compatibles. Les commandes passent par l’historique et n’altèrent ni les positions ni les débits. Le réglage d’apparence survit à une nouvelle génération de placement. La matière des sols reste réglable séparément dans « Sols et espacement ».

Validation : test `check_workshop_appearance.cjs` pour valeurs par défaut, persistance et refus des valeurs invalides ; suites modèle et implantation réussies. Dans Chrome : neutralité initiale, application d’une couleur aux deux machines, annulation et rechargement en affichage neutre.
