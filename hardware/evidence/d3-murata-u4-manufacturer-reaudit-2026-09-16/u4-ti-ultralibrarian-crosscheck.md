# U4 — TI DCY package and TI-linked Ultra Librarian cross-check

Read-only audit, 2026-09-16.  No controlled design or generated-output file
was changed.

## TI primary package comparison

TI `TLV1117LV` datasheet SBVS160C, package drawing MPDS094A / 4202506/B,
identifies `TLV1117LV33DCYR` as four-pin DCY/SOT-223.  The primary drawing
specifies body L=6.30..6.70 mm, W=3.30..3.70 mm, 2.30-mm lead pitch, lead
width 0.66..0.84 mm, lead contact length >=0.75 mm, and exposed tab = pin 2.
The functional pin order is 1=GND, 2=OUT (including tab), 3=IN.

| physical terminal | current local/embedded land | local centre (mm) | size (mm) | absolute centre / net |
|---|---|---:|---:|---|
| pin 1 | 1 | (-3.15,-2.30) | 2.00 x 1.50 | (17.50,24.70) / GND |
| pin 2 lead | 2 | (-3.15,0) | 2.00 x 1.50 | (17.50,27.00) / AUX_3V3 |
| pin 2 tab | 2 | (+3.15,0) | 2.00 x 3.80 | (23.80,27.00) / AUX_3V3 |
| pin 3 | 3 | (-3.15,+2.30) | 2.00 x 1.50 | (17.50,29.30) / 5V_SYS |

The project-local footprint, embedded PCB and diagnostic Gerber/IPC-D-356
agree on each centre, size, duplicate pad-2 mapping, orientation and net.
This confirms package/pin mapping; TI does not provide a recommended PCB land
pattern in this datasheet/drawing.

## TI-linked CAD source result

TI's product page offers the `SOT-223 (DCY), 4` CAD link through Ultra
Librarian.  Its public part page for `TLV1117LV33DCYR` identifies that MPN as
four-pin SOT-223 and exposes a detailed-footprint preview.  The actual public
preview asset served for that page is `detailed-YDC4.svg`, whose visible pads
are labelled `A1`, `A2`, `B1`, `B2` and arranged as a 2x2 array.  It therefore
does **not** describe a DCY/SOT-223 lead-and-tab footprint and contradicts TI's
own DCY drawing and the page's MPN/package metadata.

`CONTEXT PROVENANCE CONFLICT`:

* TI primary: DCY/SOT-223, lead pads 1/2/3 plus tab pad 2.
* TI-linked Ultra Librarian public preview: unrelated `YDC4` four-pad 2x2
  representation.

The Ultra Librarian download is login-gated, so no licensed CAD download was
used or retained.  The preview is not a valid independent numerical land
pattern and cannot justify replacing or approving the current footprint.

## Disposition

No new U4 physical mismatch is demonstrated.  Package dimensions, pin
numbering, tab-to-pad-2 mapping, schematic nets and Gerber are consistent
with TI's primary drawing.  U4 remains `UNVERIFIED LAND PATTERN`: a correct
TI-linked vendor CAD cross-check could alter that disposition only after the
vendor supplies a DCY/SOT-223 footprint rather than this contradictory public
preview.

Sources: TI primary PDF retained at
`hardware/evidence/full-production-audit-2026-09-15/primary/ti-tlv1117lv.pdf`;
TI product page `https://www.ti.com/product/TLV1117LV`; TI-linked CAD page
`https://cad.ultralibrarian.com/orcad/Home?mfr=Texas-Instruments&mpn=TLV1117LV33DCYR&partUuid=1683fc3b-103f-11e9-ab3a-0a3560a4cccc`; preview
`https://static.ultralibrarian.com/part-previews/footprints/5162827/detailed-YDC4.svg`.
