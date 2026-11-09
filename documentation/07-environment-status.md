# F00 setup status — 18 October 2026

## Outcome

Local environment inventoried and public starter project cloned. Minimal FactoryTools bootstrap source prepared. No editor build, package, game launch, or in-game feature test completed.

## Verified local state

| Component | Evidence / result |
| --- | --- |
| Game | Steam installation at `D:\steam\steamapps\common\Satisfactory` |
| Current executable | `FactoryGameSteam.exe`: `++FactoryGame+rel-main-anniversary-2026-CL-502094`; module manifest BuildId `502094` |
| Steam manifest | Installed build ID `24656030`; pending target `25782416`; do not assume game is fully updated |
| Historical log | July 2026 log reports CL 495413 / engine 5.6.1; historical only, not current executable evidence |
| Mod Manager | Present under LocalAppData/Programs; uninstaller product version 3.1.0; main executable did not expose a version |
| Mod Manager selected installation | The above Steam path, Default profile, `vanilla: true`; not changed |
| Installed SML | No `FactoryGame/Mods/SML/SML.uplugin` found at inspected game path; starter source is not a runtime installation |
| Visual Studio | Community 2022, 17.10.2, installed and launchable according to vswhere |
| MSVC | 14.40.33807 found; documented 14.38 toolset not found in this VS instance |
| Windows SDK | Include directory 10.0.22621.0 present |
| .NET runtime | 8.0.14 present; also 6.0.35 |
| .NET Framework 4.8.1 SDK | Not found in checked SDK registry keys/directories; confirm via VS Installer |
| Custom editor | No 5.6.1-CSS editor found in checked install locations/UE registration; user confirms no UE installed |
| Wwise | No installation found in checked program/registry locations |
| Disk | Approximately 667 GB free on C: and 425 GB on D: at inspection time |
| GitHub | Authenticated outside restricted sandbox; public starter access works |
| Custom engine access | Authenticated GitHub API request for latest `satisfactorymodding/UnrealEngine` release returned 404; account linking/access must be completed |

The restricted shell initially reported GitHub login failure. The authorized unsandboxed check confirmed login works; authentication itself is not the current blocker. No credential values are stored here.

## Source/version baseline

- Upstream: https://github.com/satisfactorymodding/SatisfactoryModLoader
- Local checkout: `starter-project/` inside the project root.
- Pinned captured commit: `8eebc9e659f0b2ff4392d2f8cf6e2cff60c8ea49` (master when cloned).
- Source descriptor: SML 3.12.0, declared minimum game CL 491125.
- Project engine association: `5.6.1-CSS`.
- No `.gitmodules` file in this checkout.
- Alpakit and SMLEditor are present under `Mods/`.
- Project-specific bootstrap: `starter-project/Mods/FactoryTools`.

Do not fetch a moving latest revision later without updating this record. Current game/SML runtime compatibility remains to be tested, especially if Steam updates the game.

## Required next actions

1. Link GitHub to Epic and complete the Ficsit linker so the required private engine release is accessible. Account login/linking is user work.
2. Obtain and install the matching custom editor. Standard Unreal from the Epic launcher is insufficient for this project.
3. Add the documented compiler/SDK components and Wwise 2025.1.6.9117/integration for this baseline, rechecking the matching guide before installation.
4. Fill the exact engine release identifier and Wwise integration version. Generate project files and build.
5. Package bootstrap via Alpakit; use a dedicated test profile/save; verify fresh runtime startup log before marking F00 complete.

No compiler installation, engine installation, Wwise installation, game update, mod-profile change, or save edit was performed.

## Sources

- [Required Software](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/dependencies.html)
- [Project Setup](https://docs.ficsit.app/satisfactory-modding/latest/Development/BeginnersGuide/project_setup.html)
- [Epic/GitHub account linking](https://www.unrealengine.com/en-US/ue-on-github)
- [Ficsit custom-engine linker](https://linker.ficsit.app/link)

F00 is **in progress, blocked on missing toolchain/access**, not complete. F01 UI has not started.

