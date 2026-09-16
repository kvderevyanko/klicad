# Murata GRM manufacturer land-pattern re-audit

Read-only evidence audit, 2026-09-16.  Scope is the populated GRM MLCCs only.
No controlled design file, generator, Gerber, release, commit, or push was changed.

## FACT

Murata's own `2. Land Dimensions` diagram defines **a** as the copper
inner-edge gap, **b** as the individual land length along the capacitor long
axis, and **c** as land width.  This is visible in the retained exact Murata
document page image `primary/GRM21BR61A226ME44-page-25.png`; Table 2 is
explicitly headed `Reflow Soldering Method`.

All current project-local and embedded footprints use the same relevant
geometry, and the retained final F.Cu Gerber plus IPC-D-356 agree with it:

| GRM case | current individual land b x c | current a inner gap | centres / pitch |
|---|---:|---:|---:|
| GRM18 / 1608M | 0.95 x 1.00 | 0.50 | +/-0.725 / 1.45 |
| GRM21 / 2012M | 1.15 x 1.40 | 0.85 | +/-1.000 / 2.00 |

`a = pitch - b`, hence these are not an inference from the footprint name.
MLCCs have no polarity; physical terminals 1/2 therefore have no orientation
semantics beyond the numbered PCB pad/net traceability below.

| Ref(s) | exact MPN | exact Murata physical package data | exact applicable Table 2 reflow row (a gap / b length / c width, mm) | current -> manufacturer delta | pad/net chain |
|---|---|---|---|---|---|
| C2,C6,C7,C8 | `GRM188R71C104KA01D` | 1608M: L 1.6 +/-0.1, W 0.8 +/-0.1, T 0.8 +/-0.1; termination e 0.2..0.5, g >=0.5 | GRM18, 1.6x0.8 within +/-0.10: **0.6..0.8 / 0.6..0.7 / 0.6..0.8** | current **0.50 / 0.95 / 1.00**: a -0.10 below min; b +0.25 above max; c +0.20 above max. Centre pitch 1.45 can be retained only with a/b selected in-range (e.g. 0.75/0.70). | C2 1=`BUCK_IN`,2=`GND`; C6/7 1=`5V_SYS`,2=`GND`; C8 1=`BAT_SENSE`,2=`GND`. |
| C4 | `GRM1885C1H332JA01D` | 1608M: L 1.6 +/-0.1, W 0.8 +/-0.1, T 0.8 +/-0.1 | same GRM18 +/-0.10 row: **0.6..0.8 / 0.6..0.7 / 0.6..0.8** | current **0.50 / 0.95 / 1.00**: a -0.10; b +0.25; c +0.20 outside limits. | 1=`SS_TR`,2=`GND`. |
| C5 | `GRM188R61A106MAAL` | 1608M: L/W/T 1.6/0.8/0.8 +/-0.15; e 0.2..0.55, g >=0.6 | GRM18, 1.6x0.8 +/-0.15/+/-0.20: **0.7..0.9 / 0.7..0.8 / 0.8..1.0** | current **0.50 / 0.95 / 1.00**: a -0.20 below min; b +0.15 above max; c 0.00 at max. Pitch 1.45 can be retained with an in-range a/b pair (e.g. 0.70/0.75). | 1=`5V_SYS`,2=`GND`. |
| C1,C9,C10 | `GRM21BR61E106KA73` | 2012M: L/W/T 2.0/1.25/1.25 +/-0.15; e 0.2..0.7, g >=0.7 | GRM21, 2.0x1.25 +/-0.15: **0.6..0.8 / 1.2 fixed / 1.2..1.4** | current **0.85 / 1.15 / 1.40**: a +0.05 above max; b -0.05 below required; c 0.00 at max. Pitch 2.00 is retained by a=0.80,b=1.20. | C1 1=`BUCK_IN`,2=`GND`; C9 1=`5V_SYS`,2=`GND`; C10 1=`AUX_3V3`,2=`GND`. |
| C3 | `GRM21BR61A226ME44` | 2012M: L/W/T 2.0/1.25/1.25 +/-0.20; e 0.2..0.7, g >=0.7 | GRM21, 2.0x1.25 +/-0.20: **1.0..1.4 / 0.6..0.8 / 1.2..1.4** | current **0.85 / 1.15 / 1.40**: a -0.15 below min; b +0.35..+0.55 above range; c is at the upper limit. To preserve 2.00-mm pitch, choose an in-range pair such as a=1.30,b=0.70. | 1=`5V_SYS`,2=`GND`. |

The required manufacturer land-pattern comparisons are with the existing
physical copper dimensions; F.Paste and F.Mask share the same local pad
centres/sizes.  Thus the generated Gerber agrees with the incorrect current
land geometry rather than resolving the delta.

## SOURCE

Primary author and document content: Murata detailed specification / reference
sheets, section `2. Land Dimensions`, Table 2 `Reflow Soldering Method`:

* `primary/GRM188R71C104KA01D-murata-document.pdf` — exact C2/C6/C7/C8 MPN;
  package data p.1.
* `primary/GRM1885C1H332JA01D-murata-document.pdf` — exact C4 MPN;
  package data p.1.
* `primary/GRM188R61A106MAAL-01A-murata-document.pdf` — exact C5 MPN;
  package data p.1 and Table 2 p.25.
* `primary/GRM21BR61E106KA73-01A-murata-document.pdf` — exact C1/C9/C10 MPN;
  package data p.1.
* `primary/GRM21BR61A226ME44-01A-murata-document.pdf` — exact C3 MPN;
  package data p.1 and Table 2 p.25.

The locally retained copies are vendor-hosted copies of Murata-authored
reference sheets because Murata's PIM asset endpoint returned HTTP 403 to
direct retrieval.  Their title pages identify Murata and exact MPN; this is
not a distributor-generated footprint.  The canonical manufacturer product
pages use the same part roots: `https://www.murata.com/products/productdetail?partno=<MPN>%23`.
Extracted source text is retained under `primary/text/`; PDF SHA-256 values
are in the command record for this scope.

## CLASSIFICATION

**REAL MISMATCH — FAIL** for every populated Murata GRM footprint group above.
This supersedes the earlier `UNVERIFIED` disposition.  The earlier audit did
not inspect the manufacturer `Land Dimensions` Table 2 and consequently used
the generic 0603/0805 project pattern as its evidence basis.

## IMPACT

Do not change these footprints merely to make a status pass.  The documented
manufacturer deltas require a controlled physical correction transaction:
generator/source-of-truth update, embedded-footprint update, local routing
review if pad edges change, full regenerate and Gerber/IPC re-audit, then an
independent implementation review.  The table shows that centre pitch can be
preserved in all groups by selecting a/b inside Murata's stated ranges, so
the likely physical scope is pad-size adjustment; it is not authorized or
implemented by this read-only audit.

AUDIT COMPLETE
