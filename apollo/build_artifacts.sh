#!/usr/bin/env bash
# Build the two Apollo M-1 release artifacts from the apollo_m1 environment:
#   out/M-1_full_install.bin  - merged image for offset 0x0 after a full erase
#                               (bootloader + partition table + otadata + app +
#                                LittleFS with factory cfg.json/presets.json)
#   out/M-1_ota.bin           - app only, for the WLED OTA update page; does not
#                               touch the filesystem
#
# Usage: apollo/build_artifacts.sh [--skip-pio]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_NAME=apollo_m1
BUILD="$ROOT/.pio/build/$ENV_NAME"
OUT="$ROOT/apollo/out"

# Partition layout from tools/WLED_ESP32_16MB_9MB_FS.csv (esp32.extreme_partitions).
# These values are identical on units factory-flashed with WLED-MM.
OTADATA_OFF=0xe000
APP0_OFF=0x10000
APP_SLOT_SIZE=$((0x300000))
FS_OFF=0x610000
FS_SIZE=$((0x9E0000))

MKLITTLEFS="$HOME/.platformio/packages/tool-mklittlefs/mklittlefs"
BOOT_APP0="$(ls "$HOME"/.platformio/packages/framework-arduinoespressif32*/tools/partitions/boot_app0.bin 2>/dev/null | head -1)"
ESPTOOL="esptool.py"
command -v "$ESPTOOL" >/dev/null || ESPTOOL="python3 -m esptool"

[ -x "$MKLITTLEFS" ] || { echo "mklittlefs not found at $MKLITTLEFS"; exit 1; }
[ -n "$BOOT_APP0" ] || { echo "boot_app0.bin not found in PlatformIO packages"; exit 1; }

if [ "${1:-}" != "--skip-pio" ]; then
  (cd "$ROOT" && pio run -e "$ENV_NAME")
fi

for f in bootloader.bin partitions.bin firmware.bin; do
  [ -f "$BUILD/$f" ] || { echo "missing $BUILD/$f - build the $ENV_NAME env first"; exit 1; }
done

APP_SIZE=$(stat -f%z "$BUILD/firmware.bin" 2>/dev/null || stat -c%s "$BUILD/firmware.bin")
if [ "$APP_SIZE" -gt "$APP_SLOT_SIZE" ]; then
  echo "firmware.bin ($APP_SIZE bytes) exceeds the $APP_SLOT_SIZE byte OTA slot"; exit 1
fi

mkdir -p "$OUT"

echo "== LittleFS image from apollo/fs (offset $FS_OFF, size $FS_SIZE)"
"$MKLITTLEFS" -c "$ROOT/apollo/fs" -b 4096 -p 256 -s "$FS_SIZE" "$OUT/littlefs.bin" >/dev/null

echo "== M-1_full_install.bin (merged at 0x0, ESP32-S3)"
$ESPTOOL --chip esp32s3 merge_bin -o "$OUT/M-1_full_install.bin" \
  --flash_mode keep --flash_freq keep --flash_size 16MB \
  0x0 "$BUILD/bootloader.bin" \
  0x8000 "$BUILD/partitions.bin" \
  "$OTADATA_OFF" "$BOOT_APP0" \
  "$APP0_OFF" "$BUILD/firmware.bin" \
  "$FS_OFF" "$OUT/littlefs.bin"

echo "== M-1_ota.bin (app only)"
cp "$BUILD/firmware.bin" "$OUT/M-1_ota.bin"

echo
echo "Artifacts in $OUT:"
ls -l "$OUT/M-1_full_install.bin" "$OUT/M-1_ota.bin"
echo
echo "App size: $APP_SIZE / $APP_SLOT_SIZE bytes ($((APP_SIZE * 100 / APP_SLOT_SIZE))% of OTA slot)"
