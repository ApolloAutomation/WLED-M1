#!/usr/bin/env python3
"""Bench serial logger v2 for ESP32-S3 USB-Serial-JTAG.
The plain OS open() can momentarily assert DTR+RTS together, which the S3
interprets as the bootloader-entry sequence and parks the chip in download
mode. This logger neutralizes the lines, issues a clean normal-boot reset
(RTS pulse with DTR low = EN cycle with BOOT high), then raises DTR for
HWCDC streaming. Every (re)open therefore yields a fresh full boot log."""
import serial, time

PORT = "/dev/cu.usbmodem1101"
LOG = "/private/tmp/claude-501/-Users-justinapollo-Code-ApolloAutomation/17143c94-ba61-41a1-a8cd-011bd2e2cf7b/scratchpad/serial_ap_session.log"

while True:
    try:
        with serial.Serial(PORT, 115200, timeout=1) as ser:
            ser.dtr = False
            ser.rts = False
            time.sleep(0.1)
            ser.rts = True          # EN low: hold in reset
            time.sleep(0.15)
            ser.rts = False         # EN high, BOOT high (DTR low) -> normal SPI boot
            time.sleep(0.3)
            ser.dtr = True          # assert DTR so HWCDC app output flows
            with open(LOG, "ab", buffering=0) as f:
                f.write(b"\n--- port opened + clean reset ---\n")
                while True:
                    d = ser.read(4096)
                    if d:
                        f.write(d)
    except (serial.SerialException, OSError) as e:
        with open(LOG, "ab", buffering=0) as f:
            f.write(("\n--- port gone (%s), retrying ---\n" % e).encode())
        time.sleep(2)
