# Licensing

Original Factory Manager code and documentation are available under the [MIT License](LICENSE-MIT). This permission covers the original work in `external-tool/` and `documentation/`, excluding third-party code, third-party-derived code, game data, artwork, and community blueprint content.

MIT permits reuse, modification, redistribution, and commercial use while retaining the copyright and license notice. It does not require downstream projects to publish their source code.

## Bundled application

The application directly imports GreyHak's **sat_sav_parse**, licensed under **GPL-3.0-only**. Distribution of the combined application must comply with GPL version 3, including providing corresponding source code and retaining notices. Our MIT permission for original code does not remove these obligations or relicense the parser. See [GPL text](external-tool/LICENSE) and the [upstream parser license](external-tool/vendor/sat_sav_parse/LICENSE).

A wholly permissive application distribution would require replacing the GPL parser with a compatible permissively licensed implementation, or obtaining separate permission from its rights holders.

## Exclusions

- `external-tool/vendor/`: original upstream licenses apply.
- `starter-project/`: the earlier SatisfactoryModLoader checkout retains its own GPL license, notices, and third-party terms. It is not covered by Factory Manager's MIT license.
- Game artwork, map imagery, extracted game data, screenshots containing game content, and community blueprint designs retain their respective owners' rights. They are not relicensed under MIT or GPL by this project. Credits describe provenance, not a grant of redistribution rights.
- Any file containing third-party code or a more specific upstream notice retains that notice and its applicable terms.

See [CREDITS.md](CREDITS.md) for sources and attribution.
