# Draft replacement: /products/m1/addons/adding-microphone-to-m-1/

Editor note (not part of the page): on firmware 16.0.1 the microphone type, all
three pins, and the sync mode are factory defaults. The old page's five settings
steps reduce to one checkbox. Keep the physical installation photos and steps as
they are; only the software section below changes.

---

## Adding the microphone to your M-1

The microphone addon fits rev6 and newer boards. Rev4 boards do not have the
microphone connector; if you are unsure which board you have, the revision is
printed on the controller PCB.

### Install the hardware

(keep the existing physical installation steps and photos)

### Use it

There is no software setup. Sound reactivity is on by default with the microphone
type (Generic I2S), the pins (SD 10, WS 12, SCK 11), and the sync mode (Off) all
configured at the factory on firmware 16.0.1 and later.

Pick any effect marked with the musical note symbol in the effect list and make
some noise.

### If sound effects do not react

- Check that Enabled was not turned off under Config, Usermods, AudioReactive
  (it is on from the factory).
- Confirm the microphone board is seated fully in its connector.
- Units running firmware older than 16.0.1: set Type to Generic I2S and the pins to
  SD 10, WS 12, SCK 11 manually, or update the firmware first (settings survive the
  update).
