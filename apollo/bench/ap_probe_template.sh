#!/bin/bash
# Self-contained AP probe: join hotspot, enumerate routes, rejoin home WiFi. NO internet during run.
HOME_SSID="JT 5G"
AP_SSID="Apollo M-1-6d0a40"
OUT=/Users/justinapollo/Code/ApolloAutomation/WLED-M1/baseline/ap-firstrun
LOG="$OUT/route_battery.txt"
GIF=/private/tmp/claude-501/-Users-justinapollo-Code-ApolloAutomation/17143c94-ba61-41a1-a8cd-011bd2e2cf7b/scratchpad/bounce.gif

rejoin() { networksetup -setairportnetwork en0 "$HOME_SSID" >/dev/null 2>&1; }
trap rejoin EXIT

echo "== joining $AP_SSID ==" > "$LOG"
networksetup -setairportnetwork en0 "$AP_SSID" >> "$LOG" 2>&1
IP=""; for i in $(seq 1 20); do sleep 1; IP=$(ipconfig getifaddr en0 2>/dev/null); [ -n "$IP" ] && break; done
GW=$(route -n get default 2>/dev/null | awk '/gateway/{print $2}')
echo "mac ip=$IP gateway=$GW" >> "$LOG"
if [ -z "$IP" ]; then echo "JOIN FAILED" >> "$LOG"; exit 1; fi

probe() { # url label extra...
  local url="$1" label="$2"; shift 2
  local code size
  code=$(curl -s -o /tmp/ap_body -w "%{http_code} %{size_download} %{redirect_url}" --max-time 8 "$@" "$url" 2>>"$LOG")
  echo "PROBE [$label] $url -> $code" >> "$LOG"
}
T=${GW:-4.3.2.1}
probe "http://4.3.2.1/"            "root-4321"
probe "http://$T/"                 "root-gw"
probe "http://$T/index.htm"        "index"
probe "http://$T/json/info"        "json-info"
probe "http://$T/json/state"       "json-state"
probe "http://$T/json/cfg"         "json-cfg"
probe "http://$T/presets.json"     "presets"
probe "http://$T/cfg.json"         "cfg-raw"
probe "http://$T/pixelforge.htm"   "pixelforge"
probe "http://$T/pixelpaint.htm"   "pixelpaint"
probe "http://$T/edit"             "edit"
probe "http://$T/nonexistent-xyz"  "404-test"
probe "http://4.3.2.1/"            "captive-host" -H "Host: connectivitycheck.gstatic.com"
probe "http://$T/win&T=2"          "http-api"
# DNS wildcard test
echo "== DNS test ==" >> "$LOG"
dscacheutil -flushcache 2>/dev/null
python3 - << 'PYEOF' >> "$LOG" 2>&1
import socket
try:
    socket.setdefaulttimeout(4)
    print("resolve example.com ->", socket.gethostbyname("example.com"))
except Exception as e:
    print("resolve example.com FAILED:", e)
PYEOF
# capture canonical state files over AP
for f in json/state json/cfg presets.json json/info; do
  curl -s --max-time 8 "http://$T/$f" -o "$OUT/$(echo $f | tr '/' '_')" 2>>"$LOG"
done
# upload test: POST a gif to /upload like PixelForge does
if [ -f "$GIF" ]; then
  UP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 -F "data=@$GIF;filename=/aptest.gif" "http://$T/upload")
  echo "PROBE [upload-gif] /upload -> $UP" >> "$LOG"
  DL=$(curl -s -o /dev/null -w "%{http_code} %{size_download}" --max-time 8 "http://$T/aptest.gif")
  echo "PROBE [readback-gif] /aptest.gif -> $DL" >> "$LOG"
fi
echo "== rejoining $HOME_SSID ==" >> "$LOG"
rejoin
for i in $(seq 1 25); do sleep 1; ping -c1 -t2 192.168.1.1 >/dev/null 2>&1 && { echo "home network restored" >> "$LOG"; break; }; done
