# Credits and third-party notices

## Open-source projects

| Project | Used for | License / provenance |
| --- | --- | --- |
| [GreyHak/sat_sav_parse](https://github.com/GreyHak/sat_sav_parse) | Reading Satisfactory saves and reading/writing native `.sbp` blueprints. Imported by the Python application. | GPL-3.0-only. Copyright 2024–2026 GreyHak. Vendored revision `bf490d3638a7af3ea174ea7d14c7b2304d3637d8`. [License](external-tool/vendor/sat_sav_parse/LICENSE) and [upstream README and credits](external-tool/vendor/sat_sav_parse/README.md) are retained. |
| [greeny/SatisfactoryTools](https://github.com/greeny/SatisfactoryTools) | Source of the item icon files used in the interface; no claim is made that its application code is part of Factory Manager. | Revision `fb43f813c03eb306b0e8d0047a8c53ae010044e0`. Per-icon URLs and hashes are recorded in [game-icons-manifest.json](external-tool/data/game-icons-manifest.json). Game artwork belongs to Coffee Stain Studios and is outside our code license. |
| [SatisfactoryModLoader](https://github.com/satisfactorymodding/SatisfactoryModLoader) | The separate earlier Unreal/modding starter in `starter-project/`; not a runtime dependency of the local web application. | GPL version 3; retain its [license](starter-project/LICENSE.txt), [credits](starter-project/CREDITS.md), and bundled third-party notices. |

## Game and community assets

- **Coffee Stain Studios / Satisfactory**: game names, item icons, extracted recipe and building data, game content visible in screenshots, and native game asset references. English/French display names are derived from the game's CommunityResources documentation. These remain subject to their owners' rights.
- **Satisfactory Wiki contributors**: the [world map image](https://satisfactory.wiki.gg/images/Map.jpg), downloaded on 18 October 2026 and used as `external-tool/dist/assets/world-map.jpg`. This is game/community imagery, not MIT-licensed application code. Its provenance is retained in the [asset notes](external-tool/dist/assets/README.md).
- **[JazzFrank — Modular Warehouse](https://satisfactoryblueprints.com/author/jazzfrank)**: source community blueprint modules for the M05 architecture system. Source URLs and file hashes are retained in [the module catalog](external-tool/data/m05/catalog.json) and [manifest](external-tool/data/m05/manifest.json). Attribution does not relicense these designs or establish redistribution permission.

## Design references

Architecture studies also credit TotalXclipse, Reekitect, and Tenhope as visual design references. The individual reference links are retained in the architecture study interface. These are acknowledgments of inspiration, not claims that their work is open-source or bundled code.

Factory Manager is an independent fan project and is not an official Coffee Stain Studios product. See [LICENSING.md](LICENSING.md) for the scope of the MIT permission and the GPL obligations of the combined application.
