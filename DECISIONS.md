# DECISIONS

Decisions made autonomously during the migration, with rationale. Items under
"Assumptions to confirm" need Justin's review.

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

### A3. ANSWERED (session 3, Justin's D1): AP password is wled1234
The session-2 build shipped an open AP to match WLED-MM. Justin decided: use WLED's
documented default password wled1234. Applied in [env:apollo_m1]. Logged consequence:
OTA-upgraded units keep whatever AP configuration their existing cfg.json carries
(for WLED-MM units that is the open AP); only a full-erase flash gets the password.

### A4. ANSWERED (session 3, Justin's D4): server description is "Apollo M-1"
The session-2 build used "Apollo LED Matrix" from the old acceptance table. Justin
decided "Apollo M-1". Applied in [env:apollo_m1] and apollo/fs/cfg.json.

### A5. SUPERSEDED (session 3): canonical repo and branch
Canonical fork is ApolloAutomation/WLED-M1 (a prior session note guessed "wled"; the
old ApolloAutomation/wled clone is retired, read-only). Working branch is
m1-wled-update, pushed. The prepared upstream PR branch hub75-first-boot-defaults is
pushed to the same fork.

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

## Session 3 decisions (2026-07-11)

### D11. Branch consolidation used a pointer move, not merge or rebase
m1-wled-update sat at upstream main tip c7d41a8e with zero unique commits.
`git merge --ff-only prior/apollo/m1` refused (diverged), and a literal rebase would
have replayed the 622 upstream commits between v16.0.1 and main onto the Apollo work.
TASK.md A4's own semantics create the working branch AT the prior work, so the branch
pointer was reset to prior/apollo/m1 (nothing lost: zero unique commits, verified
before the move) and M1_FACTS.md committed on top.

### D12. [env:apollo_m1] rewritten to inherit, not restate (the audit)
The env now expands ${env:esp32s3dev_16MB_opi_hub75.build_flags} and unflags the
inherited release name (the waveshare pattern from upstream main). Deleted as
duplication: MOONHUB_S3_PINOUT, LEDPIN/BTNPIN/RLYPIN/IRPIN/AUDIOPIN, SR_DMTYPE and
all I2S pin defines, and the four flag-group references; all of them arrive from the
parent env. What remains is pure Apollo delta: identity strings, AP/mDNS uniqueness,
factory 64x64 defaults, ABL off, PIXEL_COUNTS, and the WLED-MM migration shim.

### D13. DEFAULT_LED_COUNT define was silently ineffective; replaced with PIXEL_COUNTS
const.h defines DEFAULT_LED_COUNT (and DEFAULT_LED_TYPE) unguarded, so the compiler
redefines any -D value back to the header default (warning only visible in full build
logs). The prior session's -D DEFAULT_LED_COUNT=4096 never took effect; harmless in
practice because BusHub75Matrix derives its length from panel dimensions, but wrong.
Now using -D PIXEL_COUNTS=4096, which cfg.cpp guards with #ifndef and actually honors.

### D14. ANSWERED live (2026-07-12): factory welcome color is Apollo blue 0x4379AA
Justin saw the orange factory boot on hardware and chose Apollo blue #4379AA.
Implemented via a new #ifndef guard on DEFAULT_COLOR in FX.h (it was unguarded,
same trap as D13) plus -D DEFAULT_COLOR=0x4379AA in the env. Original proposal
kept below for the record.

### D14-old. Boot visual (Apollo delta item 7): proposal, superseded
Current factory boot state: power on, Solid effect, warm orange 0xFFAA00, brightness
128, full 64x64 segment. That is visible light within a couple of seconds and cannot
brown out a 3A supply. Options for something livelier:
  a) keep Solid orange (recommended until hardware QA: zero risk, proof of life,
     matches stock WLED expectations)
  b) ship preset 1 = a gentle 2D effect at brightness 128 with bootPreset=1
     (one more delta surface, needs gamma-shifted color check on hardware first)
Justin picks after seeing option (a) on a real panel in QA.

### D15. ANSWERED live (2026-07-12): AudioReactive defaults to ON (Justin's D3)
Justin decided during the hardware session: -D UM_AUDIOREACTIVE_ENABLE is set, so
factory units boot with the usermod active on the baked pins (rev6 with mic needs
zero interaction). The rev4 no-mic cost (CPU, heap, refresh, noise-driven audio
effects on a floating input) remains a QA D9 measurement item; if it proves
significant, the fallback is a rev4-specific decision, not a silent revert.

### D16. ANSWERED live (2026-07-12): setup hotspot is OPEN again (reverses D1)
After walking the customer flow on hardware, Justin chose to drop the AP password
so customers join and start playing with no password step. This restores the
WLED-MM shipping posture. Tradeoff accepted deliberately: an unconfigured unit
(or one that loses WiFi) can be configured by anyone in radio range until it is
on the customer's network. wled1234 no longer appears in the binary; the unique
SSID per unit (Apollo M-1-xxxxxx) stays. OTA-updated units that saved wled1234
keep it unless cleared; the demo unit was cleared via the API (ap pskl 0).

### D17. ANSWERED live (2026-07-12): image tools and factory presets pre-installed
Justin asked for the image tool, scrolling text, and pixel paint out of the box.
Implemented: WLED_ENABLE_PIXART + WLED_ENABLE_PXMAGIC serve /pixart.htm (pixel
paint) and /pxmagic.htm (image upload) on the device (the Pixelforge workflow
depends on them; WLED-MM had them built in). Factory presets baked into the
filesystem image, authored on the live unit and downloaded back (format exact):
1 Scrolling Text ("APOLLO M-1" in Apollo blue, text edits via segment name),
2 Apollo Blue (solid, the boot look as a tappable preset), 3 Sound Bars (GEQ,
gives the audio-on default a face; harmless idle bars on rev4 - flag if
unwanted). Boot remains preset-less solid Apollo blue; presets are one tap away.

### D17 addendum (2026-07-12, correcting the picture)
Pixelforge itself turned out to be BUILT INTO upstream WLED 16.0.1 (served at
/pixelforge.htm, enabled by default via #ifndef WLED_DISABLE_PIXELFORGE) - the
Apollo tool was upstreamed. Its image and GIF functions un-greyed once b2 enabled
the pixart/pxmagic machinery, verified working from Justin's PC (GIF upload and
playback). "Installing pixel paint" is Pixelforge's own module system writing
pixelpaint.htm.gz to the device filesystem. Per Justin's pre-installed request,
the factory image now ships the Pixel Paint module v1.11 by @dedehai
(DedeHai/WLED-Tools, EUPL-1.2, same license as WLED) plus the pftools.json
catalog, so pixel paint works out of the box with no install step. Video Lab and
Font Factory remain one-tap installs inside Pixelforge (not shipped, not asked).

### D18. ANSWERED live (2026-07-12): PixelForge only; legacy tool pages dropped
Firefox-on-the-same-phone proved the image greying was the WLED Android app's
file-chooser bug, not firmware: PixelForge is self-contained (own GIF encoder,
no references to the legacy pages), so the b2 pixart/pxmagic enablement was a
red herring and Justin called the old Pixel Magic tool outdated. b5 removes
WLED_ENABLE_PIXART and WLED_ENABLE_PXMAGIC (leaner app, back to upstream
defaults); the supported flow is the built-in /pixelforge.htm plus the
pre-installed Pixel Paint module. App bug report drafted for Justin to file
(apollo/WLED_APP_BUG.md); phone workaround is any mobile browser.
