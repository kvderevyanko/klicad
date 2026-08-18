# Rev.1 project-local footprint library

This library contains only the Stage 7 interface/mechanical footprints. It is
not a PCB layout and is not a release package.

`ESP32_DevKit_2x15_Socket_P2.54mm_P25.40mm` has verified electrical socket
coordinates (two 1x15 rows, 2.54 mm pitch, 25.40 mm row spacing). Its 28 x
51 mm body envelope is deliberately marked **USER-MEASURED / DATUM
REGISTRATION TBD**: it must not be used to place a board edge, keepout or
enclosure until the distance from the header datum to the actual DevKit body
and antenna is measured.

`E220_T22D_Socket_400_900` uses the common EBYTE E220-400/900T22D source
drawing: 21 x 36 mm body, a 7-pin 2.54-mm row, pin-row centreline 1.50 mm
from the short edge, and pin 1 at X=2.88 mm. It represents the **carrier-side
Samtec socket**, not EBYTE's soldered-module pad pattern. The EBYTE fixed
holes are intentionally not carrier holes: their function, coordinates and
underside clearance must be audited before a PCB release.

`OLED_0.96in_1x04_InterfaceOnly` verifies only the 1x4 socket coordinates and
the user/seller-provided 25.20 x 26.00 mm outline. It has no mounting holes:
`OLED_MOUNT_Y` is unknown and a production mounting pattern is forbidden.

Each footprint's full source and verification status is in
`docs/footprint-mechanical-review.md`.
