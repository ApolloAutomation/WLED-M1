# BENCH SESSION: post-b7 tester feedback, QR redesign, business tail (2026-07-15)

Resume file for this session. Prior context: BENCH_SESSION_AP.md, SUMMARY.md.
Focus rewritten live: tester feedback landed (first-boot tour + QR + release
hosting), so the b7 gate re-run is superseded by a b8 gate after the redesign.

## Session state (established)
1. FACT 1 restated and unchanged (half scan, type 65).
2. Serial port this session: /dev/cu.usbmodem2101 (NOT 1101; Mac USB port
   changed). Logger copy with the new port in the session scratchpad.
3. UNIT ON USB IS A THIRD UNIT: base MAC 30:ed:a0:2f:5e:50, suffix 2f5e50.
   Neither the test unit (6d0a40) nor the demo unit (2f5f7c). Boot log clean
   (SPI_FAST_FLASH_BOOT, console-silent production build, no panic loop).
   NOT to be erased or flashed until Justin says what it is.
4. Memory directory was EMPTY at session start (m1-bench-techniques memory
   lost); rewritten this session from apollo/bench/README.md + new findings.
5. Mac is on 192.168.1.x wired; 192.168.20.x subnet (demo unit, Belle
   lights) unreachable right now. Demo unit not reachable by mDNS either.

## Tester feedback ledger (2026-07-15, this session's driver)
- Tour: workshop it; ONE static page instead of a cycling playlist (missed
  frames force a wait for the loop); instructions unclear for newcomers;
  "hotspot" wording confuses non-technical users; the final card assumes
  the phone is already on the M-1 WiFi; the QR page should carry the QR
  plus the actual address as text below it, QR slightly smaller.
- Reference point: Pavlov's ESPHome firmware "bios screen" showing all
  relevant info until provisioned.
- QR does not scan in a normally lit room (reproduced by tester on iPhone
  AND Android; scanned OK at arm's length in earlier low-light bench work).
- Captive portal: tester expected a signin popup; modern phones show none
  (that is D22 by design); ONE OLDER ANDROID still popped the WLED window.
- Distribution: put the bin on a GitHub release on our repo instead of the
  Google Drive link.

## Desk research verdicts (workflow wf_82237fdd, four agents + verify pass)
1. QR scannability (sourced): the dark-room-pass/lit-room-fail signature is
   explained by (a) inverted polarity being a documented Android decoder
   gap (ZXing ALSO_INVERTED off by default, ML Kit issues), (b) the glossy
   bezel being an invalid quiet zone in room light, (c) LED dot texture
   breaking module continuity once short exposures stop the blooming that
   fused dots in the dark. PREDICTED BEST FIX: standard polarity, 2px
   modules (42px code), lit on-panel quiet zone; ECC M->Q is free in
   alphanumeric mode at v1; brightness needs a sweep (inverted-U, peak
   likely 60-160/255). Full matrix in the session scratchpad, sources kept.
2. Captive/older Android (sourced, code-verified): captivePortal() answers
   ALL generate_204/gen_204 paths with 204 regardless of Host, Apple and
   Windows probes with Success; every OTHER path 302s to 4.3.2.1, which IS
   the popup trigger. Stock Android 4.4-16 always probes a generate_204
   URL, so the old-Android popup means either (most likely) a non-Google
   probe path (Amazon Fire OS wifistub.html is the prime suspect) hitting
   the 302 catch-all, or the unit ran a pre-D22 bundle. Distinguisher:
   same-session modern phones showing no popup points at the current
   bundle. NO firmware action needed; tester reply text drafted.
3. Release hosting (sourced): GitHub release assets still send no CORS
   headers in 2026, so ESP Web Tools CANNOT fetch them; dual-publish is
   the answer: release assets for human downloads (stable
   releases/latest/download links, sha256 sums, EUPL source pointer) and
   manifest+bin copies served same-origin with the installer page (GitHub
   Pages). jsDelivr rejected (cannot serve release assets; 20MB practical
   cap vs our 16MB near-miss; CDN cache is a rollback liability). Tag
   convention m1-b<N> to avoid upstream v* collisions. Release body
   drafted; gh commands staged, NOT run.
4. Three upstream PR texts drafted (AP sleep, force-scroll, freeze-thaw)
   with branch names, target main per CONTRIBUTING.md, honest semantics
   caveats (freeze-thaw preset interaction called out). Adversarial verify
   pass ran against v16.0.1 source and git history; final text lands in
   apollo/UPSTREAM_PRS_READY.md.

## Redesign build (FS-only, zero firmware delta)
- wled.cpp hook applies FACTORY_SIGNPOST_PRESET=9 while WiFi is
  unconfigured; preset 9 changes from playlist to a single static card, so
  NO firmware change. Playlist end semantics verified in playlist.cpp for
  the dog-once option: repeat:1 + end:5 plays the dog 4s then holds the
  card (loadPlaylist adds one repetition, handlePlaylist applies end
  preset at rollover).
- Generator committed: apollo/bench/gen_setup_card.py (variable-width 5px
  caps font + 7px digits, QR via python qrcode, v1 alphanumeric).
- Card variants staged in scratchpad: cardA_invM/invQ (inverted 2px, one
  top line JOIN:APOLLO M-1, 4.3.2.1 below), cardA_stdM (standard polarity,
  lit quiet zone), cardB_invM (two top lines, tighter quiet zones).
- presets_optA.json (presets 1-4 + 9 Setup card; setup cards 5-8 removed)
  and presets_optB.json (5 = card, 9 = one-shot dog playlist end->5).
- Bench iteration plan: join test unit AP, upload variants via /upload,
  live-switch via JSON API, Justin scans each in normal room light
  (iPhone + Android), brightness sweep via bri. Winner ships as
  apollo/fs/setup.gif + final presets.json; then virgin + AP walkthrough
  gates on b8. D13 gate text needs updating to the static page wording.

## D11 groundwork (HA MCP, desk-side reads only)
- HA has exactly ONE wled config entry: "The Belle Permanent Lights",
  zeroconf-discovered, host 192.168.20.30, state setup_retry (unreachable
  since early Jan per modified_at), options keep_master_light=false. All
  its entities unavailable; script.all_lights_on references them.
- The M-1 demo unit has NEVER been added to this HA. D11 click-through
  needs the demo unit powered + reachable and a pending zeroconf flow.

## Asks handed to Justin (batched, this session)
1. Identity of USB unit 2f5e50 (third unit?) and whether it may be erased.
2. Approve the gate plan: skip the b7 re-run, gate once on b8 after the
   tour redesign is approved on glass.
3. Card design pick on glass + QR variant scan matrix (his phones).
4. Demo unit power/network status for D11/D12; whether to run the D12
   restore (it erases the demo unit's current state).
5. Tester follow-ups: old-Android device make/model (Fire tablet?), and
   which bundle that unit ran.
6. Go/no-go on publishing the GitHub release once b8 exists (commands are
   staged, nothing published).

## Paste-ready tester reply: captive popup question (verified against source)
> Correct, and it is deliberate: WLED normally answers the phone's "is there
> internet here?" checks with a redirect, which is what makes the sign-in
> popup appear. We changed that on purpose. The popup only opens a crippled
> mini-browser that cannot upload files, and worse, while the network looks
> "captive" Android keeps routing the real browser over mobile data, so
> http://4.3.2.1 never loads unless you turn data off. Instead we answer
> those checks with "all good", so the phone treats the hotspot as a working
> network and the normal browser reaches 4.3.2.1 with mobile data still on.
> The tradeoff is no automatic popup, which is why the panel itself shows
> the join-then-browse instructions and the QR code on first boot.
>
> The older Android popping the control window is not a bug and needs no
> fix. We only answer the standard check URLs (the generate_204 family,
> Apple, Windows). Older or non-Google devices, Amazon Fire tablets
> especially, check a different URL, and anything we do not recognize still
> gets the classic redirect, so those devices show the old-style popup. On
> those devices that is harmless and actually convenient: the popup lands
> straight on the control page.
>
> Two things would help us confirm: (1) the make, model, and OS version of
> the older device, and (2) whether that unit was on the b7 bundle when you
> tested. If the unit had an older bundle, every phone would get the popup,
> so no popup on your modern phones in the same session already suggests
> the bundle was current.

## Hardware log addendum (14:00)
- One-shot dump of unit 2f5e50 FAILED to start: esptool cannot connect
  ("No serial data received") though the USB JTAG device still enumerates
  and the same tool read the MAC 15 minutes earlier. The bench logger's
  clean-reset dance now also returns zero bytes. Diagnosis: the S3
  USB-Serial-JTAG wedged state; needs a physical unplug/replug of the
  USB-C (or unit power cycle). NOTHING was written to the unit's flash;
  the dump had not started (chunk 0 never read).

## QR scan matrix results (2026-07-15 afternoon, Justin on glass, lit room)
Unit: test unit 2f5e50, flashed b7 full install this session (write --erase-all,
hash verified, virgin boot clean). Test loop deployed by uploading a modified
presets.json (preset 9 = test playlist) + reboot; every reset then lands back
in the loop. LESSON: the JSON psave API does NOT save an inline playlist
object; it snapshots the currently showing state (two rounds were lost to
stale tour frames before switching to the file-upload approach).

Round 1 (all bri 90, 25s frames): invM card / stdM card / std full-field /
b7 3px control -> results overtaken by the psave bug, rerun as round 2.
Round 2 (bri 220 vs 90): ONLY the inverted 2px card at bri 220 scanned, and
intermittently; BOTH standard-polarity (lit background) frames failed at
both brightnesses. Photo evidence: no refresh banding at 220; LED dots
sharply resolved with bloom; a "lit background" on P2.5 is really a dot
grid with black gaps (~16 percent fill), which the binarizer reads as
noise. THE RESEARCH PREDICTION (standard polarity wins) IS REFUTED ON
DISCRETE-LED GLASS; the brightness prediction is CONFIRMED (90 -> 220 was
the difference between never and sometimes).
Round 3 (all inverted, all bri 220): dim-text ECC-Q card = once out of
multiple tries; 3px full-panel (bezel quiet zone) = never; amber modules =
never; original 2px card = once out of multiple. Conclusions: quiet zone
dominates module size (3px edge-to-edge loses to 2px with on-panel border);
text dimming and ECC Q do not rescue it; amber loses luminance for nothing.
Distance test (~5 ft): both surviving cards scan but STILL INTERMITTENT.

VERDICT: on bare P2.5 glass in a lit room, a 64px QR is intermittent at
best in every software configuration. Best-achieved: inverted 2px modules,
on-panel dark quiet zone, bri 220. The physics (dot fill factor) is the
binding constraint; a diffuser front would likely fix it (product/hardware
lane, not firmware).

## OPEN DECISION for next session (D24 pending)
Ship card, two options:
A. Keep the QR as best-effort: cardB2_invM at bri 220 ("1 JOIN WIFI /
   APOLLO M-1 / QR / 2 SCAN OR 4.3.2.1"). QR works sometimes (dark rooms,
   patient users); the text address is the reliable path.
B. Drop the QR: large-text card only ("1 JOIN WIFI: APOLLO M-1 /
   2 OPEN BROWSER: 4.3.2.1"). No false affordance, nothing to fail.
RECOMMENDATION on the evidence: B, or A with the QR visually de-emphasized;
an intermittent QR invites the exact thumb-twiddling the tester reported.
Justin approved: one gate only, on b8, after this decision. Justin picked
the cardB layout + step numbering + "scan or url" wording (his messages).

## Where everything stands at session pause (2026-07-15 ~16:00)
- Test unit 2f5e50: b7 + MUTATED presets (preset 9 = QR test loop r3,
  presets 11-23 = test cards, bri 220). Fine for more QR testing; MUST be
  re-flashed for the b8 gate (it will be anyway).
- Demo unit 2f5f7c: old firmware, NEVER enumerated on USB today (suspect
  charge-only cable or no power; its panel state unconfirmed). Pending:
  reflash to b8 (Justin), D11 HA discovery (HA has ONE wled entry, "The
  Belle Permanent Lights" at 192.168.20.30, setup_retry; M-1 never added),
  D12 dump-restore drill (dump exists: baseline/live/m1_factory_16mb.bin).
- Desk deliverables DONE: apollo/UPSTREAM_PRS_READY.md (verified),
  apollo/RELEASE_DRAFT.md (publish approved once b8 gated),
  installer patch applied + pushed (24b94ee), captive tester reply in this
  file, OnePlus 9-ish on b7 confirmed as the vendor-probe popup case.
- NEXT SESSION: 1) Justin picks card A/B; 2) build final setup.gif +
  presets.json (variants staged: presets_optA/optB pattern in scratchpad is
  reproducible from apollo/bench/gen_setup_card.py + this file); 3) rebuild
  artifacts = bundle b8; 4) virgin-boot gate + full D13 AP walkthrough
  (capture the freeze-thaw raw evidence this time); 5) sha256 + versioned
  filenames to Downloads; 6) publish GitHub release m1-b8 (approved);
  7) demo unit: D12 restore drill, flash b8, provision, D11 HA click-
  through; 8) remaining QA: D3 FS-reset button, D5 current, D6 ghosting,
  D7 driver id; 9) open the three upstream PRs (human, texts ready).

## Day 2 (2026-07-16): D24 CLOSED on glass, bundle b8 built (UNGATED)
- Morning retest: the round-3 dim-text card scanned RELIABLY (conditions
  matter; yesterday's "intermittent" was the same asset). Justin picked
  the QR card path.
- BREAKTHROUGH, prediction refuted by test: a 21x21px QR at ONE LED PER
  MODULE (inverted, ECC Q, 4-module quiet zones, bri 220) scans RELIABLY
  on glass. The 2px-minimum assumption was wrong; the huge quiet zone and
  reduced lit area beat module size. This freed the layout for full copy.
- Card iterations on glass: B4 (one-line top), B5 (thin spaces), B6 (1px
  QR + STEP wording), B7 (hotspot copy, small address), B8 (QR moved BELOW
  the steps, order-of-operations), B9 (STEP 2 / SCAN QR BELOW / OR GO TO
  4.3.2.1) = APPROVED SHIP CARD ("Looks great"). All in
  apollo/bench/gen_setup_card.py; scan-verified at each geometry change.
- Factory FS finalized: presets 1-4 unchanged, 5 = Setup card (bri 220),
  9 = First Boot playlist (dog once 4s -> holds 5). setup1-3.gif and
  qr.gif removed, setup.gif = cardB9. Pre-flight workflow verdict on the
  presets file: CLEAN, every behavior source-proven (playlist.cpp repeat
  and end paths, Image effect filename convention, bri handoff 128->220).
- Stale-doc fixes shipped: wiki no-wifi page rewritten for the card,
  apollo/README.md factory-FS description corrected, QA D13 wording, D24
  flipped to ANSWERED (HOTSPOT wording kept by Justin over tester
  feedback, flagged and accepted).
- BUNDLE b8 BUILT, NOT GATED YET: M-1_full_install.bin sha256
  0b92d55af50bca103a4aaa9d3afd4e2b54041d60cd0f09fe24cec211dc8733a3
  (b7 app byte-identical + new FS; M-1_ota.bin unchanged from b7
  6853ce51...). Artifacts in apollo/out/ ONLY; deliberately NOT copied to
  Downloads until the gates pass, so ungated bins cannot be distributed
  by accident. OTA note: existing units will NOT receive the new card via
  OTA (filesystem only ships in the full install).

## NEXT SESSION, first actions (everything staged)
1. Virgin-boot gate: full erase + flash apollo/out/M-1_full_install.bin
   on the test unit (2f5e50, on USB); watch dog 4s -> cardB9 hold.
2. D13 AP walkthrough with Justin's phone (checklist in QA_CHECKLIST.md,
   now includes the freeze-thaw raw evidence capture rows).
3. On PASS: bundle b8 versioned filenames + sha256 to ~/Downloads, update
   QA_CHECKLIST results, then publish GitHub release m1-b8 (Justin
   pre-approved post-gate publish; commands in apollo/RELEASE_DRAFT.md,
   fill real sha256, target the b8 commit).
4. Then: demo unit 2f5f7c (never enumerated on USB; check cable/power),
   D12 restore drill + flash b8 + provision + D11 HA discovery.
5. Remaining QA: D3 FS-reset button, D5 current draw, D6 ghosting, D7
   driver id. Tester thread replies ready in this file. Upstream PRs
   ready in apollo/UPSTREAM_PRS_READY.md (humans open).

## Unit roster correction + AR report resolution (2026-07-16 evening)
- Justin: AR effects "not working" on the gate unit. RESOLVED, not a bug:
  unit 2f5e50 is a REV 6 UPDATED BOARD WITH NO MICROPHONE ADDON FITTED
  (Justin, visual check). AR idles flat without audio input by design;
  audio code untouched b7->b8; Sound Bars reactivity remains glass-proven
  on the mic-equipped unit (2026-07-15). Rev4/no-mic customer experience
  note: factory preset 3 shows idle bars until a mic is fitted (D17
  flagged-and-accepted; mic-addon wiki page covers it; FAQ line suggested).
- D9 no-mic half: this unit has run force-enabled AR through the entire
  b8 gate with zero crashes and normal panel behavior; formal CPU/heap
  A/B (AR on vs off) deferred until after the walkthrough to preserve the
  factory-fresh gate state. Rev6-sans-addon stands in for the no-mic
  condition (rev4 board still ideal for exactness).
- Unit roster: 6d0a40 test #1 (mic-equipped, ran the b7 tour),
  2f5f7c demo (mic-equipped, USB enumeration mystery unresolved),
  2f5e50 test #2 (rev6 updated, NO mic addon, current gate unit).

## 2x2 grid session (2026-07-16 late): mapping PROVEN, arrangement vindicated
Justin stacked four panels 2x2 (128x128) per a rearrangement diagram from an
earlier planning session; panel showed top half only, banded. Software side
AUDITED CLEAN over LAN (bus [64,64,4,2,2] type 65, one 128x128 2D panel,
no ledmap, 27fps, healthy heap). Quadrant color test painted the canvas;
glass showed canvas-TL red on the TL panel and canvas-TR green on the TR
panel (both BANDED), bottom row fully dark.
Rebuilt the lost D10 virtual-mapping simulator from the vendored library
source and COMMITTED it (apollo/bench/virtual_sim.py). Proven mapping for
CHAIN_TOP_RIGHT_DOWN as configured by bus_manager (rows=2, cols=2):
  chain 1 (first from controller) = canvas BOTTOM-RIGHT, rotated 180
  chain 2 = canvas BOTTOM-LEFT, rotated 180
  chain 3 = canvas TOP-LEFT, upright
  chain 4 = canvas TOP-RIGHT, upright
This matches the wiki recipe AND Justin's diagram given his cabling
(controller enters at the YELLOW panel). The observed correct content on
chain 3/4 CONFIRMS the arrangement is right; the assistant's earlier
"inverse arrangement" call assumed controller-at-green and was WRONG.
VERDICT: chain panels 1-2 are dark while demonstrably passing data, and
the lit pair shows banding = POWER STARVATION signature (bottom row LED
supply loose/insufficient; whole-rig-on-USB suspected). Wiki rule stands:
four panels need a real 5V supply (12A+ for bright content), never USB.
Justin is swapping cables/power. Verification: the four-color quadrant
test is left running; success = solid red TL, green TR, blue BL, amber BR,
no bands.
LIB WART (log for upstream findings): legacy getCoords odd-row branch has
an off-by-one (DMA x 1..128 instead of 0..127): bottom row shifts one
column and its first column lands on the next panel; 16320/16384 unique
cells in sim. Cosmetic 1px seam; check on glass once powered; candidate
for the findings ledger if visible.

## 2x2 rig resolution (2026-07-17): OUT-header trap + ghosting data point
- ROOT CAUSE of the dark bottom row: the rotated bottom-right panel had its
  ribbon plugged into the OUT header (180-degree rotation swaps the header
  positions). The chain died there; the impossible-looking content on the
  earlier photos (top-row quadrants "correct" under controller-at-green) is
  explained by the backwards-connected panel feeding signals into output
  buffers: garbage topology, not a mapper bug. With the ribbon moved to IN,
  ALL FOUR panels display correctly: the shipped VirtualMatrixPanel mapping
  (sim: chain 1 = canvas bottom-right rotated 180, 2 = bottom-left rotated,
  3 = top-left upright, 4 = top-right upright) is CONFIRMED WORKING on
  glass with controller at GREEN top-right... which per the sim means the
  physically displayed arrangement matches the recipe serpentine. Wiki
  multiple-panels page gained the IN/OUT troubleshooting bullet (first-line
  diagnostic) and a chain-ghosting note.
- GHOSTING (D6 first data point): faint red scan-boundary line at the row
  seam + red fringes on bright edges, bri >= 100, gone on black. Classic
  parasitic ghosting, amplified by 4-panel address-line loading. QA D6
  updated; single-panel product unaffected in all sessions to date.
  Mitigation options recorded (brightness cap now, MAX_BRIGHTNESS=239
  build later if desired: full gates).
- Bench technique gold: the corner-probe + auto-reapply watcher pattern
  (probe_reapply.sh in scratchpad; pattern documented here): paint low-power
  diagnostics that survive the operator's power cycles via a LAN watcher.
- Library off-by-one (odd-row getCoords, DMA x 1..128) remains UNVERIFIED
  on glass: look for a 1px bottom-row shift / stale first column of chain
  panel 1 during future chain work. virtual_sim.py committed.

## 2x2 seam-line hunt part 2 + mapping closure (2026-07-17 evening)
- Corner probe (post OUT/IN fix) finally verified: ALL FOUR quadrants correct
  (red TL, green TR, blue BL, white BR, outer corners). Justin's arrangement
  (controller into TOP-RIGHT, top row upright, bottom row rotated 180) is
  THE correct recipe for the shipped mapper. TWO doc corrections landed:
  (1) the wiki 2x2 serpentine was INVERTED (said controller bottom-right);
  fixed with a glass-verified note. (2) virtual_sim.py chain numbering was
  backwards (first panel from controller = HIGHEST DMA columns, end of the
  shift chain); corrected, sim now matches glass exactly.
- Driver IC identified (D7 partial): ICN2037BP on Justin's 2x2 batch.
  Support colleague's 2x2 shows NO seam line on identical firmware =
  panel-batch variance. His chip marking still wanted for the sourcing table.
- Seam line elimination trail: brightness-independent (visible at bri 40),
  load-independent (thin band at quarter current shows it), latch_blanking=3
  no effect (guarded hook added to bus_manager, inert without build flag),
  clock PHASE no effect (and wrong phase adds a distinctive one-column
  vertical edge artifact: reverted; that artifact documented for the fault
  decoder). Line requires BOTH seam-adjacent rows lit (= both panels' last
  scan address carrying data). Remaining lever: I2S clock speed (ICN2037
  documented sensitivity). Status: PARKED pending Justin's call; cosmetic,
  batch-specific, single-panel product unaffected.
- FIRMWARE QUIRK FOUND (upstream findings candidate): the HUB75 "Reversed"
  (clkphase) checkbox does NOT persist through LED-settings save or JSON
  cfg POST: BusHub75Matrix consumes bc.reversed for mxconfig.clkphase but
  never stores it in the Bus base (ctor passes only type/start/autoWhite),
  so every save re-serializes rev=false from the live bus. Workaround that
  works: edit cfg.json on the FS via /upload + reboot. Also: /json/cfg
  LIVE view reports rev=false even when the file (and active clkphase) is
  true: cosmetic but misleading.
- Fault decoder additions earned on glass: single bright vertical edge
  column = wrong clkphase; rotated panel dark with downstream panels dead =
  ribbon in OUT header.
