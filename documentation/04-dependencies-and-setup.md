# Dependencies and setup

Documentation checked: 18 October 2026. Nothing below has been inventoried or installed locally for this project. Pin an internally compatible game/SML/engine/starter-project set before coding; “latest” links are discovery links, not reproducible version pins.

## Development dependencies

| Dependency | Purpose | Baseline |
| --- | --- | --- |
| Satisfactory on Windows | Packaged runtime tests | Record build and Stable/Experimental channel |
| Satisfactory Mod Manager (SMM) | Test profiles and mod installation | Record installed release |
| Satisfactory Mod Loader (SML) | Mod framework | Match game and starter project |
| CSS custom Unreal Engine | Editor and packaging | Match the modding release; stock Epic UE is insufficient |
| Visual Studio 2022 + required MSVC/.NET components | C++ compilation | Follow current required-software guide exactly |
| Wwise + matching integration | Starter-project setup | Follow matching setup instructions even without custom sounds |
| SatisfactoryModLoader starter project | Game headers/placeholders, examples, tooling | Pin commit and submodules |
| Alpakit | Create/package/install the mod from the development project | Use the matching project's tooling |
| Git | Reproducible source and documentation history | Recommended; version project-specific source/content |

The current guide lists custom UE 5.6.1, MSVC v143 14.38-17.8, .NET 8 runtime, .NET Framework 4.8.1 SDK, and Wwise 2025.1.6.9117. Treat these as a documentation snapshot to recheck during setup, not a compatibility lock. See [Required Software](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/dependencies.html).

Some engine downloads require Epic/GitHub account linking and repository access. Follow the source guide. Reserve disk space after inspecting engine/project package sizes; the documentation warns that the environment can exceed 30 GB, but that is not a complete disk estimate for our checkout, caches, and packaged builds.

The setup guide warns against enabling the Visual Studio Integration Tool or Unreal Engine Test Adapter through the editor's integration configuration because they can break the custom project. Follow the matching [Project Setup guide](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/project_setup.html).

## Runtime and code dependencies

Initial player requirements: compatible game, SML, and this mod. SMM is the recommended installation workflow. Do not require FicsIt-Networks, an external planner, cloud services, API keys, or an AI model for the foundation.

Proposed code dependencies: FactoryGame, SML, Unreal Core/CoreUObject/Engine, UMG, and the input/UI modules actually needed by the chosen integration. Verify exact Build.cs entries from the pinned template and used headers; do not copy an unnecessarily broad list as a permanent dependency set. See [C++ Setup](https://docs.ficsit.app/satisfactory-modding/latest/Development/Cpp/setup.html).

Start with vanilla assets. A future optional asset mod should add an adapter/style pack without making it mandatory for users of the inspector. No runtime downloads are needed for inspection.

## Setup sequence and evidence

1. Inventory game location/build/channel, available disk, existing compiler/engine/SMM installations, and account access. Report missing pieces before large installations.
2. Record a compatible version set using current documentation and releases.
3. Obtain the matching custom engine and starter project; preserve exact release/commit identifiers.
4. Configure compiler and Wwise integration using the matching guide.
5. Build/open the starter project and package a minimal empty/example mod.
6. Launch a dedicated test save in the real game and verify mod load/unload behavior.
7. Add the first compact panel and rebindable action.
8. Record logs and a screenshot; only then begin actor inspection.

Use a disposable test save and an isolated mod profile for repeatability. Keep large engine installations outside the eventual source repository. Do not put proprietary game assets, generated builds/caches, personal saves, or credentials in source control.

Suggested future layout, to finalize during setup:

```text
satisfactory mod/
  documentation/       this plan
  src/                 project-specific source/plugin, after choosing build layout
  tests/               graph fixtures and acceptance records
  tools/               reproducible project helpers
```

Do not move starter-project folders arbitrarily to match this sketch. Prefer a clearly documented starter-project checkout and plugin path. The Desktop folder can be the project home while heavy toolchains live elsewhere.

## Version record to fill during setup

| Field | Recorded value |
| --- | --- |
| Game build / channel / platform | Not checked |
| SML release / starter commit / submodules | Not selected |
| Custom engine release | Not selected |
| MSVC / Windows SDK / .NET | Not checked |
| Wwise SDK / integration | Not checked |
| SMM / Alpakit | Not checked |
| Test mod reference / package version | Not chosen |
| Successful build / packaged launch evidence | None |

Linux cross-compilation and dedicated-server tooling are deferred until their support milestone. Do not install those dependencies merely for the single-player inspector.

## Technical investigations before promises

| Investigation | Evidence needed | Fallback |
| --- | --- | --- |
| Target selection and overlay/input integration | Packaged-game selection, close/reopen, modal-conflict test | Simpler deliberate open-and-pick workflow |
| Port direction and neighbor resolution | Belt, lift, disconnected endpoint fixtures | Restrict supported actors; expose unresolved endpoints |
| Bounds and units | Known foundation arrangement and rotated machine | Approximate labeled bounds |
| Lifecycle invalidation | Dismantle/reconnect during scan | Bounded validation and manual refresh |
| Recipe/modifier access | Compare game UI and hand calculation | Fixed supported recipe/configuration subset |
| Stable saved identity | Save/reload, dismantle/rebuild | Session-only scopes |
| Actual item-transfer measurement | Controlled count and time-window test without altering flow | Capacity/expected rates only |
| Multiplayer visibility | Host/client snapshots agree | Explicit single-player support |

The FicsIt-Networks reflection API is a separate mod API. Its connection or transfer features do not prove equivalent direct access in our plugin. Validate our own game-header adapters and instrumentation.
