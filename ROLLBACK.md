# Rollback to WLED-MM (last known good)

The complete WLED-MM shipping lineage is archived in git in the WLED-MM-M1 repository
(https://github.com/ApolloAutomation/WLED-MM-M1, branch mdev, docs/ directory) and
served from its GitHub Pages. Nothing in this migration deletes or rewrites it.

## Archived binaries (docs/ in WLED-MM-M1)
| Build | File | Version | Notes |
|---|---|---|---|
| Merged factory image | docs/merged-firmware.bin | 25.7.14.1 | flash at 0x0 after erase |
| Rev4 app | docs/14.5.1/Apollo_M-1_Firmware_14.5.1.bin | 25.8.19.1 | flash at 0x0 (merged) |
| Rev6 app (last shipping) | docs/Rev6_14.5.1/Apollo_M-1_Rev6_14.5.1.bin | 25.10.9.1 | flash at 0x0 (merged) |
| Loose parts | docs/bootloader.bin, docs/partitions.bin, docs/firmware.bin | | for manual flashing |

Live ESP Web Tools pages (unchanged by this migration):
- https://apolloautomation.github.io/WLED-MM-M1/ (root, 25.7.14.1)
- https://apolloautomation.github.io/WLED-MM-M1/14.5.1/ manifest (Rev4)
- https://apolloautomation.github.io/WLED-MM-M1/Rev6_14.5.1/ manifest (Rev6)

## Rolling a single unit back
Serial (always works):
1. esptool --chip esp32s3 erase_flash
2. esptool --chip esp32s3 write_flash 0x0 Apollo_M-1_Rev6_14.5.1.bin
3. Reconfigure per the old wiki settings page (the MM build needs the manual steps).

OTA (from a 16.0.1 unit): both firmwares use the same partition table, so uploading
the OLD app is mechanically possible via Manual OTA, BUT the 16.0.1 cfg.json on the
filesystem uses 16.x bus type 65, which WLED-MM does not understand. After an OTA
downgrade, expect to redo the LED and 2D settings (or do the full serial rollback,
which starts clean). Verify this path once in QA before relying on it.

## Rolling the fleet back
The installer entry for the M-1 (ApolloAutomation/installer, branch feat/m1-wled-entry)
still points at the WLED-MM manifests until the 16.0.1 hosting is switched on, so
"rollback" for new customers is: do not flip the installer URLs. For shipped 16.0.1
units, publish the archived MM manifest as the install target again.
