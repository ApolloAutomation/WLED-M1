# BENCH SESSION: AP-mode first-run investigation (2026-07-14, live, Justin at bench)

Resume file for this session. Prior context: BENCH_SESSION_D10.md, SUMMARY.md.
Test unit: NEW physical unit (MAC suffix 6d0a40; demo unit was 2f5f7c), USB
/dev/cu.usbmodem1101, flashed with the exact shipping artifact this session.
Justin's report + binding D20 (AP = first-class destination) in the session brief.

## Established so far (evidence in baseline/ap-firstrun/)
1. FACT 1 restated and unchanged (half-scan, type 65).
2. Clean boot log captured (ROM banner, SPI_FAST_FLASH_BOOT, no crash loop;
   production build is console-silent by design).
3. Virgin flash reproduced: AP appears as "Apollo M-1-6d0a40" ~45-60s after
   power-on (STA timeout first). Wiki note: tell customers to wait a minute.
4. MAC-JOINED THE AP AND ENUMERATED ROUTES (route_battery.txt): EVERYTHING
   SERVES. / (UI shell) 200, /json/info|state|cfg 200, /presets.json 200,
   /cfg.json 200, /pixelforge.htm 200, /pixelpaint.htm 200, /edit 200,
   HTTP API /win 200, 404s normal, captive redirect for foreign Host = 302.
   GIF UPLOAD over AP: POST /upload 200 + readback 200 (7378B intact).
5. DHCP packet captured (battery2.txt): router 4.3.2.1, DNS 4.3.2.1,
   mask/lease correct. Device-side network config is CLEAN.
6. Therefore the working hypothesis (to be confirmed on the phone with the
   serial log): Justin's "basic control worked" was Android's CAPTIVE
   MINI-BROWSER (crippled: no file chooser, no real nav); Chrome/Firefox
   failing on http://4.3.2.1 is Android routing browser traffic via MOBILE
   DATA because the AP has no internet. Predicted fix: mobile data OFF (or
   "stay connected" + real browser) -> full UI works over AP.

## Next steps
- Flash dbg app-only (FS preserved) for request-level serial visibility.
- Batch phone tests with Justin (mobile data on/off matrix, captive window
  vs real browser, full customer script over AP).
- Then: scrolling-text fits fix, presets normalization, app-upload item.
- Desk analysis workflow wf_56e91209-04d running (AP server source, scroll
  text design, presets audit, Android app research).

## VERDICTS (all reproduced with evidence; fixes applied + verified over AP)
| Symptom | Verdict | Root cause | Fix location |
|---|---|---|---|
| 4.3.2.1 unreachable in Chrome/Firefox | REPRODUCED (Justin #2), NOT device-side | Android keeps cellular as default net for a no-internet AP; 4.3.2.1 is a real Level3 internet IP; captive mini-browser binds to WiFi (hence "basic control worked") | Wiki: mobile data OFF (Justin #4 "Works!") |
| Pixel Paint dead over AP | REPRODUCED (Justin #8/#9) - DEVICE-SIDE BUG | shipped pixelpaint.htm.gz loaded iro.js+omggif.js from cdn.jsdelivr.net; no internet on AP = tool never initializes (works on WiFi = CDN reachable). Violates nothing-leaves-home on its own | FS: rewrote to on-device /iro.js + /omggif.js (identical iro 5.5.2); verified 200 over AP, 0 CDN refs |
| PixelForge/GIF upload over AP | NOT REPRODUCED as device bug: works (Mac battery; Justin #7 in real browser, data off) | original failure was the captive mini-browser (no file chooser) + cellular routing | Wiki (real browser + data off); captive-window limitation documented |
| Weak/laggy AP | CONFIRMED device-side (source) | LOLIN_WIFI_FIX caps S3 TX at 8.5dBm; initAP never disables modem sleep on factory-fresh units | FS: cfg wifi.txpwr=78 (19.5dBm); FW: +1 line initAP setSleep. Post-fix: 0% loss, ~5ms avg |
| Scrolling text static when fits | REPRODUCED (Justin #6) + arithmetic (APOLLO M-1 = 56px on 64px) | upstream design: horizontal scroll only when totalTextWidth > cols; check3 dead when fits | FW: 2 lines - check3 forces scroll; preset 1 ships o3=true. Upstream PR candidate |
| "Dog gif creates its own segment" | ROOT-CAUSED, not a segment | segment NAME persistence: dog preset names seg0 "apollo_dog.gif" (Image filename); manual effect switch keeps the name -> Scrolling Text scrolls the filename; UI titles segment by name | FS: presets normalized (explicit n everywhere); residual preset->manual trap documented; UI-level fix noted as upstream candidate |
| Sound Bars preset (found by audit) | LATENT DEFECT | saved c1=0 -> GEQ renders ONE bar, not 16 | FS: c1=255,c2=64,c3=0 |
| GIF via WLED Android app | CONFIRMED CLIENT-SIDE at app source level | DeviceWebview.kt getMimeType() discards accept types -> picker filtered to application/octet-stream -> all images greyed; ships in v7.0.1; issue #141 open | apollo/WLED_APP_BUG.md upgraded; wiki: use any browser |
Post-fix virgin gate: erase + flash final artifact, AP up, 0 panics, all routes
200 over AP incl. offline pixelpaint chain, JSON POSTs 200 (Content-Type
header required - earlier 400s were the probe's own missing header).
Firmware surface: +171/-16 vs base (was +168/-14): wled.cpp +1, FX.cpp 2 lines.
REMAINING: Justin's final phone walkthrough on the fixed artifact; docs (QA
gate, D20/D21, SUMMARY correction, wiki no-wifi page, app bug doc, upstream
PR texts).

## FINAL STATE (2026-07-15, tour approved "thats great")
### First-boot signpost tour (D23) - APPROVED ON GLASS after 10 iterations
Frames (preset 9 playlist, applied at boot only while WiFi unconfigured,
FACTORY_SIGNPOST_PRESET in const.h + conditional in beginStrip):
  dog 4s -> STEP 1 "JOIN / APOLLO M-1 / WIFI / HOTSPOT" 9s
  -> STEP 2 "SCAN / QR CODE" 7s -> inverted QR (HTTP://4.3.2.1, v1 ECC-M,
  3px modules, bri 90) 12s -> "NO CAMERA? / OPEN / BROWSER / GO TO /
  4.3.2.1" 8s. Cards share fixed anchors (header y1, divider y14, body
  y17), amber/sky/white on navy, colorblind-safe. Assets: setup1-3.gif,
  qr.gif, apollo_dog.gif (approved blink/ears/sniff, NO lick - tongue
  experiments failed twice, art has no room).
### Iteration lessons (for future panel-card work)
- Per-card vertical centering makes headers jump between frames: anchor.
- Standard black-on-white QR scans poorly on LED (dot texture): INVERT
  (bright-on-black), 3px modules, bezel as quiet zone, dim to ~90 bri,
  scan from arm's length. ECC M + uppercase-alnum payload.
- Long URLs cannot fit scannable on 64px (72-char wiki URL = v4 = 66px):
  wiki-help QR CUT by Justin; if ever revisited, needs a short redirect
  (wiki.apolloautomation.com/m1 -> v2 25x25).
- Tiny-font Q reads as O; custom glyphs read as icons; the answer was
  plain text and letting people read (Justin's call).
### Still open for the NEXT session (after fresh-flash test)
1. FRESH-FLASH GATE: erase + flash apollo/out/M-1_full_install.bin
   (rebuilt at HEAD) + full AP walkthrough script + Justin's phone.
2. Docs written this session: QA gate, D20-D23, SUMMARY correction,
   wiki no-wifi page, WLED_APP_BUG upgrade, upstream findings 9-10.
3. Upstream PRs prepared not opened: scroll-force (FX.cpp), AP modem
   sleep (wled.cpp), connectivity-probe answers (wled_server.cpp,
   discuss upstream appetite first - it changes captive UX).
4. Business tail unchanged (bundle number, hosting, installer, PR open).

## POST-GATE FINDING (2026-07-15): Pixel Paint freeze-trap, fixed
Justin: after Pixel Paint + clear + backing out, effects show a BLACK
screen until PixelForge plays a gif. Root cause (source + live repro):
per-pixel "i" writes force seg.freeze=true (json.cpp) so effects cannot
repaint the drawing; the UI's effect picker changes fx but never thaws;
frozen segments skip their effect function -> the cleared black canvas
persists. PixelForge worked because imgPlay sends frz:false explicitly.
FIX (json.cpp, +2 lines net): an fx change now clears freeze unless the
same message carries an explicit frz key (parsed earlier, so explicit
frz still wins). Verified live: paint->frz true, clear->frz true,
fx pick->fx applied AND frz false. Upstream PR candidate (findings #12).
ANOMALY LOGGED, unresolved, observed once: the first production boot on
the fresh flash returned odd HTTP codes (413 with success:true bodies,
400s) and dropped some JSON POST effects cross-subnet; a reflash+reboot
cleared it; dbg-build debug dump captured a request in state 100. Watch
for recurrence before chasing.

## Sound Bars glass verification (2026-07-15): "multiple bars corresponding
## to type of sound. it looked great." - the 16-band GEQ preset fix
## (audit finding: shipped c1=0 = one bar) is confirmed on hardware.
## Audio pipeline healthy end-to-end; the earlier "AR not working" report
## is attributed to the frozen-segment trap, fixed same session.
