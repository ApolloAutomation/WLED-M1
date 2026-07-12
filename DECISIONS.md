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

### D4. No APOLLO_M1_PINOUT block; the pinout is already upstream
The task planned a new #elif in bus_manager.cpp modeled on the Seengreat block. Not
needed: upstream v16.0.1 already contains MOONHUB_S3_PINOUT (wled00/bus_manager.cpp:
887-890) with GPIOs byte-identical to the shipping MM build ({1,5,6,7,13,9,16,48,47,
21,38,8,4,18}), plus env esp32s3dev_16MB_opi_hub75 (platformio.ini:881-893) that
already carries the M-1 aux pins and I2S mic pins. The MoonModules HUB75 work was
upstreamed before 16.0.1. Adding a duplicate APOLLO_M1_PINOUT would be rejected as
redundant. Consequence: the planned "apollo-m1-pinout" upstream PR is replaced by a
PR that fixes HUB75 first-boot defaults (the genuinely missing piece; see D6).

### D5. Phase 1 collision check: PASS
HUB75 {1,4,5,6,7,8,9,13,16,18,21,38,47,48} vs I2S mic {10,11,12} vs BTN 0, RLY 15,
LEDPIN 14: disjoint. No pin manager conflicts.

### D6. Upstream PR content = HUB75 first-boot defaults fix
Upstream cannot create a HUB75 bus from compile-time defaults: the cfg.cpp first-boot
GPIO sanitization mangles the HUB75 config slots (panelW=64 fails isPinOk). Upstream
main even removed LED_TYPES=65 from hub75 envs because of this (commit 66069245). The
prepared PR adds the isHub75 carve-out to the sanitize loop (mirroring the carve-out
that already exists in validatePinsAndTypes) plus optional DEFAULT_PANEL_WIDTH/HEIGHT
seeding. Branch: hub75-first-boot-defaults off upstream/main. PR description drafted,
PR NOT opened.

### D7. Dropped MM-only usermods
ARTIFX (MM-exclusive, no upstream equivalent), Auto Playlist, Auto Save, Animartrix
were compiled into the MM build but none are part of the acceptance spec and none had
shipped runtime configuration. They are not in the apollo_m1 env. Animartrix in
particular has a non-EUPL license attached upstream. Add back individually via
custom_usermods if a customer-visible regression is identified.

### D8. WLED_BRAND stays "WLED"
The UI keeps saying WLED (community-first; customers follow generic WLED tutorials).
Apollo identity comes from WLED_PRODUCT_NAME "Apollo M-1", WLED_RELEASE_NAME
"Apollo_M-1", server description "Apollo LED Matrix", and the AP/mDNS names.
/json/info reports brand WLED, product Apollo M-1, release Apollo_M-1, ver 16.0.1.

### D9. Version string stays 16.0.1 (no Apollo suffix)
set_metadata.py injects the version from package.json; adding a second -D WLED_VERSION
would produce a redefinition. 14.5.1-dev -> 16.0.1 is the OTA-visible bump. The
Apollo build is identified by release/product strings instead.

### D10. Shipping MM bug found in passing: release name self-cancelled
platformio_override.ini lists -D WLED_RELEASE_NAME=Apollo_M-1 in BOTH build_flags and
build_unflags, so shipped units report release "mdev_release" instead of Apollo_M-1.
No action needed in the old repo (it is being retired), but OTA tooling must not
match on release name "Apollo_M-1" for currently fielded units.

## Assumptions to confirm (continued)

### A6. mDNS unique suffix is 6 hex chars, not 4
Task suggested apollo-led-matrix-XXXX. Implemented apollo-led-matrix-XXXXXX (last 6
MAC hex chars) to match the existing upstream convention used for the AP SSID, MQTT
topic and client id (wled.cpp:536-539). One mechanism, one suffix length everywhere.
24 chars total fits the 32-char cmDNS buffer.

### A7. AudioReactive ships compiled but runtime-disabled (matches WLED-MM)
Ground truth: the shipping MM build compiles the usermod but boots with enabled=false;
rev6 customers enable it in Usermod settings. The new build does the same, with type
Generic I2S and pins SD 10 / WS 12 / SCK 11 already baked so enabling it needs no pin
entry. Tradeoff if you enable by default instead: rev6-with-mic works out of the box,
but rev4 units (no microphone) would run FFT sampling against a floating input,
wasting CPU and showing noise-driven effects if a customer selects an audio effect.
One firmware serves both revisions, so disabled-by-default is the conservative choice.
Flip = one define (-D UM_AUDIOREACTIVE_ENABLE) or one line in the shipped cfg.json.

(Sections below are appended as later phases hit decision points.)
