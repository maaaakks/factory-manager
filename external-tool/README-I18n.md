# Interface languages

Use the language selector at the top right to switch between Français and English. The choice is stored locally and shared by the explorer, calculator, workshop, creation gallery, creation pages and reference viewer. Switching updates the current page without reloading it.

The display layer translates known text, tooltips, accessibility labels, placeholders and dynamically generated UI. Resource, recipe and machine names use the official English names from the locally installed game documentation. Searches also accept the translated resource and building names. Internal IDs, numerical model data, form values, project files and user-provided names are preserved.

`dist/i18n.js` provides `FactoryI18n.text(value)`, `FactoryI18n.locale`, `FactoryI18n.language`, `FactoryI18n.ready` and `FactoryI18n.setLanguage('fr' | 'en')`. Text and attribute sources are retained so switching back restores their French originals. UI elements containing custom names can opt out with `data-i18n-ignore`.

Add interface translations to `data/locales/ui-en.tsv` (French source, tab, English translation). Official game-name translations live in `data/locales/game-en.json`. Run `python tools/build_locales.py` to regenerate the offline browser pack. Optionally pass `--docs <CommunityResources/Docs>` to refresh official game names from `en-US.json`.

Run `node tests/check_i18n.cjs <external-tool>` to check the pack, dynamic strings, number conversion, page wiring and custom-name exclusions.
