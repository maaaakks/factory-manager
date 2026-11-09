# Decisions, uncertainties, and sources

## Proposed decisions

| Decision | Reason |
| --- | --- |
| One initial mod with reusable internal services | Simplifies setup/testing and avoids distribution dependencies |
| C++ core plus Blueprint/UMG presentation | Separates version-specific reads/calculations from tunable UI |
| Vanilla solid conveyors and single-player first | Smallest useful supported scope |
| Explicit membership and editable trace candidates | Connected networks do not uniquely identify a factory line |
| Port-level transport graph with internal transfer adapters | Handles junctions/buffers without pretending recipes pass items through |
| Captured snapshots and revisioned results | Supports consistent analysis and stale-result rejection |
| Compact summary plus world overlays | Keeps results connected to normal play |
| Capacity, expected rate, observed rate separately labeled | Prevents false flow claims |
| Approximate bounds before efficiency metrics | Avoids measuring empty bounding-box space as occupied area |
| Previews before construction | Makes later layout/design features reviewable |
| Session scopes before persistence | Avoids assuming stable object identities |

These are project proposals derived from our goals, not statements from the modding documentation.

## Open choices that need evidence or later user input

- Final mod name/reference and visual identity.
- Installed game/channel and compatible toolchain versions.
- Preferred eventual multiplayer/server support priority.
- Scope stopping behavior for complex storage/manufacturers, after basic fixtures.
- Reliable object identity across save/load and reconstruction.
- Reliable actual-transfer measurement with acceptable runtime overhead.
- Exact collision/clearance representations for valid layout previews.
- Style-kit source, dimensions, compatibility, and permissions for redistributing third-party assets if needed.
- Optimization priorities and acceptable tradeoffs, once layout work begins.

None blocks documenting or prototyping the first single-belt inspector.

## Source register

Checked online on 18 October 2026. These are primary documentation from the Satisfactory modding ecosystem; the mod loader is community-maintained. Latest URLs can change. Pin releases during implementation and verify headers/example assets against the selected starter project.

| Source | What it supports | Evidence limit |
| --- | --- | --- |
| [Required Software](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/dependencies.html) | Matching custom engine, compiler, Wwise, starter project, setup prerequisites | Does not prove anything is installed locally |
| [Project Setup](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/project_setup.html) | Wwise integration, project generation/build, integration-tool caveats | Must match chosen toolchain |
| [C++ Setup](https://docs.ficsit.app/satisfactory-modding/latest/Development/Cpp/setup.html) | UBT modules and game/SML dependencies | Exact project Build.cs remains to implement |
| [Starter Project Structure](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/StarterProjectStructure.html) | Placeholder assets, SML/editor tooling, project organization | Placeholders are not full game runtime behavior |
| [Enhanced Input System](https://docs.ficsit.app/satisfactory-modding/latest/Development/Satisfactory/EnhancedInputSystem.html) | Satisfactory mapping contexts and widget input lifecycle | Exact overlay/targeting workflow needs a packaged prototype |
| [Machine Interaction GUI](https://docs.ficsit.app/satisfactory-modding/v3.8.0/Development/BeginnersGuide/SimpleMod/machines/SimpleInteraction.html) | Widget-based UI and ExampleMod patterns | Versioned older example; not proof of a global inspector overlay |
| [Mod Configuration](https://docs.ficsit.app/satisfactory-modding/latest/Development/ModLoader/Configuration.html) | In-game configurable settings and preview support | Some C++ documentation is marked partially outdated |
| [Multiplayer](https://docs.ficsit.app/satisfactory-modding/latest/Development/Satisfactory/Multiplayer.html) | Authority, RCO/subsystem communication patterns and ownership constraints | Does not establish client visibility of our factory data |
| [Updating your Mod](https://docs.ficsit.app/satisfactory-modding/latest/Development/UpdatingToNewVersions.html) | Engine/starter/dependency update discipline | Re-test compatibility after updates |
| [SML 3.12 upgrade notes](https://docs.ficsit.app/satisfactory-modding/latest/Development/UpdatingFromSml311.html) | Documentation context for Satisfactory 1.2/SML 3.12 | Not a locally verified selected compatibility set |
| [Mod Manager introduction](https://docs.ficsit.app/satisfactory-modding/latest/ForUsers/Welcome.html) | Recommended player installation workflow | No installation performed here |
| [Buildable holograms](https://docs.ficsit.app/satisfactory-modding/latest/Development/Satisfactory/BuildableHolograms.html) | Candidate placement-preview mechanisms for later modules | Valid geometry, snapping, and construction still need testing |

Do not use old UE4 dependency pages as the current setup guide. Likewise, FicsIt-Networks reflection examples belong to another mod and are not an API contract for this project.

## Next concrete task

Inventory the local development environment, fill the version record, and package the smallest mod with the Inspect shell. Do not start a broad factory optimizer before F00–F03 are playable and testable.
