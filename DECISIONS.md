# DECISIONS

Decisions made autonomously during the migration, with rationale. Items under
"Assumptions to confirm" need Trevor's review.

## Decided

### D1. Pinned at v16.0.1, not v16.1
The task said "upstream WLED 16.1", but upstream Aircoookie/WLED has no v16.1 tag as of
2026-07-11. The newest release tag is v16.0.1 (which contains the Seengreat HUB75 pinout
from PR #5662 that the task references as the template). Branch apollo/m1 is created at
v16.0.1. The branch is kept small and rebasable so moving to a future v16.1 tag is a
rebase, not a rework.

### D2. Upstream push protection
Local clone /Users/justinapollo/Code/ApolloAutomation/WLED originally had origin =
Aircoookie/WLED with a working push URL. Rewired: origin is now
https://github.com/ApolloAutomation/wled.git, upstream is Aircoookie/WLED fetch-only
with push URL set to the non-resolvable string DISABLED_push_to_Aircoookie_blocked.
An accidental "git push upstream" now fails instantly.

### D3. Baseline reconstructed from source, not a live device
No live M-1 was reachable (see BLOCKED.md B1). The shipping build config
(platformio_override.ini in WLED-MM-M1) plus WLED-MM source defaults are authoritative
for what a factory-fresh unit reports, so the baseline and the Phase 3 cfg.json were
derived from those instead of /json/cfg captures.

## Assumptions to confirm

### A1. mDNS hostname gets a unique suffix (deviation from wiki)
Wiki says literal "apollo-led-matrix". Per task instructions, shipping that literal
value on every unit collides when a customer has two M-1s on one network. Implemented:
apollo-led-matrix-XXXX where XXXX is derived from the last two MAC octets. The wiki
settings page rewrite reflects this. Confirm the suffix format before release.

### A2. AP SSID uniqueness
Same reasoning as A1 applied to the AP hotspot SSID. The current shipping build uses
SSID "Apollo M-1" for every unit. Implementation detail recorded in Phase 2/3 notes
once upstream's WLED_AP_SSID_UNIQUE mechanism was checked. Confirm desired SSID text.

### A3. AP password stays empty (open AP) to match shipping behavior
The shipping WLED-MM build sets WLED_AP_PASS="" which produces an OPEN access point.
The task's acceptance table says AP SSID/password must match the current WLED-MM build,
so the new build keeps the open AP. Tradeoff: anyone nearby can configure an
unconfigured M-1. Upstream default would be a password-protected AP. Flagging because
this is a security posture choice that should be a deliberate product decision.

### A4. Server description "Apollo LED Matrix" (acceptance table) vs "Apollo M-1"
(current compiled default)
Today the firmware compiles SERVERNAME "Apollo M-1" and the wiki has customers manually
change the description to "Apollo LED Matrix". The acceptance table is the spec, so the
new build compiles SERVERNAME "Apollo LED Matrix". If you prefer "Apollo M-1", it is a
one-line change in the apollo_m1 env.

### A5. Working branch naming
You said you created an "add m1 to wled" branch, but the ApolloAutomation/wled fork on
GitHub has only "main" (nothing else was pushed). The task spec names the branch
apollo/m1, so work proceeds on local branch apollo/m1 (created at v16.0.1) and pushes
to the fork under that name. If you want it named differently, rename at push time.

(Sections below are appended as later phases hit decision points.)
