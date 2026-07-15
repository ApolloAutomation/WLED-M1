# New page: /products/m1/setup/use-without-wifi/

Editor note (not part of the page): written 2026-07-15 from the AP-mode
bench session (BENCH_SESSION_AP.md). Every step verified on hardware with
an Android phone WITH MOBILE DATA ON. Requires firmware with the AP session
fixes (post-D22/D23 build).

---

## Using your M-1 with no WiFi at all

Your M-1 does not need a WiFi network. Out of the box it makes its own,
and the panel itself walks you through connecting - full control, nothing
sent anywhere, no internet involved.

### First power-on

Plug the M-1 in. After about a minute the panel starts a short guide that
repeats: the Apollo dog, STEP 1, STEP 2, a QR code, and a fallback card.

1. **STEP 1 - join the hotspot.** On your phone or computer, open the WiFi
   list and join the network called **Apollo M-1-xxxxxx** (the letters at
   the end are unique to your unit). There is no password. If your phone
   warns "this network has no internet - stay connected?", choose **stay
   connected**. You can leave mobile data on.
2. **STEP 2 - scan the code.** When the QR code appears on the panel, point
   your camera app at it and tap the link. Your browser opens the M-1's
   control page. Tip: scan from about arm's length - it reads better than
   up close.
3. **No camera?** Open any browser and go to **4.3.2.1** - that address
   works whenever you are connected to the M-1's own hotspot.

From the control page you have everything: presets, effects, scrolling
text, Pixel Paint, and GIF upload through PixelForge - all without the M-1
ever touching a network.

### Good to know

- The setup guide on the panel only appears while the M-1 has no WiFi
  configured. Once you connect it to your home WiFi, it boots straight to
  the Apollo dog instead, and you reach it at its normal network address.
- The hotspot stays available as a fallback: if the M-1 ever cannot reach
  your WiFi, it opens its hotspot again and 4.3.2.1 works as above.
- Uploading GIFs from the **WLED phone app** does not work (a known bug in
  the app itself - its file picker greys out images). Use any browser
  instead: scan the QR or go to 4.3.2.1, then open PixelForge.
- While your phone is on the M-1 hotspot, apps that need the internet may
  pause. Your phone returns to normal the moment you leave the network.
