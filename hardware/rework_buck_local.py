#!/usr/bin/env python3
"""OBSOLETE FAILED-EXPERIMENT helper for the legacy TPS62133 geometry.

DO NOT apply this script to the active PCB as a source of approved placement or
routing.  The planner/reviewer rejected the coupled local-cell geometry that
these checkpoints encode.  It is retained only as project-history/debugging
evidence.  New feasibility work starts from the separate unrouted candidate
created by ``hardware/make_assistant_buck_candidate.py`` and must pass native
KiCad DRC, ``pcb_routing_planner`` and ``pcb_reviewer`` before adoption.

The original checkpoint implementation remains below so historical states can
still be inspected deliberately.
"""

import argparse
import shutil
import pcbnew

BOARD = "hardware/esp32-e220.kicad_pcb"
MM = pcbnew.FromMM


def pt(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def pad(board, ref, number):
    fp = board.FindFootprintByReference(ref)
    return next(p for p in fp.Pads() if p.GetNumber() == number)


def segment(board, net, start, end, width, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetNet(board.FindNet(net))
    t.SetStart(pt(*start))
    t.SetEnd(pt(*end))
    t.SetWidth(MM(width))
    t.SetLayer(layer)
    board.Add(t)


def via(board, net, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetNet(board.FindNet(net))
    v.SetPosition(pt(x, y))
    v.SetWidth(MM(0.60))
    v.SetDrill(MM(0.30))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(v)


def local_gnd_zone(board):
    """One bounded F.Cu GND island for the TPS62133 capacitor-return node."""
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.F_Cu)
    z.SetNet(board.FindNet("/GND"))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetLocalClearance(MM(.20))
    z.SetMinThickness(MM(.25))
    poly = pcbnew.SHAPE_LINE_CHAIN()
    # Bounded to the U1/C1/C2 local-return side only; it does not enter the
    # SW/L1 left side and is not a board/global pour.
    # The outer border stays clear of the AVIN route. Filled copper is then
    # naturally necked around that route rather than crossing it.
    outline = [(70.80, 71.80), (78.50, 71.80), (78.50, 76.20),
               (70.80, 76.20)]
    for x, y in outline:
        poly.Append(pt(x, y))
    poly.SetClosed(True)
    z.AddPolygon(poly)
    board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def set_fp(board, ref, x, y, angle):
    fp = board.FindFootprintByReference(ref)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(angle)


def remove_between(board, net, a, b, tol=0.02):
    """Remove one known legacy segment, independent of endpoint direction."""
    def close(p, q):
        return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol
    for t in list(board.GetTracks()):
        if t.GetNetname() != net or isinstance(t, pcbnew.PCB_VIA):
            continue
        s = (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y))
        e = (pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y))
        if (close(s, a) and close(e, b)) or (close(s, b) and close(e, a)):
            board.Remove(t)
            return
    raise RuntimeError(f"legacy segment not found: {net} {a} {b}")


def remove_via(board, net, x, y, tol=0.02):
    for t in list(board.GetTracks()):
        if not isinstance(t, pcbnew.PCB_VIA) or t.GetNetname() != net:
            continue
        p = t.GetPosition()
        if abs(pcbnew.ToMM(p.x) - x) < tol and abs(pcbnew.ToMM(p.y) - y) < tol:
            board.Remove(t)
            return
    raise RuntimeError(f"legacy via not found: {net} {(x, y)}")


def reset_local(board):
    # Delete only the former U1/C1/C2/C3/L1 local copper, preserving the
    # accepted J4/F1/D3/Q1/R1/R2 input-protection path (old track indices 0..30).
    items = list(board.GetTracks())
    for t in items:
        s, e = t.GetStart(), t.GetEnd()
        sx, sy = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        ex, ey = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        net = t.GetNetname()
        local = (
            net in ("/BUCK_SW", "/5V_SYS", "/SS_TR")
            or (net == "/GND" and min(sx, ex) >= 60.0 and min(sy, ey) >= 69.0)
            or (net == "/BUCK_IN" and min(sx, ex) >= 66.2)
        )
        # R1's former GND tail ended at the old C3 pad; it must be replaced by
        # the local-via termination below when C3 moves.
        if net == "/GND" and ((abs(sx-60.0) < .01 and abs(ex-61.2) < .01) or
                              (abs(ex-60.0) < .01 and abs(sx-61.2) < .01)):
            local = True
        if local:
            board.Remove(t)

    # Preserve U1 orientation.  The passives are deliberately oriented so the
    # supply pads face their functional pins and each GND pad faces the compact
    # lower/right local ground region.
    set_fp(board, "C1", 75.300, 72.750, 270)
    set_fp(board, "C2", 75.900, 75.200, 270)
    set_fp(board, "C4", 74.800, 76.000, 0)
    set_fp(board, "L1", 66.300, 71.750, 180)
    set_fp(board, "C3", 65.500, 74.200, 0)


def checkpoint_a(board):
    # Direct common F.Cu AGND/PGND/EP bonds. Existing accepted C1/C2/C3
    # routes are deliberately retained until their own replacement checkpoints.
    # No via-in-pad.
    g = "/GND"
    # EP to immediately adjacent U1 GND pins.
    segment(board, g, (71.25, 70.60), (71.25, 71.16), .25)
    segment(board, g, (71.75, 70.60), (71.75, 71.16), .25)
    segment(board, g, (71.25, 73.40), (71.25, 72.84), .25)
    segment(board, g, (71.75, 73.40), (71.75, 72.84), .25)
    segment(board, g, (72.75, 73.40), (72.75, 72.84), .25)


def checkpoint_b(board):
    # Coupled B/C input checkpoint. The old C2 return via is inside C1's only
    # viable clearance corridor, so DRC makes a C1-only replacement impossible.
    # C1.1=(75.3,71.0) faces PVIN; C2.1=(77,74.075) faces AVIN.
    n = "/BUCK_IN"
    for a, b in [
        ((66.20, 69.00), (75.30, 69.00)),
        ((75.30, 69.50), (74.10, 69.50)),
        ((74.10, 69.50), (74.10, 71.25)),
        ((74.10, 71.25), (73.40, 71.25)),
        ((73.40, 71.25), (73.40, 72.25)),
        ((74.10, 69.50), (72.75, 70.60)),
    ]:
        remove_between(board, n, a, b)
    remove_between(board, "/GND", (75.30, 71.50), (76.20, 71.50))
    for a, b in [
        ((75.40, 74.625), (76.25, 74.625)),
        ((76.25, 74.625), (76.25, 71.50)),
        ((76.20, 71.50), (72.75, 74.20)),
    ]:
        remove_between(board, "/GND", a, b)
    for a, b in [
        ((75.40, 73.175), (74.20, 73.175)),
        ((74.20, 73.175), (74.20, 72.25)),
        ((74.20, 72.25), (73.40, 72.25)),
    ]:
        try:
            remove_between(board, n, a, b)
        except RuntimeError:
            pass
    remove_via(board, "/GND", 76.20, 71.50)
    set_fp(board, "C1", 75.300, 72.000, 270)
    set_fp(board, "C2", 77.000, 74.800, 270)
    segment(board, n, (66.20, 69.00), (75.30, 69.00), 1.00)
    segment(board, n, (75.30, 69.00), (75.30, 71.00), 1.00)
    segment(board, n, (75.30, 71.00), (73.40, 71.00), .35)
    segment(board, n, (73.40, 71.00), (73.40, 71.25), .25)
    segment(board, n, (73.40, 71.25), (73.40, 71.75), .25)
    segment(board, n, (73.40, 71.25), (72.75, 70.60), .25)
    local_gnd_zone(board)
    segment(board, n, (73.40, 72.25), (74.25, 72.25), .25)
    segment(board, n, (74.25, 72.25), (74.25, 74.075), .25)
    segment(board, n, (74.25, 74.075), (77.00, 74.075), .25)


def checkpoint_c(board):
    # C2 is completed atomically with C1 in checkpoint B because the former
    # C2 return via has zero physical clearance to the only C1 landing.
    return


def checkpoint_d(board):
    # Short F.Cu SW only, no via or copper expansion.
    segment(board, "/BUCK_SW", (70.60, 71.25), (70.60, 72.25), .25)
    segment(board, "/BUCK_SW", (70.60, 71.75), (67.975, 71.75), .70)


def checkpoint_e(board):
    # C3.1=(64.5,74.2), C3.2=(66.5,74.2).  The output power path is separate
    # from the later Kelvin VOS route.
    segment(board, "/5V_SYS", (64.625, 71.75), (64.625, 74.20), 1.00)
    segment(board, "/5V_SYS", (64.625, 74.20), (64.50, 74.20), 1.00)
    segment(board, "/GND", (66.50, 74.20), (69.20, 74.20), .50)
    segment(board, "/GND", (69.20, 74.20), (71.25, 73.40), .50)


def checkpoint_f(board):
    # VOS is low-current Kelvin sense.  It reaches C3's output pad via the
    # clear lower perimeter; it does not share the L1-to-C3 high-current run.
    n = "/5V_SYS"
    segment(board, n, (72.25, 70.60), (73.00, 69.85), .20)
    segment(board, n, (73.00, 69.85), (63.55, 69.85), .20)
    segment(board, n, (63.55, 69.85), (63.55, 74.20), .20)
    segment(board, n, (63.55, 74.20), (64.50, 74.20), .20)


def checkpoint_g(board):
    # C4.1=(74.075,76.0), C4.2=(75.525,76.0). SS/TR has a dedicated short
    # route on the east side of U1, away from the SW/L1 side.
    segment(board, "/SS_TR", (73.40, 72.75), (74.075, 72.75), .20)
    segment(board, "/SS_TR", (74.075, 72.75), (74.075, 76.00), .20)
    segment(board, "/GND", (75.525, 76.00), (74.60, 76.00), .35)
    segment(board, "/GND", (74.60, 76.00), (74.60, 75.45), .35)


def checkpoint_h(board):
    # FSW is a low-current configuration trace, not part of the 5V power
    # trunk.  FB and DEF are already directly tied to the common GND structure
    # through their footprint pads/EP connections; EN is part of checkpoint B.
    segment(board, "/5V_SYS", (72.25, 73.40), (73.20, 73.40), .20)
    segment(board, "/5V_SYS", (73.20, 73.40), (73.20, 74.05), .20)
    segment(board, "/5V_SYS", (73.20, 74.05), (72.45, 74.05), .20)
    # Explicit short DEF/FB ground links into the already bonded lower U1 GND.
    segment(board, "/GND", (71.25, 73.40), (72.75, 73.40), .20)


def main():
    ap = argparse.ArgumentParser(
        description="OBSOLETE legacy TPS62133 experiment helper; not an approved routing source."
    )
    ap.add_argument("checkpoint", choices=["restore", "reset", "a", "b", "c", "d", "e", "f", "g", "h"])
    ap.add_argument(
        "--allow-obsolete",
        action="store_true",
        help="required acknowledgement before applying any legacy checkpoint to the active PCB",
    )
    args = ap.parse_args()
    if not args.allow_obsolete:
        ap.error(
            "refusing to apply rejected legacy buck geometry; use "
            "hardware/make_assistant_buck_candidate.py for new feasibility work, "
            "or pass --allow-obsolete only for deliberate historical inspection"
        )
    if args.checkpoint == "restore":
        # The checked local reset is one reversible checkpoint.  This is the
        # documented clean partial-routing backup, not an abandoned full-board
        # routing attempt.
        shutil.copyfile("hardware/esp32-e220-pre-c2-ss-rework.kicad_pcb", BOARD)
        return
    board = pcbnew.LoadBoard(BOARD)
    {
        "reset": reset_local,
        "a": checkpoint_a,
        "b": checkpoint_b,
        "c": checkpoint_c,
        "d": checkpoint_d,
        "e": checkpoint_e,
        "f": checkpoint_f,
        "g": checkpoint_g,
        "h": checkpoint_h,
    }[args.checkpoint](board)
    pcbnew.SaveBoard(BOARD, board)


if __name__ == "__main__":
    main()
