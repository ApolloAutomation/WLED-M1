# Bug report draft: WLED Android app file picker greys out all images

For Trevor to file against the WLED Android app project (do not file from
automation). Verified 2026-07-12 on a Samsung Galaxy Z Fold7.

## Summary
Inside the WLED Android app, opening a device page that uses a standard HTML
file input (input type="file" accept="image/*") shows the system file picker
with every image and GIF greyed out and unselectable. The same page, same
device, same phone works correctly in Firefox for Android (and in desktop
browsers), so the page and firmware are fine; the app's WebView file-chooser
wiring (WebChromeClient.onShowFileChooser or the intent MIME filter it builds)
appears to be at fault.

## Reproduce
1. WLED device running 16.0.1 with the built-in PixelForge page (/pixelforge.htm).
2. Open the device in the WLED Android app, tap the PixelForge button, tap the
   image upload control.
3. The picker opens with all images/GIFs greyed out.
4. Repeat in Firefox for Android at http://device-ip/pixelforge.htm: files are
   selectable and upload works.

## Impact
Any device page with file upload is unusable from the app (image tools, GIF
upload, filesystem /edit uploads). Users conclude the device is broken.

## Workaround
Use a mobile browser at http://device-ip/pixelforge.htm.
