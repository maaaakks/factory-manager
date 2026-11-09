# Foundation backlog — small vertical slices

Every slice contains its minimal UI, normal fixture, failure case, and packaged-game check. Do not complete all backend services before making something visible. IDs express implementation order and dependencies, not calendar estimates.

| ID | Feature and player result | Depends on | Acceptance |
| --- | --- | --- | --- |
| F00 | Reproducible minimal mod | Setup | Package loads in recorded game/SML set; logs identify version |
| F01 | Open/close compact Inspect shell | F00 | Helpful empty state, correct binding hint, Escape restores normal input |
| F02 | Aim and select one vanilla belt | F01 | Correct friendly identity, one highlight, clear/reselect works |
| F03 | Inspect immediate ports | F02 | Direction, connected/open states, capacity or explicit unavailable; port marker locates each |
| F04 | Trace a straight conveyor chain | F03 | Correct downstream sequence; stops at open end; upstream gives reversed reachability |
| F05 | Trace supported branches | F04 | Ordinary splitter/merger branches shown; loop terminates; storage/producer stops explained |
| F06 | Bounded cancellable scan | F04 | Progress, cancel, cap explanation; old request cannot overwrite newer selection |
| F07 | Review and edit candidate membership | F05, F06 | Add/remove/stop, undo last edit, Done/Cancel; exclusions survive refresh |
| F08 | Show boundary connections | F07 | Known entering/leaving edges counted correctly; open/unresolved ports separate |
| F09 | Show approximate bounding size | F07 | Known dimensions/rotation tests; units correct; bounds overlay clears on close |
| F10 | Name and revisit session scopes | F08, F09 | Two scopes remain distinct during session; no cross-world carryover |
| F11 | Detect outdated data | F10 | Dismantle/reconnect marks old data; Refresh repairs or reports missing members |
| F12 | Read one simple recipe and configured rates | F03 | Matches game UI and calculation; unsupported modifiers labeled |
| F13 | Show simple expected balance | F08, F12 | Known supported linear chain reports demand/capacity with assumptions |
| F14 | Prototype one observation point | F13 | Known transfer count/window; no double count, pause/time handling, topology reset |
| F15 | Save/reload scope identity | F10, identity investigation | Scope repair works after member removal/replacement; versioned serialization |
| F16 | Multiplayer inspection | Foundation stable, network investigation | Two clients isolate selection; authoritative result consistency; reconnect tested |

F06 can follow F04 before branch support if it makes debugging safer. F09 and F12 are independent after their prerequisites. F14–F16 are separate extensions; the first foundation release does not depend on them.

## Release-sized checkpoints

**A — Inspector:** F00–F03. A real user can inspect one belt without commands. This is the first build to hand over for testing.

**B — Trace and line definition:** F04–F11. The user can trace, adjust, name, and inspect a small line's connections and approximate size. This is the first complete shared-foundation experience.

**C — Expected flow:** F12–F13. One supported production-chain type can show calculated rates and explain a simple capacity mismatch.

Observation, persisted scopes, and multiplayer receive their own checkpoints. Architecture/layout/transport previews can branch from checkpoint B where the needed data is ready.

## Test fixtures

Keep tiny named areas in a dedicated test save. Record included buildings and expected graph edges; screenshots alone do not specify topology.

| Fixture | Purpose |
| --- | --- |
| T01: one disconnected belt | Open endpoints, no inferred item/flow |
| T02: storage → two belts → storage | Direction, direct neighbors, buffer stopping |
| T03: ordinary splitter with two connected exits and one open exit | Branches and open ports |
| T04: two sources → merger → storage | Upstream branching, downstream convergence |
| T05: lift between two elevations | Direction, vertical bounds, lift adapter |
| T06: conveyor loop, using appropriate junctions | Cycle detection without dropped edges |
| T07: source → simple manufacturer → storage | Production boundary and later recipe calculation |
| T08: shared supply to two separate lines | Editable boundary; no silent over-selection |
| T09: selected machine plus distant decorative object | Logical/spatial distinction and geometry filters |
| T10: rotated machines on a known foundation grid | Unit conversion and approximate AABB inflation |
| T11: dismantle/reconnect while a trace is pending | Lifetime safety and stale revisions |
| T12: unsupported modded building, later compatibility fixture | Honest frontier and partial analysis |
| T13: generated/repeated larger network | Scan caps, cancellation, profiling |
| T14: controlled input/output count over time | Later observation correctness |

For T07 choose a simple current-game recipe, record its quantities/time and clock/modifier settings from the game, then hand-calculate expected rates. Do not rely on remembered recipe numbers.

## What to verify automatically

Pure graph fixture checks are appropriate for direction, branches, loops, boundary crossings, exclusions, and revision rejection. Pure geometry fixtures verify unit conversion and unions; rate fixtures verify units and supported formulas.

Those checks do not prove adapters work in Satisfactory. Packaged-game tests verify real ports, lift behavior, lifecycle changes, input/focus, bounds, and performance. Mock widgets can test readable UI states but do not prove in-game integration.

## Per-slice test record

```text
Feature ID / package version:
Game build / SML / engine / starter commit:
Fixture and starting conditions:
Player steps:
Expected result:
Actual result:
Unsupported/error case:
Close/cancel/input recovery:
Evidence files and log excerpt:
Performance measurement, if relevant:
Pass / fail / blocked and reason:
```

Record build, editor preview, packaged single-player, remote client, and dedicated-server outcomes separately. Mark untested states as untested.

## UX checks on every visible slice

Open from default configuration; inspect at ordinary viewing distance; read the compact summary; locate a world object; cancel or close; reopen. Confirm no leftover highlight/input context, no misleading zero values, no unexpected factory changes, and a clear next action for an unsupported target.
