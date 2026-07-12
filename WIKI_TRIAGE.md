# WIKI_TRIAGE

Session 3, derived by one read-only agent per wiki page (13 agents), classified
against the m1-wled-update factory defaults. Classifications:
FIXED AS DEFAULT = step is unnecessary on a factory unit running the new firmware;
CANNOT FIX = firmware cannot remove it (reason given);
NOT A DEFAULT = genuine user choice, keep documenting.

## Scorecard

| Page | Fixed as default | Cannot fix | Not a default |
|---|---|---|---|
| introduction | 0 | 0 | 0 |
| faq | 6 | 2 | 4 |
| getting-started | 8 | 8 | 0 |
| general-tips | 0 | 0 | 0 |
| matrix-settings | 11 | 2 | 0 |
| multiple-panels | 0 | 6 | 7 |
| segments | 0 | 2 | 6 |
| pinout-guide | 5 | 0 | 0 |
| microphone-addon | 5 | 5 | 0 |
| reflash | 0 | 11 | 0 |
| boot-mode | 0 | 5 | 0 |
| find-ip-hostname | 1 | 5 | 1 |
| examples | 1 | 19 | 30 |
| TOTAL | 37 | 65 | 48 |

## introduction
https://wiki.apolloautomation.com/products/m1/introduction/

Product-overview page for the Apollo M-1 LED matrix (4096-pixel HUB75 display, integrated 5V 3A controller). Pure prose: product specs, "pre-flashed with WLED firmware" claim, capability claims (up to four chained panels with power injection, Pixel Magic for custom images, real-time data visualization), and a list of seven use cases. Sidebar links to setup, configuration (matrix settings, segments, pinout), microphone addon, examples (GIFs, scrolling text, QR codes), troubleshooting, and the alternative ESPHome firmware. The page contains zero manual instruction/configuration steps.

No manual configuration steps on this page.

Copy updates needed:
- "Pixel Magic tool" reference: Pixel Magic is a MoonModules/WLED-MM-ecosystem tool; after the move to upstream WLED 16.0.1 this workflow may no longer apply as described. Verify it still works against upstream WLED or update/remove the mention (also check the examples sub-pages it foreshadows).
- "Pre-flashed with WLED firmware" is still accurate under the new upstream-WLED 16.0.1 firmware (arguably more accurate than under WLED-MM); no change strictly required, but if other pages say WLED-MM/MoonModules this page's plain "WLED" is the wording to standardize on.
- "Supports up to four panels connected horizontally": capability claim remains true, but the factory default is now chain length 1 with a single 64x64 panel; consider a note that multi-panel setups require changing chain length (the actual steps belong on the configuration page, not here).
- Sidebar's ESPHome alternative-firmware section must be preserved untouched, the WLED migration explicitly must not break or hide the ESPHome option.

Fact challenge field: No premise challenged: the introduction page says nothing about panel scan type, HUB75 bus types, AP credentials, hostnames, audio pins, or brightness limiter, so nothing on it contradicts FACT 1 or the stated new-firmware defaults.

## faq
https://wiki.apolloautomation.com/products/m1/faq/

M-1 FAQ page with 9 Q&As: (1) half-screen-of-color symptom pointing users at the post-connect-setup steps, (2) vertical lines fixed by re-seating the controller, (3) max power spec, (4) scrolling-text fix via 2D Matrix 64x64 / chain length 1 / disable auto brightness limiter, (5) WizMote support requiring a special firmware compile, (6) enabling audio-reactive from the info pane, (7) using the device without WiFi via the WLED-AP (password wled1234) at http://4.3.2.1 or http://wled.me, (8) power draw prose, (9) reflashing requires a special fork, links the srg74 WLED-wemos-shield ESP Flasher and a Discord CDN download of WLEDMM_0.14.1-b32.40_adafruit_matrixportal_esp32s3.bin.

| Step | Classification | Reason |
|---|---|---|
| Q1: Follow the post-connect-setup steps to configure required settings (fix for seeing only half a screen of color) | FIXED AS DEFAULT | New firmware factory-boots a HUB75 Half Scan bus (type 65), one 64x64 panel, chain 1, 2D matrix 1x 64x64, the half-screen symptom should not occur on a factory unit and no post-connect configuration is required. |
| Q2: Re-seat the M-1 controller on the back of the matrix panel (fix for vertical sideways lines) | CANNOT FIX | Physical assembly/connector seating issue; firmware cannot correct a poorly seated HUB75 connector. |
| Q4: Navigate to Config -> 2D Configuration, select 2D Matrix (Basic) | FIXED AS DEFAULT | Factory default already configures a 2D matrix (1x 64x64). |
| Q4: Change Panel Dimensions to 64 x 64 and click Save | FIXED AS DEFAULT | 64x64 panel dimensions are the factory default. |
| Q4: Config -> LED Preferences, set Chain Length to 1 | FIXED AS DEFAULT | Chain length 1 is the factory default. |
| Q4: Uncheck 'enable automatic brightness limiter' and click Save | FIXED AS DEFAULT | Automatic brightness limiter is OFF in the factory defaults. |
| Q5: Compile/flash a special firmware build to use the WizMote over ESP-NOW | FIXED AS DEFAULT | The new firmware is based on upstream WLED 16.0.1, which ships ESP-NOW/WizMote remote support in standard builds, no special compile should be needed (verify ESP-NOW remote is enabled in the m1-wled-update build flags). Pairing the remote (enabling ESP-NOW and entering the WizMote MAC in WiFi settings) remains a per-user step the page should document. |
| Q6: Enable audio-reactive from the 'info' pane | CANNOT FIX | AudioReactive is compiled in and fully preconfigured (Generic I2S, SD 10 / WS 12 / SCK 11, sync Off) but ships disabled because the microphone is an optional rev6 addon; whether it is installed depends on the customer's hardware, so the single enable toggle must remain. Note the toggle location has moved, see copy updates. |
| Q6: Select effects marked with the musical note icon | NOT A DEFAULT | Which effects to run is customer taste; the musical-note guidance remains valid usage documentation. |
| Q7: Connect to the device's access point (page says SSID 'WLED-AP', password wled1234) | NOT A DEFAULT | Using the M-1 without WiFi/Home Assistant is a genuine user choice and joining the AP is inherent to it; keep documenting, but the SSID is now 'Apollo M-1-xxxxxx' (password wled1234 is unchanged). |
| Q7: Browse to http://4.3.2.1 or http://wled.me while on the AP | NOT A DEFAULT | Inherent part of the AP-only workflow; both addresses remain valid in AP mode (the captive DNS is independent of the new mDNS hostname). |
| Q9: Flash the device with WLEDMM_0.14.1-b32.40_adafruit_matrixportal_esp32s3.bin using the srg74 WLED-wemos-shield ESP Flasher tool | NOT A DEFAULT | Reflashing/recovery is a legitimate user-initiated action the page should keep documenting, but the referenced binary, Discord CDN link, and third-party flasher are obsolete, it must point at the new Apollo M-1 firmware install path, note that OTA from the old WLED-MM build preserves settings while a full-erase install restores factory defaults, and continue to present the ESPHome firmware option without hiding it. |

Copy updates needed:
- Q1 answer states 'The firmware we use currently does not support us pre-configuring a few settings but they are required to be set', now false; the new firmware ships fully preconfigured (HUB75 Half Scan type 65, 64x64, chain 1, ABL off, Solid orange at brightness 128). Rewrite Q1: a factory unit should never show half a screen; if it does after a manual reconfig, the likely cause is selecting a plain-panel type instead of the Half Scan type.
- Q1 links to https://wiki.apolloautomation.com/products/m1/setup/getting-started-m1/#post-connect-setup, that anchor/section will change or disappear once post-connect setup is unnecessary; update or remove the link.
- Q4 (scrolling text) answer is entirely obsolete: 2D Matrix 64x64, chain length 1, and unchecking the automatic brightness limiter are all factory defaults now. Rewrite to 'works out of the box' (keep only as troubleshooting after a factory reset of a non-Apollo build, if at all).
- Q5 (WizMote): remove 'Currently needs a special firmware compiled', the upstream WLED 16.0.1 base includes ESP-NOW/WizMote support; replace with instructions to enable the ESP-NOW remote and enter the WizMote MAC in WiFi settings (verify the m1-wled-update build enables ESP-NOW remote before publishing).
- Q6 (microphone): 'enable it from the info pane' is WLED-MM UI wording; in the upstream-16-based firmware AudioReactive is enabled via the Usermod/Sound settings toggle (Config -> Usermods). All pins (SD 10 / WS 12 / SCK 11, Generic I2S) are preconfigured, so the rev6 mic addon needs only that single enable toggle. Also clarify the mic is a hardware addon.
- Q7: AP SSID 'WLED-AP' is stale, new setup AP SSID is 'Apollo M-1-xxxxxx' (xxxxxx = last 6 MAC hex chars); password wled1234 is unchanged; http://4.3.2.1 and http://wled.me remain valid. Note the AP is not open/passwordless.
- Q9: firmware filename WLEDMM_0.14.1-b32.40_adafruit_matrixportal_esp32s3.bin, the Discord CDN attachment link, and the srg74 WLED-wemos-shield ESP Flasher link (https://github.com/srg74/WLED-wemos-shield/tree/master/resources/Firmware/WLED_%20ESP_Flasher) are all stale, point at the new ApolloAutomation firmware/install method; state OTA-updating from the old WLED-MM build preserves settings (migration shim) while a full-erase flash restores factory defaults; keep the ESPHome firmware option visible as an alternative.
- Consider adding the new identity details where relevant: server description 'Apollo M-1' and mDNS hostname apollo-led-matrix-xxxxxx.local for finding the device on the LAN (the page currently never mentions a hostname).
- Q1/Q4 cross-link https://wiki.apolloautomation.com/products/m1/setup/m1-matrix-settings/, that settings page describes the now-unnecessary manual matrix configuration and will itself need revision; re-check this link after that page is updated.

Fact challenge field: No premise on this page contradicts the provided facts. The FAQ never names a Hub75Matrix panel type, WLED-MM, MoonModules, Pixel Magic, or Pixelforge; its half-screen symptom (Q1) is consistent with a half-scan panel being driven with a plain-panel/wrong scan configuration. One item to verify rather than a challenge: the claim that WizMote no longer needs a special compile assumes ESP-NOW remote support is enabled in the m1-wled-update build, which the provided defaults list does not explicitly state.

## getting-started
https://wiki.apolloautomation.com/products/m1/setup/getting-started-m1/

"Getting Started (WLED-MM)" page (breadcrumb: Home Assistant > M-1 (LED Matrix) > Getting Started). Covers: physically attaching the controller to the panel; joining the open "Apollo M-1" setup AP and entering home Wi-Fi credentials at http://4.3.2.1/ or http://wled.me (with optional hostname "apollo-led-matrix"); a "Required Configuration" section (LED Preferences: chain length 1, uncheck automatic brightness limiter, confirm Hub75Matrix 64x64; 2D Configuration: 2D Matrix, Basic, panel dimensions 64x64); and Home Assistant auto-discovery via the WLED integration. Opens with a note redirecting hub75-studio ESPHome firmware users to the ESPHome getting-started page. No mention of an AP password, scan type, brightness/effect defaults, AudioReactive/mic, install URLs, MoonModules, Pixel Magic, or Pixelforge; "WLED-MM" appears only in the title/heading.

| Step | Classification | Reason |
|---|---|---|
| Gently attach the controller to the back of the M-1 LED Matrix panel | CANNOT FIX | Physical assembly, the controller ships detached; firmware cannot remove this step. |
| Plug in the USB-C power and let the device boot | CANNOT FIX | Physical power-up; not addressable by firmware defaults. |
| On your phone, select the 'Apollo M-1' Wi-Fi network | CANNOT FIX | Onboarding requires joining the setup AP; firmware cannot skip it. But copy must change: new SSID is 'Apollo M-1-xxxxxx' (unique suffix) and the AP now requires password wled1234, the page currently mentions no password. |
| Navigate to http://4.3.2.1/ or http://wled.me | CANNOT FIX | Captive-portal navigation is inherent to Wi-Fi onboarding; still valid on upstream WLED 16.0.1. |
| Tap Wi-Fi Settings and input your Wi-Fi SSID where it shows Your_Network | CANNOT FIX | Depends on the customer's Wi-Fi network; firmware cannot know it. |
| Input your Wi-Fi password below it and click Save and Connect | CANNOT FIX | Depends on customer Wi-Fi credentials. |
| Optionally set your hostname here, such as 'apollo-led-matrix' | FIXED AS DEFAULT | New firmware ships mDNS hostname apollo-led-matrix-xxxxxx (unique per unit) by default, so the suggested rename is unnecessary; changing it further remains an available user choice but need not be a documented setup step. |
| Click Config, then LED Preferences | FIXED AS DEFAULT | Navigation exists only to perform the three LED Preferences changes below, all of which are now factory defaults. |
| Set Chain Length to 1 | FIXED AS DEFAULT | Factory default is chain length 1. |
| Uncheck 'enable automatic brightness limiter' and click Save | FIXED AS DEFAULT | Automatic brightness limiter is OFF by factory default. |
| Confirm Hub75Matrix is set to 64x64 | FIXED AS DEFAULT | Factory default is a HUB75 Half Scan bus (type 65), one 64x64 panel. Note the wiki's 'Hub75Matrix 64x64' is the WLED-MM plain-panel type 103, which is the wrong type for this half-scan panel, the new default is both preset and correct, so this instruction should be deleted, not translated. |
| Click Config, then 2D Configuration | FIXED AS DEFAULT | Navigation exists only for the 2D setup steps below, which are now factory defaults. |
| Select 2D Matrix and click the circle next to Basic | FIXED AS DEFAULT | Factory default is a 2D matrix configuration (1x 64x64). |
| Change the Panel Dimensions to 64 x 64 and click Save | FIXED AS DEFAULT | Factory default panel dimensions are 64x64; no save needed. |
| Head to the Integrations page in Home Assistant and accept the auto-discovered WLED device (Click Add, then Click Submit) | CANNOT FIX | Happens inside the customer's Home Assistant instance; device firmware cannot accept the discovery on their behalf. |
| Give it a name and a location, then click Skip and Finish | CANNOT FIX | Naming/area assignment is done in the customer's Home Assistant and reflects customer taste; outside firmware control. |

Copy updates needed:
- Title/heading: 'Getting Started (WLED-MM)' and 'Getting Started with M-1 LED Matrix (WLED-MM)', firmware is now upstream WLED 16.0.1-based, not WLED-MM/MoonModules; retitle (e.g. 'Getting Started (WLED)').
- Setup AP SSID: page says 'Apollo M-1'; new SSID is 'Apollo M-1-xxxxxx' (last 6 MAC hex chars). Also the AP is no longer open/passwordless, the page must add the AP password wled1234, which it currently never mentions.
- Hostname copy: 'set your hostname here such as apollo-led-matrix', the default hostname is now apollo-led-matrix-xxxxxx out of the box; drop or reframe this as purely optional customization.
- Delete the entire 'Required Configuration' section (LED Preferences: chain length 1, ABL uncheck, Hub75Matrix 64x64; 2D Configuration: 2D Matrix/Basic/64x64), all factory defaults now. If any recovery/troubleshooting variant is kept, it must reference the upstream 'HUB75 Half Scan' type (type 65), not the MM 'Hub75Matrix 64x64' entry, which is the plain (non-half-scan) type 103 and is wrong for this panel.
- Consider adding: factory unit boots powered on at brightness 128 showing a Solid orange effect, useful 'what you should see' copy the page currently lacks.
- Consider adding for existing owners: OTA update from old WLED-MM firmware preserves settings (HUB75 config migrated automatically); a full-erase reflash returns the unit to factory defaults.
- Keep the ESPHome note ('If you flashed the hub75-studio ESPHome firmware, head to the ESPHome Getting Started page instead'), the WLED migration does not affect it.
- No occurrences of MoonModules, Pixel Magic, Pixelforge, or install.wled.me/web-installer URLs on this page; 'WLED-MM' appears only in the title/heading and needs updating as above.

Fact challenge field: No premise challenged. The page itself never mentions scan type; its 'Hub75Matrix ... 64x64' instruction is consistent with FACT 1's claim that the wiki selects the plain type 103 rather than a half-scan type.

## general-tips
https://wiki.apolloautomation.com/products/m1/setup/m1-general-tips/

A short prose "General Tips" page. It states the M-1 runs "WLED MoonModules," a fork of WLED supporting the Hub75 Matrix (linking to github.com/MoonModules/WLED-MM), explains that segments act as virtual LED strips/panels (enabling scrolling text across chained panels and driving two panels from one controller), and notes JSON API support for Home Assistant integration (linking to the MoonModules docs at mm.kno.wled.ge), with a tip that scrolling text works best on 1-3 panels since it supports up to 32 characters. It ends with links to the m1-segments and m1-multiple-panels wiki pages. The page contains zero manual instruction/configuration steps, no settings values, dropdown selections, checkboxes, pin entries, reboots, or button holds, so there is nothing to classify as FIXED_AS_DEFAULT / CANNOT_FIX / NOT_A_DEFAULT. Its triage impact is purely copy: the WLED-MM/MoonModules identity claim and the two MoonModules URLs become inaccurate under the new upstream-WLED-16.0.1-based Apollo firmware.

No manual configuration steps on this page.

Copy updates needed:
- Opening claim that the M-1 'operates using WLED MoonModules... a fork of WLED that supports the Hub75 Matrix', the new firmware is based on upstream WLED 16.0.1 (Apollo build from ApolloAutomation/WLED-M1, branch m1-wled-update), which supports HUB75 natively (Half Scan bus type 65); the MoonModules framing should be rewritten (or kept only as a note for units still on the old firmware).
- Link to https://github.com/MoonModules/WLED-MM, should point to the Apollo firmware repo (ApolloAutomation/WLED-M1) or be removed.
- JSON API documentation link https://mm.kno.wled.ge/interfaces/json-api/ points at the MoonModules docs mirror, should point to the upstream WLED docs (https://kno.wled.ge/interfaces/json-api/) once the firmware is upstream-based.
- The 'up to 32 characters' scrolling-text limit and 'use 1 to 3 panels instead of 4' guidance were written against WLED-MM's scrolling-text behavior; verify these numbers still hold on the upstream 16.0.1 Scrolling Text effect before keeping them.
- No references on this page to Pixel Magic, Pixelforge, open/passwordless AP, hostnames, or install URLs, no AP/hostname copy changes needed here (those belong on the setup/install pages).

Fact challenge field: No premise challenged: nothing on this page conflicts with the stated new-firmware defaults (half-scan type 65, Apollo M-1 identity, AP password wled1234, AudioReactive preconfig, OTA migration shim, or the separate ESPHome option). The page never mentions scan type, AP credentials, or hostnames at all.

## matrix-settings
https://wiki.apolloautomation.com/products/m1/setup/m1-matrix-settings/

Page loaded fine (no 404). "M-1 LED Matrix Settings for WLED" walks a user who has just flashed WLED (links to the m1-reflash guide as prerequisite) through five manual configuration sections: Friendly Name (Config > User Interface, Server description e.g. "Apollo LED Matrix"), Hostname (Config > WiFi Setup, mDNS e.g. "apollo-led-matrix", accessible at http://apollo-led-matrix.local, with hostname-character-rule callouts), LED Settings (Config > LED Preferences: select "Hub75Matrix 64x64", Chain Length 1, uncheck automatic brightness limiter, Save), 2D Settings (Config > 2D Configuration: 2D Matrix, Basic layout, Panel Dimensions 64x64, Save), and AudioReactive Settings (rev6 PCB + optional mic addon only: check Enabled, Type Generic I2S, pins SD 10 / WS 12 / SCK 11, Mode Off, Save). Callouts note AudioReactive does not work on Rev4 boards. With the new firmware defaults, every section except the single AudioReactive enable toggle is factory-preconfigured, so the page can shrink to optional personalization plus the mic-addon toggle.

| Step | Classification | Reason |
|---|---|---|
| Prerequisite: flash the M-1 following the linked flashing guide (m1-reflash) | CANNOT FIX | Flashing/reflashing is a user-performed physical recovery or migration action firmware cannot eliminate; note however that a full-erase install of the new firmware restores all factory defaults, making every downstream step on this page unnecessary post-reflash, and OTA from old WLED-MM preserves settings via the migration shim. |
| Friendly Name: Config > User Interface, enter a descriptive name (e.g. "Apollo LED Matrix") in Server description | FIXED AS DEFAULT | Factory firmware ships with server description "Apollo M-1", so no entry is required; picking a different personal name remains an optional taste choice, not a setup step. |
| Hostname: Config > WiFi Setup, set mDNS address (e.g. apollo-led-matrix) so the device is reachable at http://apollo-led-matrix.local | FIXED AS DEFAULT | Factory firmware ships with unique mDNS hostname apollo-led-matrix-xxxxxx (last 6 MAC hex chars), so the device is reachable out of the box; customizing it remains optional. The page's example URL without the -xxxxxx suffix is now inaccurate. |
| LED Settings: Config > LED Preferences, select "Hub75Matrix 64x64" from the LED type dropdown | FIXED AS DEFAULT | Factory boot config already has the HUB75 Half Scan bus (upstream type 65) for one 64x64 panel; the panel is half scan, not quarter. The MM-specific dropdown label "Hub75Matrix 64x64" (MM type 103) no longer exists in the upstream-16.0.1-based build, so this instruction is both unnecessary and un-followable. |
| LED Settings: set Chain Length to 1 | FIXED AS DEFAULT | Factory default is chain length 1. |
| LED Settings: uncheck "enable automatic brightness limiter" | FIXED AS DEFAULT | Factory default has the automatic brightness limiter OFF. |
| LED Settings: click Save | FIXED AS DEFAULT | With all LED Preferences values factory-correct there is nothing to save. |
| 2D Settings: Config > 2D Configuration, select 2D Matrix and the Basic layout radio button | FIXED AS DEFAULT | Factory default is a 2D matrix, 1x 64x64, already configured. |
| 2D Settings: set Panel Dimensions to 64 x 64 and click Save | FIXED AS DEFAULT | Factory default 2D matrix is already 64x64 with one panel; no save needed. |
| AudioReactive: check Enabled (rev6 PCB with microphone addon only) | CANNOT FIX | Depends on optional physical hardware (mic addon, rev6+ only); firmware deliberately ships AudioReactive compiled in but disabled, so an owner who installs the addon flips this one toggle. This is the only remaining real configuration step and the page should keep it (with its rev4-incompatibility warning). |
| AudioReactive: select Generic I2S for Type | FIXED AS DEFAULT | Type Generic I2S is preconfigured in the factory defaults. |
| AudioReactive: select pins 10 (I2S SD), 12 (I2S WS), 11 (I2S SCK) | FIXED AS DEFAULT | Pins SD 10 / WS 12 / SCK 11 are preconfigured in the factory defaults. |
| AudioReactive: set Mode to Off and click Save | FIXED AS DEFAULT | Sync mode Off is preconfigured; the only click a mic-addon owner still makes is the enable toggle plus its Save. |

Copy updates needed:
- Dropdown label "Hub75Matrix 64x64" is a WLED-MM-only type (MM type 103, plain panel) that does not exist in the new upstream-16.0.1-based build; any retained screenshot/text must show "HUB75 Half Scan" (type 65), and remember the panel is half scan, not quarter scan.
- Friendly Name section: example/expected value should reflect the new factory default server description "Apollo M-1" (page currently suggests entering "Apollo LED Matrix" as if the field were blank).
- Hostname section: device now ships with unique hostname apollo-led-matrix-xxxxxx (last 6 MAC hex chars); the example http://apollo-led-matrix.local needs the suffix or a rewrite to 'find your device's unique .local name'. Hostname-rule callouts only matter if the user renames it.
- Page framing: retitle/rewrite from 'settings you must enter' to 'factory defaults reference + optional personalization', keeping only the AudioReactive Enabled toggle (rev6 + mic addon) as an actual step; pins, type, and sync mode are preconfigured.
- Add migration note: OTA update from the old WLED-MM firmware preserves existing settings (migration shim converts old HUB75 config); a full-erase reflash restores all factory defaults so this page's manual reconfiguration is no longer needed after reflash.
- Linked prerequisite page /products/m1/troubleshooting/m1-reflash/ very likely contains old WLED-MM install URLs/binaries and should be triaged separately.
- No references to WLED-MM, MoonModules, Pixel Magic, Pixelforge, AP SSIDs/passwords, or install URLs appear on this page itself; if first-connect instructions are ever added here, use setup AP "Apollo M-1-xxxxxx" with password wled1234 (not an open AP).
- Ensure the rewritten page continues to coexist with (and link to, not hide) the separate ESPHome firmware option for the M-1.

Fact challenge field: No premise contradicted by the page. Minor internal tension noted in FACT 1 itself: it calls WLED-MM types 101-104 "plain panels" yet maps the wiki-selected type 103 to upstream TYPE_HUB75MATRIX_HS = 65 (half scan); the page never states a scan type, so nothing on it conflicts, I proceeded on FACT 1 as given (panel is half scan, not quarter)."

## multiple-panels
https://wiki.apolloautomation.com/products/m1/setup/m1-multiple-panels/

Multiple-panel setup guide (2-4 panels) for the M-1. Covers hardware assembly (face-down arrangement, JOUT-to-JIN ribbon cables, Matrix Power Modules on panels 2-4, USB-C power), then WLED software config (Chain Length 2/3/4 in LED Preferences, Panel Dimensions 128x64/192x64/256x64 in 2D Configuration, reboot via Info menu), then optional 4-segment layouts per panel count with a warning to save segments as a Preset. Page loaded fine (no 404). It never mentions WLED-MM, MoonModules, Pixel Magic, Pixelforge, an AP SSID/password, or install URLs; the only identity reference is the generic "http://your-hostname-here.local" plus a link to a find-your-IP/hostname troubleshooting page. Because this whole page documents the optional multi-panel upgrade path (factory default is 1 panel, 64x64), no step here becomes unnecessary under the new defaults.

| Step | Classification | Reason |
|---|---|---|
| Arrange 2/3/4 panels face-down with the controller panel on the left | CANNOT FIX | Physical assembly; firmware cannot position hardware. |
| Connect ribbon cable(s) from JOUT port to JIN port, chaining panels sequentially (1→2, 2→3, 3→4) | CANNOT FIX | Physical cabling; firmware cannot remove hardware interconnect. |
| Press Matrix Power Module onto the 4-pin header of each added panel (USB-C facing right) | CANNOT FIX | Physical assembly of the power accessory. |
| Connect USB-C power cables to the controller and to every installed Power Module | CANNOT FIX | Physical power wiring; each panel needs its own supply. |
| Navigate to http://your-hostname-here.local or the device IP in a browser | CANNOT FIX | Accessing the web UI is inherent to any configuration and depends on the customer's network; however the hostname copy should be updated to the new apollo-led-matrix-xxxxxx.local format (see copy updates). |
| Config → LED Preferences → set Chain Length to 2 / 3 / 4 | NOT A DEFAULT | Factory default is chain length 1 (single panel). How many panels the customer chained is a purchase/user choice the firmware cannot know; this page exists precisely to document that choice. |
| Config → 2D Configuration → set Panel Dimensions to 128x64 / 192x64 / 256x64 | NOT A DEFAULT | Factory default 2D matrix is 1x 64x64; wider dimensions only apply when the user has added panels, which firmware cannot detect. (Field naming needs verification against upstream 16.0.1 UI, see copy updates.) |
| Reboot WLED via Info → Reboot WLED, confirm when prompted | CANNOT FIX | The reboot applies a user-initiated bus/2D reconfiguration; since the multi-panel change itself is a user choice, defaults cannot eliminate the accompanying reboot. |
| Create Segment 0 with Stop X 128/192/256 (per panel count) and Stop Y 16 | NOT A DEFAULT | Segment layout is customer taste (splitting the display into rows) and depends on the chosen panel count. |
| Create Segment 1 with Start Y 16, Stop Y 32 | NOT A DEFAULT | Optional user layout choice. |
| Create Segment 2 with Start Y 32, Stop Y 48 | NOT A DEFAULT | Optional user layout choice. |
| Create Segment 3 with Start Y 48, Stop Y 64 | NOT A DEFAULT | Optional user layout choice. |
| Save the segment configuration as a Preset (+ Preset button, enter name, save) | NOT A DEFAULT | Persisting a user-created segment layout is inherently tied to the user's own segment choices; firmware cannot pre-save a layout it cannot predict. |

Copy updates needed:
- Hostname guidance: the page says to visit 'http://your-hostname-here.local'. Update this (and verify the linked 'find your IP or hostname' troubleshooting page) to reflect the new mDNS format apollo-led-matrix-xxxxxx.local (last 6 MAC hex chars).
- UI field names come from the WLED-MM interface: 'Config → 2D Configuration' with a 'Panel Dimensions' field may not match upstream WLED 16.0.1, whose 2D setup uses number of panels plus per-panel width/height/orientation. Verify the exact menu path and field names on the new firmware and update text/screenshots.
- Verify whether 'Chain Length' still appears under LED Preferences with that exact label for the upstream HUB75 Half Scan bus (type 65), and whether changing it auto-adjusts the 2D matrix size; adjust step wording accordingly.
- Re-verify the segment Stop X totals (128/192/256) against the upstream HUB75-HS 2D mapping after migration; values should still hold for 64x64 half-scan panels chained horizontally but should be confirmed on hardware.
- No WLED-MM, MoonModules, Pixel Magic, Pixelforge, AP SSID/password, or install-URL references exist on this page, so no copy changes are needed for those; the page also makes no promises that the new defaults (AP password wled1234, Apollo M-1 naming, brightness limiter off) would contradict.

Fact challenge field: No premise challenged: nothing on this page contradicts the stated new-firmware defaults. The page never names a panel type or scan mode, so it neither supports nor conflicts with the half-scan (type 65) factory bus.

## segments
https://wiki.apolloautomation.com/products/m1/setup/m1-segments/

Customization guide for splitting the M-1's 64x64 matrix into four horizontal segments (16 rows each) so it can show four independent lines of scrolling text. Steps: open the WLED UI, edit Segment 0 (Stop Y 16), add Segments 1-3 with Start/Stop Y of 16/32, 32/48, 48/64, test with the Scrolling Text effect, then save everything to a Preset (segments are lost on reboot otherwise). No mentions of WLED-MM, MoonModules, Pixel Magic, Pixelforge, access points, SSIDs/passwords, hostnames, or install URLs. The page assumes a 64x64 2D matrix, which matches the new factory default (1x 64x64), so its coordinates stay correct under the new firmware.

| Step | Classification | Reason |
|---|---|---|
| Navigate to the main page of your WLED instance in a browser or the WLED-native app | CANNOT FIX | Accessing the device UI is inherent to any customization and depends on the customer's network; firmware cannot remove it. (Copy could be improved by mentioning the new http://apollo-led-matrix-xxxxxx.local hostname.) |
| Segment 0: click the segment and set Stop Y to 16 | NOT A DEFAULT | Segmenting the display is a user-taste layout choice; factory default is a single full-matrix segment with Solid orange, and shipping a pre-segmented display is not in the new defaults nor desirable for all users. |
| Click Add segment, create Segment 1, set Start Y 16 / Stop Y 32 | NOT A DEFAULT | User choice of how many zones and where the boundaries fall; not part of factory defaults. |
| Click Add segment, create Segment 2, set Start Y 32 / Stop Y 48 | NOT A DEFAULT | Same as above, genuine user layout choice. |
| Click Add segment, create Segment 3, set Start Y 48 / Stop Y 64 | NOT A DEFAULT | Same as above, genuine user layout choice. |
| Change effect to Scrolling Text to test each segment | NOT A DEFAULT | Effect selection is customer taste; the factory default effect is intentionally Solid orange. Scrolling Text exists in upstream WLED 16.x, so the instruction stays valid. |
| Edit each segment's name to the desired text | NOT A DEFAULT | The displayed text is inherently the customer's content choice. |
| Click + Preset, type a name, click Save to persist the segment layout | CANNOT FIX | WLED (upstream and MM alike) only persists user-defined segments via presets; firmware defaults cannot pre-save a layout the customer defines themselves, so this step must remain documented. |

Copy updates needed:
- Optional (not required): where the page says 'Navigate to the main page of your WLED instance', add the new default hostname hint http://apollo-led-matrix-xxxxxx.local (xxxxxx = last 6 MAC hex chars) to help users find the device.
- No other updates needed: the page contains no WLED-MM/MoonModules/Pixel Magic/Pixelforge references, no AP/SSID/password text, no hostnames, and no install URLs; its 64x64 Y-coordinates match the new factory default 2D matrix (1x 64x64), and its Segment 0 / Add segment / Start-Stop Y / Scrolling Text / Preset workflow is unchanged in upstream WLED 16.x.

## pinout-guide
https://wiki.apolloautomation.com/products/m1/setup/m1-pinout-guide/

Short pinout reference page for the M-1. It contains one table (column header oddly labeled "LED-1 PCB") listing: GPIO_0 = touch button, "HUB75Matrix 64x64" as the LED data output (no per-signal HUB75 pins given), and I2S microphone pins SD=GPIO_16, WS=GPIO_6, SCK=GPIO_7. One instruction note: "If you have re-flashed your device with other WLED firmware, please fill in the gpio numbers above in WLED... The audio settings go in the AudioReactive settings." It then points to the matrix settings guide for the remaining configuration. Page did not 404. No mention of MoonModules, Pixel Magic, Pixelforge, AP SSIDs/passwords, hostnames, or install URLs on this page.

| Step | Classification | Reason |
|---|---|---|
| Select "HUB75Matrix 64x64" as the LED data output in WLED LED settings (after re-flashing with other WLED firmware) | FIXED AS DEFAULT | New factory defaults preconfigure the HUB75 Half Scan bus (type 65), one 64x64 panel, chain 1, 2D matrix 1x 64x64; a full-erase install of the new firmware restores this and OTA preserves migrated settings. Manual selection only remains relevant if the user flashes generic non-Apollo WLED, and even then the dropdown label has changed (upstream calls it "HUB75 Half Scan", not "HUB75Matrix 64x64"). |
| Enter GPIO 0 as the button pin (touch button) in WLED settings | FIXED AS DEFAULT | Factory build defines BTNPIN=0 (platformio_override.ini line 33) and the new firmware's factory defaults carry the full pin configuration, so no manual entry is needed on a factory unit. (The new-defaults brief given to me does not explicitly enumerate BTNPIN=0, worth a one-line verification on the m1-wled-update branch.) |
| Enter I2S SD = GPIO_16 in AudioReactive settings | FIXED AS DEFAULT | New firmware ships AudioReactive compiled in and preconfigured (Generic I2S, SD 10 / WS 12 / SCK 11, sync Off); a mic-addon owner only flips the enable toggle. Additionally the published value is WRONG: factory firmware source sets I2S_SDPIN=10, and GPIO 16 is actually the HUB75 'A' address line in the MOONHUB map, entering 16 as SD would conflict with the panel. |
| Enter I2S WS = GPIO_6 in AudioReactive settings | FIXED AS DEFAULT | Preconfigured by new defaults (WS = 12). Published value GPIO_6 is wrong versus the factory firmware source (I2S_WSPIN=12); GPIO 6 is the HUB75 B1 line in the MOONHUB map. |
| Enter I2S SCK = GPIO_7 in AudioReactive settings | FIXED AS DEFAULT | Preconfigured by new defaults (SCK = 11). Published value GPIO_7 is wrong versus the factory firmware source (I2S_CKPIN=11); GPIO 7 is the HUB75 R2 line in the MOONHUB map. |

Copy updates needed:
- Microphone pins are wrong on the page: it publishes SD=GPIO_16, WS=GPIO_6, SCK=GPIO_7, but the factory firmware source (/Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1/platformio_override.ini line 34) and the new firmware defaults both use SD=10, SCK=11, WS=12. Worse, 16/6/7 are HUB75 signals (A, B1, R2) in the MOONHUB map, so following the page would break the panel.
- Table column header reads "LED-1 PCB", appears copy-pasted from a different Apollo product page; should say M-1.
- "HUB75Matrix 64x64" is WLED-MM (MoonModules) naming (type 103). The new upstream-16.0.1-based firmware exposes this as "HUB75 Half Scan" (type 65); the dropdown name in the instructions must be updated.
- The page gives NO per-signal HUB75 pin map at all. If the page is meant to help users who re-flash with generic WLED, it should publish the full MOONHUB map: R1=1, G1=5, B1=6, R2=7, G2=13, B2=9, A=16, B=48, C=47, D=21, E=38, LAT=8, OE=4, CLK=18 (verified against /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1/wled00/bus_manager.cpp, MOONHUB_S3_PINOUT block at line 749).
- The re-flash framing ("if you have re-flashed your device with other WLED firmware, fill in the gpio numbers above") should be rewritten: OTA to the new Apollo firmware preserves settings via the migration shim, and a full-erase install restores all factory defaults with every pin preconfigured, manual pin entry is only needed for non-Apollo firmware. The rewrite should also continue to acknowledge the separate ESPHome firmware option.
- Minor: the old factory build sets DEFAULT_LED_TYPE=101 while the page directs users to select the 64x64 variant (type 103), reconcile when updating to the new type-65 naming.

Fact challenge field: No challenge to FACT 1, but the E-line duty result is nuanced: the published page contains NO per-signal HUB75 pin map whatsoever (no R1/G1/B1/R2/G2/B2/A/B/C/D/E/LAT/OE/CLK rows), so E (GPIO 38) is neither landed nor marked unused ON THE PAGE, the entire signal map is simply absent from the wiki. The factory firmware source in this repo, however, confirms E=38 is configured and driven: /Users/justinapollo/Code/ApolloAutomation/WLED-MM-M1/wled00/bus_manager.cpp line ~752 sets mxconfig.gpio = { 1, 5, 6, 7, 13, 9, 16, 48, 47, 21, 38, 8, 4, 18 }, exactly matching the provided MOONHUB map including E=38. Since shipping units run this firmware and display correctly on 64x64 panels, E is evidently landed on the connector; no escalation of FACT 1 is warranted. Separate data-quality flag: the page's mic pins (16/6/7) collide with HUB75 signals and contradict the firmware source (10/11/12), a documentation error, not a premise error.

## microphone-addon
https://wiki.apolloautomation.com/products/m1/addons/adding-microphone-to-m-1/

Guide for installing the microphone addon on the M-1 LED Matrix. Covers: unplugging and positioning the unit, physically inserting the mic module (label facing right, GND bottom right), then configuring firmware via Config → AudioReactive: check Enabled, select "Generic I2S" type, set pins I2S SD "10 digitalmic" / WS "12 digitalmic A5" / SCK "11 digitalmic", Save, then scroll to the bottom and set (sync) Mode to Off and Save. Page includes screenshots of the settings UI. No mentions of WLED-MM, MoonModules, Pixel Magic, Pixelforge, AP SSIDs/passwords, hostnames, IP addresses, or install/flash URLs; no prerequisites, warnings, or links to other pages. Page loaded fine (no 404).

| Step | Classification | Reason |
|---|---|---|
| Unplug the M-1 from power and set the matrix face down with the controller PCB facing you | CANNOT FIX | Physical assembly step; firmware cannot power down or position the unit. |
| Insert the microphone addon with the microphone label facing right and the GND pin at the bottom right | CANNOT FIX | Physical assembly step; orientation of the mic module is hardware, not firmware. |
| Navigate to Config → AudioReactive | CANNOT FIX | Still required to reach the one remaining enable toggle; firmware cannot know the optional mic was installed, so the user must open this page once. |
| Check 'Enabled' (AudioReactive usermod enable checkbox) | CANNOT FIX | AudioReactive is deliberately compiled in but disabled by default because factory units ship without the mic; whether the addon is installed depends on the customer, so this single toggle must remain. This is the intended one-toggle experience for rev6 owners. |
| Select 'Generic I2S' for the Type | FIXED AS DEFAULT | New firmware preconfigures AudioReactive type as Generic I2S. |
| Set Pin I2S SD to '10 digitalmic' | FIXED AS DEFAULT | New firmware preconfigures SD = 10. |
| Set Pin I2S WS to '12 digitalmic A5' | FIXED AS DEFAULT | New firmware preconfigures WS = 12. |
| Set Pin I2S SCK to '11 digitalmic' | FIXED AS DEFAULT | New firmware preconfigures SCK = 11. |
| Click Save after configuration | CANNOT FIX | One Save is still required to persist the Enabled checkbox on the same settings page; firmware cannot apply a user toggle without saving. |
| Scroll to the bottom of AudioReactive settings, set Mode to Off, and click Save | FIXED AS DEFAULT | This is the audio sync mode at the bottom of the AudioReactive page; new firmware ships with sync mode Off, so this entire step (including its second Save) is unnecessary. |

Copy updates needed:
- Rewrite the configuration section to the new one-toggle flow: open Config → AudioReactive, check Enabled, click Save. State that Type (Generic I2S), pins (SD 10 / WS 12 / SCK 11), and sync Mode (Off) are preconfigured at the factory.
- The quoted pin dropdown labels '10 digitalmic', '12 digitalmic A5', '11 digitalmic' are WLED-MM-specific pin annotations; upstream WLED 16.0.1 renders pin fields differently, so if any manual-configuration fallback text is kept, these exact strings must be updated.
- Screenshots of the AudioReactive settings page show the old WLED-MM UI; re-capture them on the new upstream-16.0.1-based firmware UI.
- Consider adding a note (or collapsed fallback section) for units OTA-updated from the old WLED-MM firmware: the migration preserves existing customer settings, so verify whether the AudioReactive pin/type defaults are also seeded on OTA, if not, OTA-upgraded units may still need the manual pin/type steps that factory units no longer do.
- Consider a note that this guide applies to the WLED firmware; M-1 units running the separate ESPHome firmware option have a different mic-enable procedure, and the page currently does not distinguish them.

Fact challenge field: No premise challenged. Nothing on this page contradicts FACT 1 or the stated new-default configuration; the page's pin values (SD 10, WS 12, SCK 11) and Generic I2S type exactly match the new firmware's preconfigured AudioReactive defaults, and the panel-scan question does not arise on this page.

## reflash
https://wiki.apolloautomation.com/products/m1/troubleshooting/m1-reflash/

"Factory Re-Flash M-1" troubleshooting page for recovering an unresponsive M-1. Prerequisites: a power+data USB cable and a Chromium-based browser. Steps: hold the boot (left) button while plugging in USB-C to enter boot mode, open the "Apollo M-1 Installer" (linked to https://apolloautomation.github.io/WLED-MM-M1/), click Connect, pick the COM port, click "Install M-1", confirm "Install", wait for "Installation complete!", then power-cycle the device ("Power cycle your device before doing anything else!", it stays in boot mode until power is removed). Ends by handing off to the Getting Started guide to set the device up as a new device. SPECIAL DUTY findings: the only install URL on the page is https://apolloautomation.github.io/WLED-MM-M1/ (old WLED-MM-M1 repo GitHub Pages installer); the page offers ONLY the WLED installer, ESPHome firmware is not mentioned or offered anywhere on this page, so the "both firmwares stay visible" requirement is not currently met here and must not be regressed further by the migration. No AP SSID/password or hostname is mentioned on the page.

| Step | Classification | Reason |
|---|---|---|
| Prerequisite: use a USB cable that supports power and data | CANNOT FIX | Physical hardware requirement for serial flashing; firmware cannot remove it. |
| Prerequisite: use Chrome, Edge, or another Chromium-based browser | CANNOT FIX | Web Serial API is only available in Chromium browsers; outside firmware control. |
| Connect the device to your computer with a USB cable | CANNOT FIX | Physical action required for any serial reflash of an unresponsive unit. |
| Enter boot mode: press and hold the boot (left) button while connecting USB-C, then release | CANNOT FIX | ESP32 ROM download mode is entered via the strapping-pin button; this is hardware/ROM behavior, not firmware, and the target device is by definition unresponsive, so firmware on it cannot help. |
| Navigate to the Apollo M-1 Installer and click the connect button | CANNOT FIX | An external web flasher is inherently required to recover a bricked device; firmware cannot reflash itself. (The link target itself needs a copy update, see copy_updates_needed.) |
| Select the open COM port from the dropdown and click Connect | CANNOT FIX | Browser security requires the user to pick the serial port; cannot be automated by firmware or the installer. |
| Click "Install M-1" on the installer page | CANNOT FIX | User action in the web flasher UI; required to start flashing. |
| Click "Install" in the confirmation dialog | CANNOT FIX | ESP Web Tools confirmation dialog; part of the flashing tool, not the device firmware. |
| Wait for "Installation complete!", click Next, and close the browser | CANNOT FIX | Inherent to the web-flash process. |
| Power cycle the device after flashing (it remains in boot mode until power is removed) | CANNOT FIX | The chip was manually strapped into ROM download mode; exiting it requires a reset/power cycle, which firmware cannot perform on its own before it is even running. |
| After power cycling, follow the Getting Started guide to set up the M-1 as a new device | CANNOT FIX | A full-erase install restores factory defaults, so WiFi provisioning (customer WiFi credentials) is still required. However, the new defaults make the downstream setup much shorter: the referenced Getting Started page's HUB75/2D/AudioReactive configuration steps become FIXED_AS_DEFAULT and that page needs its own triage. |

Copy updates needed:
- Install URL: the "Apollo M-1 Installer" link points to https://apolloautomation.github.io/WLED-MM-M1/, the old WLED-MM-M1 (MoonModules-based) repo's GitHub Pages installer. It must either be repointed to the new WLED-M1 (upstream 16.0.1) installer or the new installer must be published at that same URL; the visible repo/path name "WLED-MM-M1" is itself a WLED-MM reference that may warrant renaming.
- ESPHome option missing: this reflash page offers ONLY the WLED installer and never mentions the separate ESPHome firmware option for the M-1. Per the requirement that both firmwares stay visible, the page should present both install paths (WLED installer and ESPHome installer) or link to a chooser page.
- Post-flash expectations: after a full-erase reflash the unit now boots showing solid orange at brightness 128 and broadcasts setup AP "Apollo M-1-xxxxxx" with password wled1234 (no longer an open/passwordless AP, if the old firmware's AP was open), with mDNS hostname apollo-led-matrix-xxxxxx and server description "Apollo M-1". The page (or the Getting Started page it hands off to) should state these so users know what to look for and that the AP now requires the password wled1234.
- Data-loss warning: the page should note that a factory reflash (full erase) wipes all customer settings and restores factory defaults, whereas a normal OTA update from the old WLED-MM firmware preserves settings via the migration shim, users troubleshooting a merely misconfigured (not bricked) unit may prefer OTA.
- Button label check: verify the new installer page still labels the flash button "Install M-1" and shows "Installation complete!"; update the transcribed button/dialog text on this page if the new ESP Web Tools manifest changes any labels.

## boot-mode
https://wiki.apolloautomation.com/products/m1/troubleshooting/m1-boot-mode/

A short physical-procedure troubleshooting page explaining how to force the M-1 into ESP32 boot (download) mode for firmware reflashing: connect a data-capable USB cable to the computer, press and hold the boot button (left button) while plugging the USB-C cable into the M-1, then release. It ends with a link to the reflash guide (https://wiki.apolloautomation.com/products/m1/troubleshooting/m1-reflash/). The page contains no WLED/WLED-MM/MoonModules/ESPHome references, no settings values, no AP/SSID/hostname/password mentions, and no install URLs, it is firmware-agnostic recovery documentation.

| Step | Classification | Reason |
|---|---|---|
| Prepare a USB cable that supports both power and data, connected to your computer | CANNOT FIX | Physical hardware requirement for USB flashing; no firmware default can remove the need for a data-capable cable. |
| Press and hold the boot button (left button on the device) | CANNOT FIX | Entering the ESP32 ROM bootloader is a hardware-level procedure (GPIO0 strap at power-on); firmware cannot eliminate it, and it remains the recovery path when firmware is unbootable. It is also still required for the full-erase factory install of the new firmware. |
| While holding the boot button, connect the USB-C cable to the M-1's USB-C port | CANNOT FIX | Same hardware boot-strap procedure, the button must be held during power-up/enumeration; firmware defaults cannot change ROM bootloader behavior. |
| Release the boot button once connected | CANNOT FIX | Part of the same physical boot-mode entry sequence dictated by ESP32 hardware, not by firmware configuration. |
| Proceed to the reflash guide to reflash the firmware | CANNOT FIX | This is a recovery/reflash workflow pointer, not a configuration step; the ability to reflash over USB must remain regardless of factory defaults (and is how a full-erase install of the new firmware is performed). |

Copy updates needed:
- No copy updates strictly required on this page itself: it never names WLED-MM, MoonModules, Pixel Magic, Pixelforge, an AP/SSID/hostname, or an install URL, and promises nothing that the new defaults change.
- The linked reflash guide (https://wiki.apolloautomation.com/products/m1/troubleshooting/m1-reflash/) is where firmware names and install URLs will live, that page should be triaged separately for WLED-MM-to-new-firmware copy updates (e.g., which installer URL to use, note that a full-erase install restores factory defaults while OTA preserves settings, and that the ESPHome firmware option must remain visible).
- Optional (nice-to-have, not required): this page could add one sentence noting that boot mode is only needed for USB/full-erase reflashing, since OTA updates from the old WLED-MM firmware preserve settings and need no boot mode.

Fact challenge field: No premise challenged, the page contains nothing about panel type, scan rate, WLED configuration, AP credentials, or firmware identity, so none of the stated new-firmware defaults (HUB75 Half Scan type 65, 64x64, AP "Apollo M-1-xxxxxx"/wled1234, hostname apollo-led-matrix-xxxxxx, AudioReactive pins SD 10/WS 12/SCK 11, ABL off, brightness 128, solid orange) are contradicted or confirmed by this page.

## find-ip-hostname
https://wiki.apolloautomation.com/products/m1/troubleshooting/m1-find-ip-address-and-hostname/

Troubleshooting page teaching users to find their M-1's IP address and hostname via the WLED Native mobile app (iOS/Android): connect to WiFi, let the app auto-detect the device, open Config > WiFi Setup to read the .local hostname and IP, optionally rename the hostname, browse to http://ip or http://hostname.local, and set a friendly Server description. Contains a prominent warning not to accept the firmware update badge in the app ("DO NOT DO THIS, IT WILL BREAK YOUR CONFIG") and links to the create-logo-image wiki page. Page loaded fine (no 404).

| Step | Classification | Reason |
|---|---|---|
| Download the WLED Native app for iOS and Android | CANNOT FIX | App installation happens on the customer's phone; firmware cannot install a mobile app. The app remains a valid discovery tool for the new firmware since it still advertises the standard WLED mDNS service. |
| Make sure the M-1 is already connected to the same Wi-Fi network as your PC and phone | CANNOT FIX | Joining the customer's WiFi depends on customer network credentials; firmware cannot know them in advance. |
| Select the auto-detected M-1 in the app, then click the Config tab in the top right corner | CANNOT FIX | This is app UI navigation to look up device info; firmware cannot eliminate the need to navigate a third-party app. Auto-detection continues to work because the new firmware still advertises via mDNS (hostname apollo-led-matrix-xxxxxx). |
| Select WiFi Setup and read the hostname in the box ending in .local, with the IP shown below it | CANNOT FIX | Reading the assigned IP/hostname is inherently an information-lookup step. The new firmware improves it (predictable hostname apollo-led-matrix-xxxxxx.local derived from the last 6 MAC hex chars) but cannot know the DHCP-assigned IP ahead of time. |
| Optionally change the hostname (letters, numbers, dashes only) and click Save and Connect | NOT A DEFAULT | Renaming the hostname is a genuine customer-taste choice. The new default (apollo-led-matrix-xxxxxx) is already meaningful, so the page should present this as purely optional. |
| Access the device from a browser at http://the-ip-address-here or http://the-hostname-you-entered.local | CANNOT FIX | Opening a browser and entering the address is a user action firmware cannot perform. Copy can be simplified to the default http://apollo-led-matrix-xxxxxx.local pattern. |
| Edit the User Interface settings section under Server description with a friendly name for your device | FIXED AS DEFAULT | The new firmware ships with server description "Apollo M-1" out of the box, so factory units already show a friendly name in the app and web UI; this step becomes optional personalization only. |

Copy updates needed:
- The firmware-update warning ("WARNING ~ DO NOT UPDATE IT ~ WARNING ... DO NOT DO THIS, IT WILL BREAK YOUR CONFIG") needs revision: on the new firmware, OTA from the old WLED-MM build preserves customer settings via the migration shim, so the blanket claim is stale. However, the update badge in WLED Native points at generic upstream WLED release binaries, not Apollo's build, so the page should still steer users to Apollo-provided updates rather than the in-app badge, reword rather than delete.
- Step 4 / hostname section should state the new factory default hostname pattern apollo-led-matrix-xxxxxx.local (xxxxxx = last 6 hex chars of the MAC), so users can recognize their device in the app and even try the .local address directly.
- Step 6 URL example can mention http://apollo-led-matrix-xxxxxx.local as the default address instead of only the generic placeholder.
- Step 7 (Server description) should say the factory default is already "Apollo M-1" and renaming is optional personalization.
- The page assumes WLED firmware throughout (WLED Native app); consider a one-line note that units flashed with the separate ESPHome firmware will not appear in WLED Native and are discovered via Home Assistant/ESPHome instead, so the ESPHome path is not hidden.
- No references to WLED-MM, MoonModules, Pixel Magic, Pixelforge, install URLs, or an open/passwordless AP were found on this page, so no copy changes needed on those fronts; the "WLED Native" app references remain correct for the new firmware.

Fact challenge field: No premise challenged. Nothing on this page contradicts FACT 1 or the stated new-firmware defaults; the page never mentions panel scan type, AP SSIDs, or hostnames explicitly, so no conflicts arose.

## examples
https://wiki.apolloautomation.com/products/m1/examples/ (404); covered: https://wiki.apolloautomation.com/products/m1/examples/add-gifs-to-wled/, https://wiki.apolloautomation.com/products/m1/examples/create-gif/, https://wiki.apolloautomation.com/products/m1/examples/create-logo-image/, https://wiki.apolloautomation.com/products/m1/examples/scrolling-text/, https://wiki.apolloautomation.com/products/m1/examples/qr-code-generator/, https://wiki.apolloautomation.com/products/m1/examples/share-data-from-home-assistant/, https://wiki.apolloautomation.com/products/m1/examples/media-proxy/, https://wiki.apolloautomation.com/products/m1/examples/sendspin/

The examples index URL (/products/m1/examples/ with or without trailing slash) returns HTTP 404, there is no standalone index page; examples are only reachable via the wiki's side navigation. Per the sitemap, the main M-1 examples section contains exactly 8 pages, all fetched and triaged here: (1) add-gifs-to-wled, download/resize a 64x64 GIF, upload via Config > File System, apply the WLED-MM "Image" effect with filename as segment name, save preset; titled "Adding GIFs to M-1 on WLED-MM Firmware", requires 14.5.1+. (2) create-gif, similar GIF workflow with prerequisites "Rev 4 or Rev 6", "firmware 14.5.1 or later", and "correct LED matrix settings configured" (the last is now a factory default). (3) create-logo-image, uses the PixelMagicTool (pxmagic.htm from GitHub) to push image presets to the device by hostname (example shown: apollo-led-matrix.local) or IP; includes brightness slider, compression toggle for oversized presets, and three pre-made JSON preset codes pasted with "Use current state" unchecked. (4) scrolling-text, select Scrolling Text effect, set text via segment name, tune speed/Y offset/trail/font-size (222 suggested) sliders and Fx/Bg/Gr colors, save preset. (5) qr-code-generator, wiki-hosted QR generator (WiFi/Text/URL/vCard), download image, optionally convert to GIF and upload "for WLED-MM firmware version 14.5.1 or higher". (6) share-data-from-home-assistant, HA-side JSON API workflow: prerequisite four pre-configured segments, Studio Code Server, YAML generator into configuration.yaml, config check, test via Developer Tools, per-minute automation calling RESTful command matrix_all_segments. (7) media-proxy and (8) sendspin, both ESPHome-firmware pages (Music Assistant / media streaming); sendspin explicitly contrasts against "the stock WLED-MM firmware". A parallel Homey mirror of six of these pages exists under /homey/products/m1/examples/ (out of scope here but will need the same copy edits). As expected for example pages, almost everything is NOT_A_DEFAULT or CANNOT_FIX; the one genuine FIXED_AS_DEFAULT is create-gif's "correct LED matrix settings configured" prerequisite.

| Step | Classification | Reason |
|---|---|---|
| [add-gifs-to-wled] Download a GIF (e.g. from giphy.com) | NOT A DEFAULT | Content choice is the whole point of the example; firmware cannot pick the user's GIF. |
| [add-gifs-to-wled] Resize the GIF to 64x64 pixels using ezgif.com | CANNOT FIX | External content preparation dictated by the 64x64 panel; firmware cannot resize files the user hasn't uploaded yet. |
| [add-gifs-to-wled] Rename the file to something simple (e.g. cat-dance) | CANNOT FIX | Filename must match the segment name the user will type; user-content workflow step firmware cannot remove. |
| [add-gifs-to-wled] Open http://<your-m1-ip-address> or http://<your-device-name>.local in a browser | CANNOT FIX | Depends on customer network/IP; but the hostname example should be updated to the new apollo-led-matrix-xxxxxx.local pattern. |
| [add-gifs-to-wled] Config > File System > browse, select GIF, Save (upload) | CANNOT FIX | User content upload; firmware cannot preload the customer's GIF. |
| [add-gifs-to-wled] Select the 'image' effect and set Segment 0's name to the exact filename (cat-dance.gif) | NOT A DEFAULT | Genuine user choice of effect and file; keep documenting. Verify the Image/GIF effect exists in the new upstream-16.0.1-based build (it is MM 14.5.1 functionality). |
| [add-gifs-to-wled] Click + Preset, name it, Save | NOT A DEFAULT | User choice to persist their configuration. |
| [add-gifs-to-wled] Optional: Config > LED Preferences > Apply Preset <n> > Save (boot preset) | NOT A DEFAULT | User choice; note the factory boot default is now Solid orange, which this optional step legitimately overrides. |
| [create-gif] Prerequisite: correct LED matrix settings configured | FIXED AS DEFAULT | Factory firmware now boots with HUB75 Half Scan (type 65), one 64x64 panel, chain 1, 2D matrix 1x 64x64 preconfigured; no matrix setup needed on a factory unit. Prerequisite line should be removed or reworded to 'factory default'. |
| [create-gif] Prerequisite: firmware version 14.5.1 or later | NOT A DEFAULT | Version gate is a doc statement the user checks, not removable by defaults; but the version string is now wrong (new firmware is upstream WLED 16.0.1 based), copy update. |
| [create-gif] Connect the M-1 to your Wi-Fi via the device's config interface | CANNOT FIX | Depends on customer WiFi credentials; firmware cannot know them. Copy should reflect the new setup AP 'Apollo M-1-xxxxxx' with password wled1234. |
| [create-gif] Find the device IP via your router or the WLED Native app | CANNOT FIX | Network-dependent discovery; though the new unique mDNS hostname apollo-led-matrix-xxxxxx.local makes this easier and should be documented as the primary method. |
| [create-gif] Resize GIF to 64x64 on ezgif.com and save | CANNOT FIX | External content preparation required by panel geometry. |
| [create-gif] Upload the GIF via the dashboard File System page | CANNOT FIX | User content upload. |
| [create-gif] Select the Image effect and rename segment to match the GIF filename exactly | NOT A DEFAULT | User choice of content; verify Image effect availability in the new firmware. |
| [create-gif] Create and save a preset (optionally for boot) | NOT A DEFAULT | User choice. |
| [create-logo-image] Download pxmagic.htm (PixelMagicTool) from GitHub via 'Download raw file' | NOT A DEFAULT | External community tool for user-created content; keep documenting. Pixel Magic reference, flag for copy review and compatibility check against upstream 16.0.1 presets. |
| [create-logo-image] Open pxmagic.htm in a web browser | NOT A DEFAULT | Part of using the external tool. |
| [create-logo-image] Enter the device hostname (e.g. apollo-led-matrix.local) or IP | CANNOT FIX | Depends on customer network; the example hostname must be updated to apollo-led-matrix-xxxxxx.local (unique 6-hex-char MAC suffix). |
| [create-logo-image] Assign a preset name (e.g. 'Apollo Logo') | NOT A DEFAULT | User naming choice. |
| [create-logo-image] Adjust brightness slider (e.g. 255 for full) | NOT A DEFAULT | Customer taste; note factory default brightness is now 128, unrelated to this per-preset tool slider. |
| [create-logo-image] Select the image file via file picker and click Generate | NOT A DEFAULT | User content choice. |
| [create-logo-image] If large-data warning appears, enable compression and adjust slider | CANNOT FIX | WLED preset size limit is an inherent firmware constraint; defaults cannot remove it. |
| [create-logo-image] Click Save to upload the preset to the device | NOT A DEFAULT | User action completing their content workflow. |
| [create-logo-image] Refresh browser and reload the WLED integration in Home Assistant to see new presets | CANNOT FIX | HA-side integration cache behavior, outside device firmware control. |
| [create-logo-image] Import pre-made JSON preset codes: uncheck 'Use current state' and paste the API command | NOT A DEFAULT | Optional user choice to use provided logos (Apollo, Home Assistant, Dallas Cowboys). |
| [scrolling-text] Navigate to http://<your-ip-address> or http://<your-device-name>.local | CANNOT FIX | Customer network dependent; hostname example should show apollo-led-matrix-xxxxxx.local. |
| [scrolling-text] Search for and select the 'Scrolling Text' effect | NOT A DEFAULT | The example's purpose; user choice of effect. |
| [scrolling-text] Click the pencil icon on Segment 0 and enter the desired text | NOT A DEFAULT | User content. |
| [scrolling-text] Adjust sliders: effect speed, Y Offset, Trail/Decay, Font size (222 suggested) | NOT A DEFAULT | Customer taste; verify these MM-flavored slider names/values (esp. font size 222) match the upstream 16.0.1 Scrolling Text effect and update if renamed. |
| [scrolling-text] Set Fx/Bg/Gr colors | NOT A DEFAULT | Customer taste. |
| [scrolling-text] Click + Preset, name, save | NOT A DEFAULT | User choice, enables HA automations. |
| [qr-code-generator] Select QR code type from the dropdown (Wi-Fi/Text/URL/vCard) | NOT A DEFAULT | Wiki-hosted web tool, user choice of QR content type; nothing to do with device firmware. |
| [qr-code-generator] Enter the relevant information (SSID/password, URL, etc.) | CANNOT FIX | Depends on customer data (e.g. guest WiFi credentials). |
| [qr-code-generator] Click Generate QR Code, then Download | NOT A DEFAULT | Tool usage step. |
| [qr-code-generator] Convert the QR image to GIF and upload to WLED (stated for 'WLED-MM firmware 14.5.1 or higher') | NOT A DEFAULT | User content workflow; the WLED-MM 14.5.1 gating text needs a copy update and the GIF/Image effect dependency needs verifying on the new build. |
| [share-data-from-home-assistant] Prerequisite: pre-configure four segments on the M-1 (per segments doc) | NOT A DEFAULT | Factory default is a single 64x64 setup; the 4-segment split is example-specific user configuration the page should keep documenting. |
| [share-data-from-home-assistant] Install Studio Code Server from the HA add-on store | CANNOT FIX | Home Assistant side tooling; device firmware cannot remove it. |
| [share-data-from-home-assistant] Use the YAML generator with your entity IDs and copy the output | NOT A DEFAULT | Depends on the customer's HA entities; genuine user input. Verify the generator's default device hostname/IP placeholder matches new naming. |
| [share-data-from-home-assistant] Paste the YAML at the bottom of configuration.yaml | CANNOT FIX | HA-side configuration; outside firmware. |
| [share-data-from-home-assistant] Developer Tools > Check Configuration | CANNOT FIX | HA-side validation step. |
| [share-data-from-home-assistant] Developer Tools > Actions > search 'matrix' > execute the command to test | CANNOT FIX | HA-side test step. |
| [share-data-from-home-assistant] Create an automation with a time-pattern trigger (every minute) | NOT A DEFAULT | User choice of update cadence. |
| [share-data-from-home-assistant] Add the 'RESTful command: matrix_all_segments' action and save | NOT A DEFAULT | HA-side user configuration completing the example. |
| [media-proxy] (ESPHome firmware) Open the ESPHome integration page in HA and locate the Media Source entity | CANNOT FIX | ESPHome-firmware example, outside WLED firmware scope; the WLED migration must leave this path intact. |
| [media-proxy] (ESPHome firmware) Paste a supported media URL into the Media Source text entity | NOT A DEFAULT | User content choice on the separate ESPHome firmware. |
| [media-proxy] (ESPHome firmware) Optional: toggle 'Auto-switch to Media Stream on source change' | NOT A DEFAULT | User preference on the ESPHome firmware. |
| [sendspin] (ESPHome firmware) Install Music Assistant via the HA supervisor add-on button | CANNOT FIX | HA-side installation for the ESPHome firmware path. |
| [sendspin] (ESPHome firmware) In Music Assistant: select a player, click the players icon twice, check off the Apollo M-1 | NOT A DEFAULT | User choice of players on the ESPHome firmware. |
| [sendspin] (ESPHome firmware) Optional: Wizmote remote control via YAML editing | NOT A DEFAULT | Optional user customization on the ESPHome firmware. |

Copy updates needed:
- add-gifs-to-wled: page title 'Adding GIFs to M-1 on WLED-MM Firmware' and requirement 'firmware 14.5.1 or newer' reference WLED-MM and MM versioning; update to the new Apollo M-1 WLED firmware (upstream 16.0.1 based) naming/version, and verify the 'image' effect (GIF playback, an MM 14.5.1 feature) exists in the new build, if not, this page needs rework, not just copy edits
- qr-code-generator: 'For WLED-MM firmware version 14.5.1 or higher, you can convert images to GIF... and upload', same WLED-MM/version reference and same Image-effect dependency to update/verify
- create-gif: prerequisite 'Firmware version 14.5.1 or later' needs the new version; prerequisite 'correct LED matrix settings configured' should be removed or reworded since matrix settings (HUB75 Half Scan type 65, 1x 64x64) are now factory defaults; the 'find device IP via router or WLED Native app' guidance should lead with the new unique mDNS hostname apollo-led-matrix-xxxxxx.local; if the page's 'connect to Wi-Fi via config interface' section describes the old open/passwordless WLED-AP, update to setup AP 'Apollo M-1-xxxxxx' with password wled1234
- create-logo-image: PixelMagicTool (pxmagic.htm) reference, Pixel Magic flagged per instructions; verify it still saves presets correctly against upstream WLED 16.0.1; hostname example 'apollo-led-matrix.local' must gain the unique suffix: apollo-led-matrix-xxxxxx.local
- sendspin: phrase 'not the stock WLED-MM firmware', stock firmware is no longer WLED-MM; reword to 'the stock WLED firmware' or 'Apollo M-1 WLED firmware'
- scrolling-text: slider set (Y Offset, Trail/Decay, Font size with suggested value 222) reflects the MM implementation of Scrolling Text; verify slider names/ranges against upstream 16.0.1 and update text/screenshots if they differ
- all example pages using http://<your-device-name>.local placeholders: standardize on the new hostname pattern apollo-led-matrix-xxxxxx.local (unique last-6 MAC hex chars)
- share-data-from-home-assistant: check the linked YAML generator's default hostname/IP placeholder for old wled-* naming

Fact challenge field: No page content contradicted the stated premises. One dependency worth verifying rather than assuming: three example pages (add-gifs-to-wled, create-gif, qr-code-generator) rely on the WLED-MM 'Image' GIF-playback effect gated on MM 14.5.1; the premises do not state that the new upstream-16.0.1-based firmware compiles in an equivalent GIF/Image effect, and if it does not, those pages break functionally, not just editorially.

