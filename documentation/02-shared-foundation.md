# Shared foundation — technical design

All service/type names below are proposed project names, not claims about existing Satisfactory APIs.

## Architecture

```text
Game actors/components
        |
        v
Version-specific read adapters (game thread)
        |
        v
Immutable factory snapshot + completeness metadata
        |
        +--> connection tracing / scope / geometry / calculations
        |
        v
Presentation model --> compact widgets + world highlights
```

Use C++ for adapters, graph traversal, and calculations; expose small data structures and commands to Blueprint/UMG widgets. Keep UI layout and visual tuning in widgets. Prototype this split with a single actor before expanding the architecture.

Do not traverse game objects from arbitrary worker threads. Capture required values on the game thread; only move sufficiently expensive pure calculations on copied data to background work. UI never reads actors directly.

## Shared records

| Record | Minimum contents | Used by |
| --- | --- | --- |
| Building | Session ID, descriptor/class identity, friendly label, category, transform, support status | Every module |
| Port | Owner ID, port ID, world pose, transport kind, direction, connection state | Trace, boundary, routing |
| Connection | Source port, destination port, transport identity, capacity if known | Trace, flow, routing |
| Internal transfer | Supported transitions between a building's ports, transfer kind and routing uncertainty | Correct traversal through belts/storage/junctions |
| Recipe | Item quantities per cycle, cycle duration, supported configuration factors | Expected flow and planning |
| Geometry | World bounds, local frame if available, geometry source/quality | Dimensions and layout |
| Scope | Member IDs, exclusions, explicit stops, origin seed, selection method, revision | Named factory line |
| Observation | Item, measurement point, count/window, start/end time, validity and method | Later measured flow |
| Issue | Evidence IDs, severity, explanation, affected locations, suggested next step | Friendly diagnosis |
| Constraint set | Target, region, allowed height, fixed objects, access zones, allowed assets | Later planners |

Every snapshot has world/session identity, schema version, revision, capture time, completeness, and stopping reasons. Numeric results carry units, provenance (game read/calculated/observed), and missing-data reasons. Unknown is not zero. Old results retain an explicit “Outdated” badge.

Use session IDs mapped to weak actor references for early milestones. Never persist raw pointers. Cross-load stable references need an explicit prototype against the pinned game version; do not assume actor names or component ordering are stable. Later saved scopes must validate missing/replaced members and show a repair workflow.

## Connection graph: physical connection is not production

Represent directed port-to-port links and explicit internal transfers. An input/output count alone does not tell us how a building works.

- Belt/lift adapter: map its transport input to transport output and identify direction.
- Ordinary splitter/merger adapter: expose reachable branches; do not assume equal actual throughput.
- Storage adapter: treat as a buffer. Stop by default; player can explicitly continue through it. Its inventory breaks any inference that incoming and outgoing instantaneous flow are equal.
- Manufacturer adapter: stop at its input by default. A recipe consumes items and produces other items; it is not a conveyor pass-through. Later “Include production steps” expansion adds recipe dependencies explicitly.
- Unknown or unsupported actor: expose a labeled frontier. Never bridge it by proximity.

Maintain separate graph interpretations: transport reachability, production dependency, and measured item movement. “Reachable downstream” never means “currently flowing.”

### Bounded trace algorithm

1. Player picks a seed and direction: downstream, upstream, or both.
2. Resolve the intended port; ask through a small port picker if ambiguous.
3. Capture a revision and queue the starting port/state.
4. Traverse compatible external links and supported internal transitions.
5. Track visited ports/transitions to handle loops without losing branch edges.
6. Stop at selected endpoints, default buffer/production boundaries, unsupported actors, unresolved connections, or configured work limits.
7. Deduplicate members, retain all discovered edges, and return frontiers with explanations.
8. Show the candidate selection and allow edits. Do not automatically save it as the player's line.

Distinguish disconnected, unresolved, not loaded/not available, excluded, unsupported, and truncated states. Item filtering is an optional later query; geometric connectivity alone cannot prove which item reaches which branch.

## Logical scope and boundary

A scope is an explicit membership set. Its transport boundary consists of directed external connections with exactly one endpoint owner in that set. Entering edges are inputs; leaving edges are outputs. Disconnected ports are shown separately as open ports, not as established supply/demand. If endpoint data is incomplete, mark the boundary partial.

Selection methods, added in order:

1. Single object.
2. Traced candidate, then player review.
3. Add/remove individual objects and explicit stop points.
4. Later: box selection with an explicit center-inside or intersection rule.

Removing an object must not silently re-add it on refresh. Keep exclusions with the scope definition. Show isolated selected members and let the player choose whether to retain them.

A manufacturer can belong to the logical line while a nearby wall does not. Architectural objects may be attached as a separate spatial/decorative selection without becoming production graph nodes.

## Geometry and factory size

Begin with the world-axis-aligned union of selected supported building bounds. Show length, width, height in meters and label it “Bounding size (approx.).” Include belts and lifts when selected; allow category filters later.

This is an enclosing box, not occupied volume or usable space. Rotated machines, decorative meshes, and empty gaps can inflate it. Preserve the source/quality of every bound. Convert engine units at the adapter boundary with a validated scale fixture.

Later geometry layers:

- User-aligned oriented bounds for factories rotated relative to world axes.
- Per-floor footprint/occupancy, then access and service clearances.
- Player-defined buildable region, independent of current occupied bounds.
- Reserved transport corridors, openings, and architecture envelopes.

Do not publish a “space efficiency percentage” until usable area and required clearance have explicit definitions. Collision bounds alone cannot certify a valid factory layout.

## Expected production and observations

For a validated ordinary recipe: nominal item rate = quantity per cycle × 60 / cycle duration in seconds. Effective configured rate uses the game's validated clock and production modifiers; do not guess modifier behavior. Expected boundary totals require a complete supported scope and recipe set.

Belt capacity is an upper limit. It does not establish observed rate. Read tier/capacity from compatible game data rather than hard-coded remembered values.

For later observations, count transfers at a defined point and divide by elapsed simulation time. Capture each crossing once, document sampling coverage, reset on topology changes, and separate warmup from a valid window. Inventory differences and visual belt occupancy are not general throughput measurements. Prototype transfer instrumentation for conveyors/lifts before designing a universal sampler.

## Service responsibilities

| Proposed service | Responsibility |
| --- | --- |
| Selection service | Aim/select, port choice, editing and clear/cancel |
| Game adapter registry | Supported actor readers, version-specific access, honest failures |
| Snapshot builder | Consistent copied records and capture/completeness metadata |
| Trace service | Bounded directional traversal and frontier explanations |
| Scope service | Membership, exclusions, boundary ports, revisions |
| Geometry service | Bounds and later occupancy/clearance models |
| Analysis service | Pure calculations and evidence-based issues |
| Presentation model | Friendly labels, summary priority, visible status and actions |
| Highlight service | Local selection/path/port markers, bounded visual cost, cleanup |
| Observation service, later | Validated measurement windows and provenance |

Build these only as needed by a working slice; do not implement empty frameworks for every future module.

## Lifecycle, performance, and multiplayer

Scan on selection/refresh, not the whole world every frame. Use chunked work, cancellation tokens, a visited set, and caps. Starting tunable limits: 250 discovered buildings, 1,000 ports, and about 2 ms scan work per frame. These are proposed budgets, not benchmarks; profile them in the packaged game. Show partial results and the precise stopping reason when capped.

On dismantle, reconnect, recipe/config changes, or missing references, invalidate affected results when reliable hooks exist. Otherwise use bounded validation polling and a manual Refresh action; show capture age. Discard late results from an older request or world. Closing/world unload releases highlights, callbacks, and pending work.

First implementation supports single-player only. Keep selection/highlights client-local. Later, request authoritative server snapshots for data not reliably replicated. Validate requested scope and cap work per player; version snapshots and isolate concurrent requests. Do not claim remote-client or dedicated-server support until tested separately. SML's documented RCO/replicated-subsystem patterns are candidates, not a completed network design; see [sources](06-decisions-and-sources.md).
