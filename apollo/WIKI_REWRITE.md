# Draft rewrite: wiki page "M-1 LED Matrix WLED Configuration Settings"

Context for the wiki editor: with firmware 16.0.1 and later, every value this page
used to walk customers through is baked into the firmware. A factory-fresh or
factory-reset M-1 boots as a 64x64 matrix with the correct audio settings and needs
none of these steps. The page should shrink to a short reference inside the flashing
guide, or redirect there. Draft below. Style: no first-boot promises we have not QA
tested; keep the reassuring, matter-of-fact tone.

---

## M-1 firmware settings reference

Your M-1 arrives with all display settings preconfigured. After you connect it to
WiFi (see the setup guide), the full 64x64 panel works out of the box. You do not
need to change any WLED settings for normal use.

This page exists for two situations only:

1. You performed a factory reset from an older firmware (before 16.0.1) and the
   display shows a small square in one corner.
2. You want to verify a unit is configured correctly.

### The fix for almost everything

Reflash the current firmware from install.apolloautomation.com and choose the full
install option. It restores every factory setting, including the display size. Your
WiFi details are the only thing you will need to enter again.

If you are on firmware 16.0.1 or later, a factory reset (holding the button for ten
seconds) also returns the unit to correct factory settings on its own. The reflash
path above is only required for units still running the older WLED-MM firmware.

### Factory values (for verification)

Open the WLED interface and check Config if you want to confirm a unit is healthy:

| Setting | Factory value |
|---|---|
| Server description (Config, User Interface) | Apollo LED Matrix |
| mDNS address (Config, WiFi Setup) | apollo-led-matrix-xxxxxx (unique per unit) |
| LED type (Config, LED Preferences) | HUB75 (Half Scan), panel 64 x 64, chain 1 |
| Automatic brightness limiter | Off |
| 2D configuration | 2D Matrix, one 64x64 panel |
| AudioReactive type (Config, Usermods) | Generic I2S |
| AudioReactive pins | SD 10, WS 12, SCK 11 |
| AudioReactive sync mode | Off |

Notes for owners of several units: each M-1 uses a unique network name
(apollo-led-matrix followed by six characters from its hardware address), so multiple
units coexist on one network without conflicts. The setup hotspot name is unique per
unit the same way (Apollo M-1 followed by the same six characters).

The microphone settings only take effect on rev6 boards with the microphone addon.
Enable AudioReactive under Config, Usermods when you install the addon; the pins are
already correct.

### Chaining panels

To run up to four chained 64x64 panels, set the chain length and grid in Config, LED
Preferences (chain 4, grid 1 row x 4 columns gives 256x64) and match the layout under
Config, 2D Configuration. Chaining remains a manual step because the firmware cannot
detect how many panels you attached.

---

End of draft. Suggested disposition: replace the current page body with the above, or
delete the page and fold the "Factory values" table into the flashing guide as a
collapsible section. Every step-by-step instruction in the old page (set LED type,
uncheck limiter, set 2D size, enter audio pins) is obsolete on 16.0.1 firmware.
