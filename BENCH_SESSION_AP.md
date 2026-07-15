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
