# Bench tooling (from the D10 + AP sessions)

- serial_logger.py: S3 USB-Serial-JTAG logger. A plain OS open() can assert
  DTR+RTS together and drop the chip into DOWNLOAD mode; this logger
  neutralizes the lines, pulses a clean normal-boot reset, then raises DTR
  (HWCDC output needs it). Production builds print ROM/panic text only;
  app-level logs need the apollo_m1_dbg env (platformio_override.ini,
  gitignored - see BENCH_SESSION_D10.md for its contents).
- ap_probe_template.sh: one-shot "Mac joins the M-1 hotspot, probes, and
  auto-rejoins home WiFi" pattern. Everything inside ONE script because the
  Mac has no internet while on the AP. Edit SSIDs at the top.
- ALWAYS kill the logger before esptool (port contention reads as "serial
  noise or corruption" / "chip stopped responding").
- 16MB flash READS over this port need 16x1MB chunks; writes are fine whole.
