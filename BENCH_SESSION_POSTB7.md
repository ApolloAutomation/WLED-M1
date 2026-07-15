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
