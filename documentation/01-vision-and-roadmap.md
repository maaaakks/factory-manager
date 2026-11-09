# Vision and roadmap

## Product structure

Build one mod initially with a reusable core and five feature areas. Split distributions only when there is a concrete reason: different audiences, optional content packages, or incompatible dependency needs. Do not make players install five packages to test the first inspector.

| Area | First useful capability | Later progression |
| --- | --- | --- |
| Architectural design | Preview a selected wall module along one edge | Corners, openings, roofs, interiors, complete style kits |
| Production flow | Trace a connection, then compare recipe demand with capacity | Live rates, starvation/blockage evidence, recommendations |
| Spatial layout | Show occupied bounds of a selected line | Arrange rows, preserve access, stack floors, compare alternatives |
| New production lines | Calculate machines for one product and selected recipe | Multi-step chains, alternate recipes, resource/power constraints |
| Factory transport | Preview one belt connection between chosen ports | Obstacles, elevation, capacity allocation, shared corridors |

## Common delivery sequence

1. Establish a reproducible development environment and an in-game panel.
2. Select and identify one object.
3. Discover ports and direct neighbors.
4. Trace directed connections with visible limits.
5. Let the player define and edit a named line.
6. Calculate boundary inputs/outputs and basic spatial bounds.
7. Read recipes and configured rates; calculate simple expected balances.
8. Prototype real flow measurement; expose it only when validated.
9. Add evidence-based diagnoses and suggestions.
10. Plan new lines, place layout previews, route belts, and apply style modules.

Detailed foundation slices are in [the backlog](05-foundation-backlog.md). Later stages are dependency order, not a promise that all five modules must wait for a complete optimizer. Architecture previews can start once selection and geometry are reliable; conveyor routing can start once ports and obstacle queries are reliable.

## First complete user journey

Player opens Inspect, selects a belt, follows the downstream path, reviews the proposed set, adds/removes buildings, names it “Iron plates,” then sees boundary connections and approximate dimensions. Clicking an entry highlights its location in the world.

This journey establishes the shared foundation without requiring live item counting or automatic construction.

## What optimization will mean

Each request needs an objective and constraints. “Smallest” alone is insufficient: a compact arrangement can have inaccessible machines or long vertical transport.

| Objective | Constraints to retain |
| --- | --- |
| Increase output | Available input, recipe, belt capacity, machine configuration |
| Reduce footprint | Allowed height, clearance, walkways, usable ports |
| Use vertical space | Floor spacing, lift access, structure envelope |
| Reduce transport | Endpoints, throughput target, obstacles, allowed belt tiers |
| Match architecture | Selected asset/style kit, module dimensions, doors and reserved zones |

Start with one objective and a small supported case. Display tradeoffs in later comparison views.

## Repeatable definition of done

A slice is done when a player can discover and use it without console commands, its known fixture produces the expected result, an unsupported/error case has a useful message, cancellation works, and evidence records the exact game/mod versions tested. Local build success is distinct from packaged in-game success.
