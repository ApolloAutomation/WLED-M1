# WLED Android app: broken file chooser (KNOWN upstream bug)

Upstream issue: https://github.com/Moustachauve/WLED-Android/issues/141
("Cannot Choose file", open since 2026-03-23, reported on Samsung Fold 5 and
Pixel 7, stalled after a maintainer question).

Justin: paste the comment below on that issue rather than opening a new one.
Our repro adds what the thread is missing: proof the device side is fine, a
third device model, and a second affected feature (PixelForge uploads, not
only firmware updates).

---

Same bug on a Samsung Galaxy Z Fold7, current app version, and it is not
limited to the update page: any device page with a file input is affected.

Repro: WLED 16.0.1 device, open it in the app, tap the built-in PixelForge
button, tap the image upload control. The system picker opens with every
image and GIF greyed out and unselectable. Same result after clearing the
app's cache and data and after a full uninstall and reinstall; the app lists
no permissions to grant.

Counter-proof that the device and page are fine: the same page
(http://device-ip/pixelforge.htm) on the same phone in Firefox opens the
picker normally and the upload works. The input is a plain
input type="file" accept="image/*", so this looks like the app's WebView
onShowFileChooser wiring or the MIME filter it passes to the picker intent.

Happy to test a build; this blocks image upload and firmware update for
Android users of any WLED device.

---

Documented workaround everywhere on our side (wiki, tester README): on
phones, use a mobile browser at http://device-ip/pixelforge.htm.

## UPDATE 2026-07-15: root cause confirmed at app source level

Repo Moustachauve/WLED-Android (current official app), release v7.0.1.
DeviceWebview.kt onShowFileChooser() discards the page's accept types:
getMimeType() maps only the literal strings ".json" and ".css"; everything
else (image/*, .gif, .bin) falls through to "application/octet-stream",
which FileUploadContract passes as the ACTION_GET_CONTENT type - so the
Android documents picker greys out every image. Affects every WLED device
and every file input in the app (PixelForge uploads AND manual OTA .bin
updates). The commented-out line above the mapping shows accept
passthrough was once intended. Suggested fix for the issue thread: use
fileChooserParams.createIntent(), or type="*/*" plus EXTRA_MIME_TYPES
derived from acceptTypes (~5 lines). Tracked as open issue #141
(https://github.com/Moustachauve/WLED-Android/issues/141), stalled since
2026-03-23 after a maintainer question. Verified no device-side
workaround exists: the picker never consults the server.
Customer guidance: use any mobile/desktop browser (PixelForge works there,
including over the M-1's own hotspot).
