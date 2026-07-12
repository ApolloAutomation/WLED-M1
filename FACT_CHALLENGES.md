# FACT_CHALLENGES

Contrary evidence found by the session-3 adversarial verification pass (one agent per
fact, briefed to prove each wrong). Facts 1 and 3 survived attack unchanged. Facts 2
and 4 need corrections to their TEXT; no code on m1-wled-update changes because of
either. Full agent evidence with file:line cites is preserved in the session log.

## FACT 2: verdict PARTLY_WRONG (prose precision, not substance)

Everything structural survived: upstream does not encode panel size in the type;
HUB75 pins slots are {panelW, panelH, chain, rows, cols}; LED_TYPES is the operative
define; DEFAULT_LED_TYPE framing belongs to WLED-MM only; nothing on m1-wled-update
depends on the wrong framing.

Two precision defects in the fact's failure-mode sentence ("the default bus comes up
with the wrong panel width/height/chain and with no 2D matrix configured"):

1. On pristine v16.0.1 with only the [hub75] flag group (no DATA_PINS), first boot
   creates ZERO buses, not a wrongly sized one: cfg.cpp:280 breaks out because HUB75
   needs 5 pin slots and DATA_PINS defaults to the single DEFAULT_LED_PIN, and
   finalizeInit has no zero-bus fallback in v16.0.1. The baseline symptom is a DEAD
   display, not a small one. (The 32x32 quadrant symptom customers see today comes
   from WLED-MM's DEFAULT_LED_TYPE=101, which IS a wrong-size default; the two
   codebases fail differently.)
2. "wrong chain" is not accurate for the DATA_PINS=64,64,1,1,1-on-unpatched-upstream
   case: slot values of 1 are valid GPIOs and pass the sanitize loop untouched, and
   the constructor clamps chain to 1..4. Only the two 64s get destroyed.

Consequence: none for code. The three-part fix on m1-wled-update (DATA_PINS +
isHub75 sanitize carve-out + DEFAULT_PANEL_WIDTH/HEIGHT seeding) is exactly right,
and all three parts are required together.

## FACT 4: verdict PARTLY_WRONG (the upstream half; MM half confirmed)

MM half confirmed: EXCLUDE_FROM_ABL(t) exists at WLED-MM const.h:264 and is consumed
in estimateCurrentAndLimitBri and getLengthPhysical. MM never applies ABL to HUB75.

Upstream half WRONG on both specific claims:
1. BusHub75Matrix does NOT inherit _milliAmpsPerLed/_milliAmpsMax. Those members
   live on BusDigital (and BusPlaceholder), not the Bus base class. BusHub75Matrix
   discards the BusConfig milliamp fields; the base-class current getters return 0.
2. Upstream DOES have an exemption, structurally: every ABL loop is gated on
   bus->isDigital() (bus_manager.cpp:1452, 1461, 1468, 1488, 1513), and HUB75 types
   64-71 are outside the digital ranges. The "255 sentinel" is a WS2815 power-model
   selector, not an exemption, and is irrelevant here.

Consequences:
- The feared dim/near-black panel from fictional ABL math CANNOT occur on upstream
  16.0.1 for a HUB75 bus, under any maxpwr value.
- The planned second upstream PR (HUB75 ABL exemption) is CANCELLED: nothing to patch.
- ABL_MILLIAMPS_DEFAULT=0 and cfg.json maxpwr=0 stay in the apollo_m1 build anyway:
  the acceptance spec wants the limiter checkbox to read unchecked, and 0 keeps the
  UI power readout from showing an irrelevant estimate. They are defense-in-depth,
  not a functional requirement.
- Any dim or black panel seen in hardware QA must be attributed to geometry/scan
  rate, driver chip, or HUB75 brightness handling, not ABL. The QA checklist points
  there first.

## FACT 3 refinement (fact CONFIRMED, one overstatement noted)

"MUST build_unflags the inherited WLED_RELEASE_NAME" applies only when the child env
interpolates ${env:parent.build_flags} (which apollo_m1 now does). Envs that rebuild
build_flags from the section groups replace the option wholesale and need no unflag;
the waveshare env's own unflag is actually a no-op for that reason. Verified against
PlatformIO 6.1.19 source: unflags run AFTER flags and match the exact (name, value)
tuple, so the unflag token must be the exact escaped old value; a bare
-D WLED_RELEASE_NAME unflag would delete the new name too. The apollo_m1 env uses the
exact-token form and the build shows zero redefinition warnings.
