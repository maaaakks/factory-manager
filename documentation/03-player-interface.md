# Compact player interface

## UX baseline

The mod should be immediately useful during normal play. Opening the tool must show an action the player can take, and every result should link back to something visible in the world. First-time inspection should require no settings changes or console commands.

Use one shared tool shell. Start with Inspect only. Add feature areas when usable; do not fill the first version with disabled optimization/design tabs.

## Three interaction states

1. **Targeting:** cursor remains captured by the game. Aim at an object; a small hint shows its name and the current Select binding. No pointer buttons are active here.
2. **Inspecting:** freeze the selected target and open a compact pointer-enabled panel. Camera/build actions do not fire through the panel. The panel does not pause the simulation.
3. **Picking in world:** Add, Remove, Pick port, or Pick stop temporarily returns to targeting with an explicit mode banner. Escape cancels that pick and restores the panel.

This avoids expecting the player to aim and click UI controls simultaneously. Input behavior is part of the first prototype, not polish saved for later.

## Compact panel

Initial design target: approximately 380–440 logical pixels wide at a 1080p reference, anchored to a screen side within the safe area, height capped near 60% of the viewport. This is a starting layout target; scaling and in-game readability tests decide the final size.

```text
FACTORY TOOLS                 [—] [×]
Inspect
Conveyor belt                [Locate]
Connected • captured just now

Capacity         120 items/min
Direction        A → B
Connections      2 connected
Measured flow    Not measured

[Trace downstream]   [More ▾]
```

Numbers above are illustrative UI data, not a tier specification or measured result. When capacity is unavailable, show “Unavailable” with a short reason rather than a guessed value.

The More menu contains Trace upstream and Ports initially. Both-directions trace can appear later. Selection, Refresh, and Settings remain reachable from the shell without crowding the primary action row.

## Trace review

```text
Downstream path              [Locate]
8 buildings • 2 branches
Partial: stopped at storage

Ends
Storage container            [Show]
Open belt end                [Show]

[Define line]       [Edit selection]
```

“Partial” means the trace has an unresolved/limited reachability result; a normal supported configured endpoint may instead be a complete trace with “Stopped at storage.” Use the precise state returned by the service. A selected endpoint does not inherently make a result incomplete.

Show at most three priority summaries before a scrollable details area. Branches and endpoints appear as a list with Locate actions. A full node graph is optional later; the first UI should not require understanding one.

## Named line overview

```text
Iron plates                  [Rename]
12 buildings • Complete

Inputs / outputs    2 in • 1 out
Bounding size       24 × 16 × 8 m
Production          Not analyzed

[Connections] [Bounds] [Edit]
Updated 4 s ago              [Refresh]
```

Counts are connection crossings, not distinct item types. Connection details say “Input connection,” its item if known, and the endpoint. Grouping per item is added only when supported data exists. Dimensions are approximate world-axis bounds until a more precise geometry model exists.

## Editing a line

Offer Add building, Remove building, Set trace stop, and Clear selection. Keep an Undo last selection edit action; it only changes selection. Preview pending membership highlights and confirm with Done. Cancel restores the pre-edit membership. A name is optional until saving named scopes is implemented.

Do not ask the user to confirm every read-only action. Later construction features need a separate preview and Apply action with an explicit affected-object summary; closing a panel must never apply a plan.

## Highlight language

| Meaning | Visual treatment |
| --- | --- |
| Selected object | Outline plus a small selection marker |
| Traced path | Distinct outline and sparse direction arrows |
| Boundary input/output | Labeled IN/OUT port markers and arrows |
| Trace stop | Endpoint marker and reason on focus |
| Problem | Warning icon, affected-object outline, short explanation |
| Unsupported | Dashed/question marker plus text |

Color supplements shape and text. Use the game's existing visual language where compatible. Keep markers local to the requesting player. Default to selected/nearby endpoints rather than thousands of labels. Occluded highlighting and any rendering changes require a compatibility/performance prototype; fall back to visible markers and Locate directions.

Locate highlights/pings an object and provides direction/distance. It does not teleport the player or forcibly rotate their camera. World markers expire or disappear with the tool unless explicitly pinned.

## Status and recovery copy

| State | Player-facing text/action |
| --- | --- |
| Nothing selected | “Aim at a conveyor to inspect it.” |
| Unsupported target | “This building is not supported yet. Select a vanilla conveyor.” |
| Multiple ports | “Choose an output to follow.” |
| Scanning | “Tracing… 42 buildings found.” plus Cancel |
| Scan cap | “Stopped at 250 buildings. Narrow the selection or add a stop.” |
| Missing object | “This object was removed. Refresh the selection.” |
| Outdated | “Connections changed. Refresh to update.” |
| Unknown item | “Item not identified.” |
| Observation unavailable | “Flow measurement is not available for this connection.” |
| Cancelled | “Trace cancelled.” Preserve the last accepted result. |

Show the most actionable issue in the summary and keep technical diagnostics behind Details. Missing measurements must never look like zero flow.

## Controls and settings

Use rebindable actions integrated with the pinned game's input system. Pick an available default binding after conflict testing; display the actual current binding in hints. Avoid hard-coding a familiar key that may already be used.

Escape unwinds the current pick/edit state first, then closes the panel; closing releases pointer focus and input contexts. Respect inventory, build gun, pause menu, and other modal widgets. In targeting mode, tool selection must not simultaneously build, dismantle, fire, or interact.

First settings: UI scale, reduced highlight intensity, show/hide world labels, and input bindings. Advanced scan limits belong in an advanced section with defaults. Diagnostics are optional. Normal settings should be accessible in game; SML provides a documented configuration UI mechanism (see sources).

## Usability acceptance

- A new tester reaches the first valid inspection in under 30 seconds without verbal help; this is a proposed goal to measure.
- Inspect one target in at most two deliberate actions after opening the tool.
- Primary text and units remain readable at 1080p and 1440p, including increased UI scaling.
- Keyboard focus order is visible; controls do not rely on hover-only explanations.
- Support long names/localized text through wrapping or details, not unreadable shrinking.
- Never rely on color alone; selection and error states have labels/icons.
- Escape, cancel, reopening, inventory, and build-gun transitions never leave input captured.
- A tester can explain whether a displayed number is capacity, calculated rate, or measured rate.

Start with mouse/keyboard. Controller support must be tested as a separate deliverable before being advertised. Use localizable text from the beginning even if English is the only initial translation.
