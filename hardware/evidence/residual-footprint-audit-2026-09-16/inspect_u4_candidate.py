#!/usr/bin/env python3
"""Read-only endpoint containment audit for the proposed TI DCY lands."""
from __future__ import annotations

import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "esp32-e220.kicad_pcb"
MM = pcbnew.FromMM

# Board coordinates and copper dimensions in millimetres.  The proposed values
# are the 90-degree rotation of TI 4210278/C into the active footprint axes.
PADS = (
    ("1", "GND", (17.50, 24.70), (17.75, 24.70), (2.15, 0.95)),
    ("2 lead", "AUX_3V3", (17.50, 27.00), (17.75, 27.00), (2.15, 0.95)),
    ("2 tab", "AUX_3V3", (23.80, 27.00), (23.55, 27.00), (2.15, 3.25)),
    ("3", "5V_SYS", (17.50, 29.30), (17.75, 29.30), (2.15, 0.95)),
)


def xy(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(point.x), 4), round(pcbnew.ToMM(point.y), 4)


def inside(point: tuple[float, float], centre: tuple[float, float], size: tuple[float, float]) -> bool:
    return (
        centre[0] - size[0] / 2 <= point[0] <= centre[0] + size[0] / 2
        and centre[1] - size[1] / 2 <= point[1] <= centre[1] + size[1] / 2
    )


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    u4 = footprints["U4"]
    observed = []
    for pad in u4.Pads():
        observed.append({"number": pad.GetNumber(), "centre_mm": xy(pad.GetPosition()), "net": pad.GetNetname(), "size_mm": xy(pad.GetSize())})

    results = []
    for name, net, old, proposed, size in PADS:
        attached = []
        for track in board.GetTracks():
            if track.GetNetname().lstrip("/") != net:
                continue
            for endpoint_name, endpoint in (("start", xy(track.GetStart())), ("end", xy(track.GetEnd()))):
                # The old pads are intentionally not used for selection: record
                # every same-net endpoint at the current pad centre or inside it.
                if inside(endpoint, old, (2.0, 3.8 if name == "2 tab" else 1.5)):
                    attached.append({
                        "endpoint": endpoint_name,
                        "mm": list(endpoint),
                        "width_mm": round(pcbnew.ToMM(track.GetWidth()), 4),
                        "inside_proposed_copper": inside(endpoint, proposed, size),
                    })
        results.append({
            "pad": name,
            "net": net,
            "current_absolute_centre_mm": list(old),
            "proposed_absolute_centre_mm": list(proposed),
            "proposed_copper_size_mm": list(size),
            "attached_track_endpoints": attached,
            "routing_change_required": any(not item["inside_proposed_copper"] for item in attached),
        })

    payload = {
        "scope": "U4 TI 4210278/C candidate endpoint containment",
        "status": "READ_ONLY_PLAN_DATA",
        "u4_observed_pads": observed,
        "pads": results,
        "board_vias_within_5mm_of_u4_origin": [
            {"centre_mm": list(xy(via.GetPosition())), "net": via.GetNetname()}
            for via in board.GetTracks() if isinstance(via, pcbnew.PCB_VIA)
            and abs(pcbnew.ToMM(via.GetPosition().x) - 20.65) <= 5
            and abs(pcbnew.ToMM(via.GetPosition().y) - 27.0) <= 5
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
