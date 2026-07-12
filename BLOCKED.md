# BLOCKED

## B1. Live-device baseline capture (Phase 0)
Goal: curl /json/info, /json/state, /json/cfg, presets.json, cfg.json from a live M-1
running WLED-MM into baseline/.
Attempts:
1. mDNS: dns-sd browse for _wled._tcp on local network; probed apollo-led-matrix.local
   and wled-apollo.local over HTTP. No responders.
2. Home Assistant: the only WLED integration entry points at 192.168.20.30, state
   setup_retry (device offline), and its entities identify it as "The Belle Permanent
   Lights", not an M-1. Direct HTTP probe of 192.168.20.30 timed out.
3. Full sweep of the Mac's subnet 192.168.1.0/24 (curl /json/info on all 254 hosts):
   only a Pi-hole admin page answered. M1_IP env var is not set.
Status: blocked on hardware availability. Work continues using the shipping build
config and WLED-MM source defaults as ground truth (baseline/README.md). Consequence:
the known-good cfg.json for the Phase 3 filesystem image is synthesized against the
WLED 16.0.1 cfg schema instead of captured, and must be validated on hardware before
release (QA checklist item).

## B2. Hardware flash verification (Phase 6)
M1_ALLOW_FLASH is not set and no device is on a serial port. Per the operating rules,
stopping at artifacts plus a hardware QA checklist.
