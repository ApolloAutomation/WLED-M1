#!/usr/bin/env bash
# Build the two Apollo M-1 release artifacts from the apollo_m1 environment:
#   out/M-1_full_install.bin  - merged image for offset 0x0 after a full erase
#                               (bootloader + partition table + otadata + app +
#                                LittleFS with factory cfg.json/presets.json)
#   out/M-1_ota.bin           - app only, for the WLED OTA update page; does not
#                               touch the filesystem
# plus what is needed to support the release later: firmware.elf and firmware.map
# (decode crash backtraces), bootloader.bin, partitions.bin, littlefs.bin,
# BUILD_INFO.txt (commit and tool versions) and SHA256SUMS.txt.
#
# Usage: apollo/build_artifacts.sh [--skip-pio] [--littlefs <file>] [--allow-dirty]
#   --skip-pio         package the existing .pio build instead of running pio first
#                      (refused if that build is older than the current commit)
#   --littlefs <file>  use a prebuilt LittleFS image instead of running mklittlefs,
#                      e.g. the previous release's littlefs.bin when apollo/fs is
#                      unchanged (mklittlefs from PlatformIO is x86-only on macOS and
#                      needs Rosetta on Apple silicon)
#   --allow-dirty      allow uncommitted changes to tracked files (never for releases)
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

SKIP_PIO=0
LITTLEFS_IN=""
ALLOW_DIRTY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --skip-pio) SKIP_PIO=1 ;;
    --littlefs) LITTLEFS_IN="${2:?--littlefs needs a file}"; shift ;;
    --allow-dirty) ALLOW_DIRTY=1 ;;
    *) echo "unknown option: $1"; exit 1 ;;
  esac
  shift
done

# Use PlatformIO's own tools (the versions the platform pins), not whatever is on PATH.
PIO_HOME="${PLATFORMIO_CORE_DIR:-$HOME/.platformio}"
PIO_PY="$PIO_HOME/penv/bin/python"
[ -x "$PIO_PY" ] || PIO_PY="python3"
ESPTOOL_PY="$PIO_HOME/packages/tool-esptoolpy/esptool.py"
MKLITTLEFS="$PIO_HOME/packages/tool-mklittlefs/mklittlefs"
BOOT_APP0="$PIO_HOME/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin"

[ -f "$ESPTOOL_PY" ] || { echo "esptool not found at $ESPTOOL_PY - build the $ENV_NAME env once first"; exit 1; }
[ -f "$BOOT_APP0" ] || { echo "boot_app0.bin not found at $BOOT_APP0"; exit 1; }
esptool() { "$PIO_PY" "$ESPTOOL_PY" "$@"; }

if [ "$ALLOW_DIRTY" = 0 ] && [ -n "$(git -C "$ROOT" status --porcelain --untracked-files=no)" ]; then
  echo "tracked files have uncommitted changes; commit them or pass --allow-dirty (not for releases)"; exit 1
fi

if [ "$SKIP_PIO" = 0 ]; then
  (cd "$ROOT" && pio run -e "$ENV_NAME")
fi

for f in bootloader.bin partitions.bin firmware.bin firmware.elf firmware.map; do
  [ -f "$BUILD/$f" ] || { echo "missing $BUILD/$f - build the $ENV_NAME env first"; exit 1; }
done

mtime() { stat -f%m "$1" 2>/dev/null || stat -c%Y "$1"; }
fsize() { stat -f%z "$1" 2>/dev/null || stat -c%s "$1"; }

# A leftover bench build must never be packaged as a release.
if [ "$SKIP_PIO" = 1 ] && [ "$(mtime "$BUILD/firmware.bin")" -lt "$(git -C "$ROOT" log -1 --format=%ct)" ]; then
  echo "$BUILD/firmware.bin is older than the current commit; rebuild (run without --skip-pio)"; exit 1
fi

APP_SIZE=$(fsize "$BUILD/firmware.bin")
if [ "$APP_SIZE" -gt "$APP_SLOT_SIZE" ]; then
  echo "firmware.bin ($APP_SIZE bytes) exceeds the $APP_SLOT_SIZE byte OTA slot"; exit 1
fi

mkdir -p "$OUT"
# Clear only this script's own outputs so a failed run can't leave a stale mix.
(cd "$OUT" && rm -f M-1_full_install.bin M-1_ota.bin littlefs.bin firmware.elf firmware.map \
  bootloader.bin partitions.bin BUILD_INFO.txt SHA256SUMS.txt)

if [ -n "$LITTLEFS_IN" ]; then
  echo "== LittleFS image: prebuilt $LITTLEFS_IN"
  [ "$(fsize "$LITTLEFS_IN")" -eq "$FS_SIZE" ] || { echo "$LITTLEFS_IN is not $FS_SIZE bytes"; exit 1; }
  cp "$LITTLEFS_IN" "$OUT/littlefs.bin"
  FS_SOURCE="prebuilt $(basename "$LITTLEFS_IN") (apollo/fs last changed in $(git -C "$ROOT" log -1 --format=%h -- apollo/fs))"
else
  "$MKLITTLEFS" --version >/dev/null 2>&1 || {
    echo "mklittlefs at $MKLITTLEFS does not run here (x86-only on macOS: needs Rosetta)."
    echo "If apollo/fs is unchanged since the last release, pass --littlefs <that release's littlefs.bin>."
    exit 1
  }
  echo "== LittleFS image from apollo/fs (offset $FS_OFF, size $FS_SIZE)"
  "$MKLITTLEFS" -c "$ROOT/apollo/fs" -b 4096 -p 256 -s "$FS_SIZE" "$OUT/littlefs.bin" >/dev/null
  FS_SOURCE="mklittlefs $("$MKLITTLEFS" --version 2>&1 | head -1) from apollo/fs"
fi

echo "== M-1_full_install.bin (merged at 0x0, ESP32-S3)"
esptool --chip esp32s3 merge_bin -o "$OUT/M-1_full_install.bin" \
  --flash_mode keep --flash_freq keep --flash_size 16MB \
  0x0 "$BUILD/bootloader.bin" \
  0x8000 "$BUILD/partitions.bin" \
  "$OTADATA_OFF" "$BOOT_APP0" \
  "$APP0_OFF" "$BUILD/firmware.bin" \
  "$FS_OFF" "$OUT/littlefs.bin"

echo "== M-1_ota.bin (app only) and support files"
cp "$BUILD/firmware.bin" "$OUT/M-1_ota.bin"
cp "$BUILD/firmware.elf" "$BUILD/firmware.map" "$BUILD/bootloader.bin" "$BUILD/partitions.bin" "$OUT/"

{
  echo "commit:     $(git -C "$ROOT" rev-parse HEAD) ($(git -C "$ROOT" describe --tags --always --dirty))"
  echo "built:      $(date -u '+%Y-%m-%dT%H:%M:%SZ') (firmware.bin from $(date -u -r "$(mtime "$BUILD/firmware.bin")" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -d "@$(mtime "$BUILD/firmware.bin")" '+%Y-%m-%dT%H:%M:%SZ'))"
  echo "env:        $ENV_NAME"
  echo "platformio: $(pio --version 2>/dev/null || echo unknown)"
  echo "esptool:    $(esptool version 2>/dev/null | tail -1)"
  echo "littlefs:   $FS_SOURCE"
  echo "web ui:     $(grep -h 'define WEB_BUILD_TIME' "$ROOT"/wled00/html_ui.h 2>/dev/null | head -1)"
} > "$OUT/BUILD_INFO.txt"

(cd "$OUT" && shasum -a 256 M-1_full_install.bin M-1_ota.bin littlefs.bin firmware.elf firmware.map bootloader.bin partitions.bin > SHA256SUMS.txt)

echo
echo "Artifacts in $OUT:"
ls -l "$OUT"
echo
cat "$OUT/BUILD_INFO.txt"
echo
echo "App size: $APP_SIZE / $APP_SLOT_SIZE bytes ($((APP_SIZE * 100 / APP_SLOT_SIZE))% of OTA slot)"
