# Draft replacement: /products/m1/setup/m1-matrix-settings/

Editor note (not part of the page): with firmware 16.0.1 every configuration step on
the old page is a factory default. The wiki triage classified 11 of its 13 steps
FIXED AS DEFAULT; the remaining two are the flash itself and the rev6 microphone
toggle, which live on their own pages. Suggested disposition: replace the page body
with the text below, or delete the page and fold the table into the flashing guide.

---

## M-1 firmware settings reference

Your M-1 arrives fully configured. After you connect it to WiFi using the getting
started guide, the full 64x64 panel works with no settings changes.

This page is a reference for two situations:

1. A unit running firmware older than 16.0.1 was factory reset and now shows a small
   square in one corner of the panel.
2. You want to verify that a unit is configured correctly.

### If the display is wrong

Reflash the current firmware from the installer and choose the full install option.
It restores every factory setting, including the display size. You will need to
enter your WiFi details again; nothing else needs configuration.

On firmware 16.0.1 and later a factory reset (holding the button for ten seconds)
also returns to correct display settings on its own. The reflash is only required
for units still running the earlier WLED-MM firmware.

### Factory values

Open the WLED interface and check under Config to confirm a unit is healthy:

| Setting | Factory value |
|---|---|
| Server description (Config, User Interface) | Apollo M-1 |
| mDNS address (Config, WiFi Setup) | apollo-led-matrix-xxxxxx (unique per unit) |
| LED type (Config, LED Preferences) | HUB75 (Half Scan) |
| Panel size and chain | 64 x 64, chain length 1 |
| Automatic brightness limiter | Off |
| 2D configuration | 2D Matrix, one 64x64 panel |
| AudioReactive type (Config, Usermods) | Generic I2S |
| AudioReactive pins | SD 10, WS 12, SCK 11 |
| AudioReactive sync mode | Off |

Setup hotspot: each unit broadcasts an open network named "Apollo M-1-xxxxxx" (the
same six characters as its network name) until it joins your WiFi. Join it and the
setup page is at http://4.3.2.1.

If you own several units: names are unique per device, so multiple M-1 units coexist
on one network without conflicts.

The AudioReactive values only matter on rev6 boards with the microphone addon.
Installing the addon needs exactly one settings change (the Enabled checkbox); the
type and pins above are already set. See the microphone addon page.

### Chaining panels

Chained panels remain a manual setup because the firmware cannot detect how many
panels you attached. See the multiple panels guide; in short, set chain length and
the panel grid under Config, LED Preferences, and match the layout under Config,
2D Configuration.

### A note on firmware versions

Units shipped with firmware 16.0.1 or later run standard WLED. Units on the earlier
WLED-MM firmware keep working and keep their settings when updated over the air; the
update page in the WLED interface accepts the current M-1 firmware file directly.
