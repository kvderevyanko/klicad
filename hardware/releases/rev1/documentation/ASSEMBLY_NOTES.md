# Rev.1 assembly notes

## Factory population

Factory populates all PCBA_POPULATE items, including carrier sockets J1/J2
(ESP32), J3 (E220), and J5 (OLED), and the JP1 header.

Factory does not populate J6 BUTTONS, J9 RGB, TP1...TP5, R10/R11, ESP32
DevKit, the E220 module, or the OLED module. TP1...TP5 are plated probe holes
only. The JP1 shunt is separate manual accessory SNT-100-BK-G, not a
pick-and-place footprint.

## Connector orientation

- J4 BATTERY: pad 1 = BAT+, pad 2 = GND.
- J8: external POWER SW connection.
- J5: GND, AUX_3V3, SCL, SDA.
- J6: GND, BTN1, BTN2, BTN3, BTN4, BTN5.
- J9: 5V, WS2812 DATA, GND.
- ESP32 USB-C/antenna orientation and E220 SMA/antenna orientation follow PCB silkscreen.

## JP1 service policy

- NORMAL: POWER_SW ON, JP1 CLOSED.
- USB SERVICE / carrier isolation: POWER_SW OFF, JP1 OPEN when isolation is required.

JP1 is not automatic power OR-ing.
