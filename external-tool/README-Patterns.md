# Simple production patterns

The workshop starts with three repeatable patterns: smelter, constructor and assembler. Choose a standard recipe and 1–16 machines. Each pattern places production on the upper slab and routes its manifolds through a separate logistics floor with 4 m of clearance. Assemblers use separate input lanes and elevations.

New automatic layouts use individual machines and the same row-based generator, including the Compact density setting. They no longer select the old reinforced-plate blueprint. Existing saved projects and legacy exports remain readable. New patterns have no fixed control room or decorative interior; architecture can be added separately.

Manual construction and network tools are grouped in a foldout. Production and Logistics floor buttons switch the plan's active level. The gallery and creation detail pages use the app's shared navigation and theme selector.

Checks: `python tests/check_simple_patterns.py <external-tool> <scratch-directory>`, then `node tests/check_simple_patterns.cjs <external-tool> <scratch-directory>/projects.json`. These check all three machine types at 1 and 4 machines, native binary roundtrips, two-input assembler routing, an eight-machine production chain, and generation without the legacy blueprint. Actual placement in Satisfactory remains unverified.
