# Wiki: M-1 LED Matrix WLED Configuration Settings (captured 2026-07-11)

Source: https://wiki.apolloautomation.com/products/m1/setup/m1-matrix-settings/
This page is the manual-configuration procedure customers must follow today. The goal
of the migration is to make every step below unnecessary on a factory-fresh unit.

## Friendly Name
Config > User Interface > Server description: "Apollo LED Matrix"

## Hostname (mDNS Address)
Config > WiFi Setup > mDNS address: apollo-led-matrix
(page notes standard hostname restrictions: lowercase a-z, 0-9, hyphen; no leading or
trailing hyphen; label max 63 chars)
Result: http://apollo-led-matrix.local

## LED Preferences
Config > LED Preferences:
- LED Type: Hub75Matrix 64x64
- Chain Length: 1
- Brightness Limiter: UNCHECK "enable automatic brightness limiter"
- Save

## 2D Configuration
Config > 2D Configuration:
- 2D Matrix
- Basic
- Panel Dimensions: 64 x 64
- Save

## AudioReactive Settings (Rev6 PCB with microphone addon only)
Config > AudioReactive (usermod settings):
- Enable the feature
- Type: Generic I2S
- Pin I2S SD: 10
- Pin I2S WS: 12
- Pin I2S SCK: 11
- Mode (sync, bottom of settings): Off
