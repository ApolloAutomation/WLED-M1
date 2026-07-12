# READ THIS FIRST (ultracode session)

This session runs in ultracode: xhigh effort plus auto-orchestrated multi-agent workflows.
Subagents get CLEAN context windows. They will not see this file, this conversation, or what a
sibling agent learned. They do NOT inherit CLAUDE.md or AGENTS.md. Everything below exists
because of that.

## Step 0: propagate the facts BY VALUE, not by reference

M1_FACTS.md already exists at the repo root. Commit it onto apollo/m1 as your first commit after
Phase A consolidation.

For every subagent you spawn for the rest of this session:

1. PASTE the relevant FACTS sections VERBATIM into the subagent's brief. Do NOT merely tell it to
   "read M1_FACTS.md". A subagent asked whether it read a file will often say yes and confabulate
   plausible content from the filename alone. Never trust a self-report. Pass the facts by value.
2. Require a read receipt: the subagent's first line of output must restate FACT 1 in one
   sentence. If it cannot, the brief was defective. Re-brief it and run it again.
3. Include: "If you believe a fact here is wrong, do not silently act on that belief. Write your
   evidence to FACT_CHALLENGES.md and return it to the orchestrator."

Skip this and your fleet will independently re-derive the scan rate, the LED type model, and the
ABL behavior, and some of them will get it wrong. That is the single most likely way this session
fails.

## Hardware is a mutex. Exactly one agent, ever.

NEVER fan out any task touching a serial port, esptool, or the device HTTP API. Phase D runs
single-agent, strictly serially, in the orchestrator. Do not delegate any step of it. Two agents
talking to one M-1 corrupts the test. Two agents flashing bricks it.

The 16MB flash dump in D0 is ONE-SHOT and IRREPLACEABLE. No agent may erase, flash, or write to
the device until D0 has completed and the dump has been verified at 16,777,216 bytes. Enforce
this in the orchestrator. Do not assume a subagent read the fine print.

## The working tree is a mutex too.

Fan out READS freely. Serialize WRITES. Never two agents editing one file. Never two agents
running `pio run` in one directory. If you want parallel builds or edits, use git worktrees, one
per agent, and merge deliberately.

## Tokens are not the constraint here. Scope is.

Ultracode treats tokens as no object, which makes it excellent at the audit and verification work
in this task and dangerous on the build work. The explicit goal of this session is to make the
Apollo delta SMALLER, not bigger. If an agent's output grows the diff, that agent is probably
solving a problem upstream already solved. Every added line needs a justification in DECISIONS.md.
Reimplementing the migration from scratch is a failure condition, not a thorough job.

## Where to spend the fan-out

GO WIDE: auditing the +1163/-2 delta against upstream line by line; the 13-page wiki triage;
adversarially verifying FACTS 1 through 4 against source; cross-referencing WLED-MM source,
upstream source, and the built artifact's cfg.json.

STAY SINGLE: anything touching hardware, git writes, the build, and the decision on what to delete.

## Adversarial verification task

FACTS 1, 2, and 3 were derived by a chat model reading source, not by running code. Assign an
agent to each with the brief: "try to prove this wrong." Being corrected now is far cheaper than
being corrected after a bad flash. FACT 4 is explicitly unresolved and needs a verdict.

---

# TASK: Apollo M-1 WLED migration, session 3 (continue and correct, do not restart)

Two prior sessions did most of this. Your job: find that work, correct a structural
misunderstanding in it, shrink it, finish it. Rebuilding from scratch is the worst possible
outcome. Read M1_FACTS.md first, then PROGRESS.md, DECISIONS.md, SUMMARY.md, BLOCKED.md once
Phase A makes them available.

## What this is

Apollo Automation makes the M-1 LED Matrix: a 64x64 HUB75 panel driven by an ESP32-S3 controller
(16MB flash, 8MB octal PSRAM). It ships running WLED-MM (the MoonModules fork). We are migrating
it to upstream WLED 16.x, which now supports HUB75 natively.

The headline bug: on a fresh flash the panel comes up as a 32x32 matrix on a 64x64 panel.
Customers see a quarter-lit display and conclude the hardware is dead. A correct build must boot
straight into HUB75 64x64 with zero user configuration. Everything else is secondary to that.

## Repo state

- This repo is a clone of ApolloAutomation/wled-m1, our fork of wled/WLED. It is canonical
  going forward. Note the fork name is `wled-m1`. A prior session guessed `wled`. Correct any
  remote or doc that says otherwise.
- GitHub is now authenticated. Prior sessions could not push because a GUI git client held the
  credentials and terminal git had none. VERIFY with `git ls-remote origin` before relying on it.
- The prior work lives in a DIFFERENT clone elsewhere on this machine. See Phase A.

## PHASE A: Find and consolidate the prior work (HARD GATE)

The prior work is 9 commits on branch `apollo/m1` in an OLDER, separate clone of WLED somewhere
on this machine. It has NEVER been pushed to any remote. It exists nowhere else. Not losing it is
your first and most important job.

That clone is outside this session's project root, so the Read/Glob/Grep tools cannot index it.
Bash can reach it. Use Bash. Use `git -C <path>` to run git commands in another directory without
changing your working directory.

### A1. Locate the clones

    find ~ -maxdepth 6 -type d -name '.git' 2>/dev/null | grep -i -E 'wled|installer'
    find ~ -maxdepth 6 -name platformio.ini 2>/dev/null | grep -i wled

For each candidate that is not this repo, inspect it without leaving your working directory:

    git -C /candidate/path remote -v
    git -C /candidate/path branch -a
    git -C /candidate/path log --oneline apollo/m1 | head -12

You are looking for the one with 9 commits on `apollo/m1` and a branch
`hub75-first-boot-defaults`. Also find the ApolloAutomation/installer clone, which has a branch
`feat/m1-wled-entry`.

### A2. Pull the prior work into THIS repo

From the root of wled-m1:

    git fetch /absolute/path/to/old/clone 'refs/heads/*:refs/remotes/prior/*'
    git branch -r
    git log --oneline prior/apollo/m1 | head -12

### A3. PROVE IT before you go further

Print all of the following. Do not proceed until every one is satisfied:

    - the absolute path of the old clone you fetched from
    - the exact commit count on prior/apollo/m1 (expect 9)
    - the diffstat versus its base (expect roughly +1163/-2)
    - the subject lines of all 9 commits

If the count is not 9 or the diffstat is wildly off, you have the wrong clone. Keep looking.

### A4. Check out and secure it

    git checkout -b apollo/m1 prior/apollo/m1
    git checkout -b hub75-first-boot-defaults prior/hub75-first-boot-defaults

Confirm TASK.md and M1_FACTS.md are still in the working tree. They are untracked so they should
survive the checkout. If either is missing, restore it from the previous branch. Commit
M1_FACTS.md onto apollo/m1 as your first commit.

Verify auth with `git ls-remote origin`, then push both branches to origin
(ApolloAutomation/wled-m1). Confirm the push landed by comparing remote commit count to local.
Never push to main. Never force push.

Push the installer branch too, without leaving this directory:

    git -C /path/to/installer-clone push -u origin feat/m1-wled-entry

Confirm ApolloAutomation/wled-m1 is public. WLED is EUPL-1.2 and we owe source availability once
we ship binaries. If it is private, flag it in SUMMARY.md.

### A5. If you are blocked

If `find` returns nothing, or a bash command is denied, or the fetch fails: STOP. Write BLOCKED.md
containing the exact commands Trevor needs to run, then halt.

Do NOT reimplement the migration from scratch. Do NOT "start clean since the old work cannot be
found." Do NOT open platformio.ini. Rebuilding this work is the single worst outcome available to
you, and it is worse than doing nothing at all. A missing clone is a blocked state, not an
invitation to start over.

## AUDIT: shrink the delta

The prior delta is +1163/-2. Go through it line by line and DELETE anything that duplicates what
`env:esp32s3dev_16MB_opi_hub75` already provides (board, PSRAM, partitions, pinout, mic pins,
HUB75 flags). See FACT 3. Every redundant line is debt that fights every future upstream rebase.
Report before and after diffstat in SUMMARY.md. If it does not shrink substantially, explain why.

Also re-audit anything built on the assumption that the 32x32 bug was a DEFAULT_LED_TYPE problem.
See FACT 2. That framing is correct for WLED-MM and wrong for upstream. Verify by inspecting
cfg.json inside the built artifact, not by reading source.

## THE APOLLO DELTA (this is the whole list)

Trevor's priority: preset as many settings as possible so the customer configures NOTHING.

1. HUB75 bus type: Half Scan (65).
2. Panel width 64, panel height 64.
3. CHAIN LENGTH = 1. Explicitly. This was unsettable in WLED-MM. It must READ as 1 in the
   customer's LED Preferences UI, not merely clamp to 1 internally.
4. 2D config: single 64x64 matrix, one panel.
5. Automatic brightness limiter: OFF. See FACT 4.
6. Default brightness: a value that produces VISIBLE LIGHT on first boot and does not brown out a
   3A supply. Measure it. Do not guess.
7. Boot preset / default effect: something visibly alive, not Solid-black. A factory unit powering
   on to a dark panel produces the exact same support ticket we are trying to eliminate. Propose
   an option, do not decide.
8. Default segment must span the full 64x64. A partial segment looks like a broken panel.
9. AudioReactive: type and pins already come from the upstream env (FACT 3). Set sync mode to Off
   by default. See D3 for the `enabled` question.
10. Apollo identity: name "Apollo M-1", mDNS apollo-led-matrix-xxxxxx, AP "Apollo M-1-xxxxxx" with
    password wled1234, brand and product strings, release name.
11. The WLED-MM to upstream config migration shim (old cfg says type 101/103, which 16.x would
    otherwise read as garbage and blank the display on OTA).

That is the list. If you are adding anything else, justify it in DECISIONS.md.

## MY DECISIONS (answered, apply them)

- D1. AP password: `wled1234` (WLED's documented default). Log that OTA-upgraded units keep their
  existing open AP, since cfg.json survives an OTA; only a full-erase flash gets the password.
- D2. Unique names: YES. mDNS apollo-led-matrix-xxxxxx, AP "Apollo M-1-xxxxxx", 6 MAC hex chars.
- D3. AudioReactive `enabled` default: OPEN. Do not guess. Measure on hardware (CPU load, free
  heap, panel refresh rate, current draw) with the usermod enabled and NO mic fitted, which is the
  rev4 case. Then recommend. Pins, type, and sync-off are baked regardless, so a rev6 owner
  installing the mic addon should have exactly one toggle left, not five. Reducing the microphone
  wiki page from 5 steps to 2 is the win either way.
- D4. Server description: "Apollo M-1", not "Apollo LED Matrix".
- D5. Upstream PRs: prepare fully. Do NOT open them. Trevor will.

## PHASE B: Wiki triage (this is the real definition of done)

Read every M-1 page under https://wiki.apolloautomation.com. This is your best fan-out candidate:
one agent per page, results merged into one file. Do not run them serially in one window.

    /products/m1/introduction/
    /products/m1/faq/
    /products/m1/setup/getting-started-m1/
    /products/m1/setup/m1-general-tips/
    /products/m1/setup/m1-matrix-settings/
    /products/m1/setup/m1-multiple-panels/
    /products/m1/setup/m1-segments/
    /products/m1/setup/m1-pinout-guide/
    /products/m1/addons/adding-microphone-to-m-1/
    /products/m1/troubleshooting/m1-reflash/
    /products/m1/troubleshooting/m1-boot-mode/
    /products/m1/troubleshooting/m1-find-ip-address-and-hostname/
    /products/m1/examples/*   (GIFs, scrolling text, QR code, HA data sharing)

Every manual configuration step on those pages is a defect in the firmware defaults.

Produce WIKI_TRIAGE.md: one row per step, classified FIXED AS DEFAULT / CANNOT FIX (with reason) /
NOT A DEFAULT (genuine user choice). The matrix-settings page should end up almost entirely in
column one. If it does not, the job is not done.

Cross-check the M-1 pinout guide against the MOONHUB gpio map in FACT 3. Confirm the E line
(GPIO 38) is landed. If E is unused, FACT 1 is wrong. Escalate immediately.

The M-1 also has an ESPHome firmware option with its own wiki path and its own installer entry.
Do not break it. Confirm the installer keeps offering both firmwares.

## PHASE C: Build and verify

- Recheck upstream tags. If v16.1.x now exists, evaluate rebasing apollo/m1 onto it and log the
  decision either way. Do not rebase silently. There was no v16.1 tag as of the last session.
- Build `apollo_m1` clean on this machine. Never proceed on a build you have not watched pass.
  Expect toolchain friction (npm cache paths, mklittlefs). Fix it and log it.
- Report binary size and headroom. Prior build: 1,250,064 bytes, 39.7% of the 3MB OTA slot.
- Verify the acceptance values INSIDE the artifacts: unpack the LittleFS image and read cfg.json.
  Do not verify by reading source.

## PHASE D: Hardware QA. SINGLE AGENT ONLY. NO FAN-OUT.

Only if M1_ALLOW_FLASH=1 and a unit is on serial. If it is not set, skip to Phase E and write the
QA checklist for Trevor to run by hand. The order below is not negotiable. Doing it out of order
destroys evidence we cannot recover.

D0. CAPTURE THE FIELD UNIT BEFORE YOU TOUCH IT. One-shot, irreversible. This unit is the only
    specimen of the exact state every customer unit is in, and it is what the OTA migration shim
    must be validated against.

        curl -s http://$M1_IP/json/info    > baseline/live/json_info.json
        curl -s http://$M1_IP/json/state   > baseline/live/json_state.json
        curl -s http://$M1_IP/json/cfg     > baseline/live/json_cfg.json
        curl -s http://$M1_IP/presets.json > baseline/live/presets.json
        curl -s http://$M1_IP/cfg.json     > baseline/live/cfg.json
        esptool.py --port <port> read_flash 0 0x1000000 baseline/live/m1_factory_16mb.bin

    Verify the dump is 16,777,216 bytes. Commit the JSON captures. Do NOT commit the 16MB dump;
    store it and note the path. This dump is both the rollback AND a replayable field unit: it
    lets us re-test the OTA path as many times as needed.

D1. DIFF the live capture against the baseline reconstructed from source. Every mismatch is an
    assumption we got wrong. Report all of them before flashing anything.

D2. TEST THE OTA PATH FIRST. This is the highest-risk path and the one that touches existing
    customers. With the unit still on WLED-MM and its real cfg.json intact, push M-1_ota.bin
    through WLED's update page. Confirm:
      - the panel still lights, at 64x64, not dark and not a 32x32 quadrant
      - the migration shim correctly reinterpreted the old type 101/103 config
      - settings, mDNS name, and WiFi survived
    If it fails, restore the flash dump, fix, repeat. Do not move on until this passes.

D3. THEN the full-install path. esptool erase_flash, flash M-1_full_install.bin at 0x0, power on
    with a 64x64 panel and ZERO configuration. Confirm every item in THE APOLLO DELTA via
    /json/cfg and /json/info, including chain length reading as 1.

D4. THE REAL ACCEPTANCE TEST: a factory unit, powered on, unconfigured, must show VISIBLE LIGHT
    across the full 64x64 panel within a few seconds. Fixing 32x32 to 64x64 is worthless if the
    default state is off, black, or brightness zero, because the customer sees a dead panel and
    files the same ticket. Photograph the result.

D5. MEASURE CURRENT DRAW at full white, 100% brightness, on the stock 3A supply. We ship with the
    brightness limiter OFF, so there is no software current cap. If it browns out, flickers, or
    exceeds the supply, cap the default brightness and log it.

D6. GHOSTING. Test at full white. Upstream documents `-D WLED_HUB75_MAX_BRIGHTNESS=239` as the
    fix. Set it if needed.

D7. DRIVER CHIP. If the panel is dark or the colors look pastel, the shift register driver is
    wrong. Identify the M-1 panel's actual driver IC and set it explicitly rather than relying on
    the library default. See the fault decoder in M1_FACTS.md.

D8. WIFI UNDER LOAD. Upstream carries `-D S3_LCD_DIV_NUM=20` commented "attempt to fix wifi
    performance issue when panel active with S3 chips". Known issue. Test throughput and stability
    with the panel running a heavy effect. Customers will notice.

D9. AUDIOREACTIVE. Test on a rev6 board with the mic addon fitted: confirm pins 10/11/12, confirm
    it responds to sound, confirm Sync is Off. Then repeat with no mic fitted to resolve D3.

D10. FOUR-PANEL CHAIN at 256x64. Marketed feature, never tested on this firmware. The code clamps
     chain to 1..4 and requires PSRAM above one panel at 64px height. We have 8MB OPI PSRAM.

D11. HOME ASSISTANT. Confirm the WLED integration discovers the device, the entity name is right,
     the effect list populates, and there are no errors in the log.

D12. ROLLBACK. Restore m1_factory_16mb.bin and confirm the unit returns to its original shipping
     state.

Use the panel fault decoder in M1_FACTS.md instead of guessing when something looks wrong.

## PHASE E: Wrap up

- QA_CHECKLIST.md with actual results, not intentions.
- SUMMARY.md precisely separating hardware-verified from build-verified-only. Be exact about the
  difference. Lead with the before/after diffstat from the audit.
- WIKI_TRIAGE.md, plus rewritten matrix-settings, microphone, and troubleshooting wiki pages. Add
  the panel fault decoder to the troubleshooting page.
- FACT_CHALLENGES.md if any agent found evidence against a fact.
- Both upstream PRs prepared and unopened: the HUB75 first-boot defaults fix, and (if FACT 4 is
  confirmed) the HUB75 ABL exemption.
- Installer changes: the installer clone is outside this session's project root. Do not modify it
  beyond the push in Phase A. If Phase E needs installer changes, write them as a patch file in
  apollo/ and tell Trevor. Do not touch production install.apolloautomation.com.
- Rollback instructions plus archived last-known-good WLED-MM binaries.
- Follow-up list for Trevor: any wiki, shop, or listing copy referencing WLED-MM or Pixel Magic
  that will now be wrong.

## Standing rules

Never push to main. Never force push. Never tag or cut a release. Never open a pull request. Never
touch Shopify, the wiki, or the production installer. No secrets in commits: WiFi credentials, AP
password, and OTA password live in a gitignored my_config.h with a my_config.h.example committed
alongside. Blocked after 3 real attempts means write it to BLOCKED.md and move on, not stall. Keep
PROGRESS.md current so a fresh session can resume from it.

Trevor is AFK. Do not stop to ask questions. When you hit an ambiguity, take the conservative
option, log it in DECISIONS.md under "Assumptions to confirm", and keep going.

## Style rules for any user-facing text you draft

No em dashes. No en dashes as punctuation. No emojis. Never use "seamlessly", "powerful",
"simple", "simply", or "just" as filler. Always write "Open Home Foundation" in full. Never write
"Home Assistant add-on"; use "Home Assistant app". Tone: reassuring, matter-of-fact,
community-first, humble. Never promotional.