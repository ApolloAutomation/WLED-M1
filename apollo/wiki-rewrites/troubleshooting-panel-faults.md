# Draft new page: /products/m1/troubleshooting/m1-panel-faults/

Editor note (not part of the page): this is the panel fault decoder from the
engineering notes, adapted for customers. Link it from the FAQ and from the reflash
page. It replaces guesswork with a symptom table.

---

## Panel troubleshooting guide

Match what you see on the panel to a row below. Work from top to bottom; the first
match is usually the cause.

| What you see | Likely cause | What to do |
|---|---|---|
| Only one quarter of the panel lights, rest dark | Panel size set to 32x32 instead of 64x64 | On firmware 16.0.1+, hold the button ten seconds (factory reset), or full-reflash from the installer. On older firmware, follow the settings reference page |
| Panel completely dark, power LED on | No LED output configured, or a failed update | Full reflash from the installer restores factory settings |
| Whole panel dim or nearly black | Brightness set very low, or the brightness limiter was turned on manually | Raise brightness in the main UI; check Config, LED Preferences, brightness limiter is off (factory default) |
| Image repeated or stretched sideways | Chain length set higher than the number of panels | Config, LED Preferences, set chain length to match your panel count (1 for a single panel) |
| Interleaved horizontal bands or a doubled image | LED type changed to the Quarter Scan variant | Config, LED Preferences, LED type must be HUB75 (Half Scan) for the M-1 panel |
| Colors washed out or pastel, or panel dark with power confirmed | Wrong shift register driver selected | Leave the driver at its default; if you changed advanced HUB75 options, factory reset |
| Colors bleed sideways, vertical tearing | Clock phase toggled | Config, LED Preferences, uncheck Inverted clock phase (the Reversed checkbox) |
| Ghosting or faint smearing at high brightness | Panel driven at maximum brightness | Lower brightness slightly; this is a known panel characteristic at 100 percent |
| Panel went black right after changing LED settings | The controller needs a restart to apply HUB75 changes | Power cycle the M-1 or use the reboot button in Config |
| Vertical lines or column artifacts | Controller not seated fully on the panel connector | Power off, re-seat the controller on the back of the matrix, power on |

If none of these match, run the full install from the installer (it restores every
factory setting; you re-enter WiFi only), and if the symptom survives a full
reinstall, contact support with a photo of the panel.
