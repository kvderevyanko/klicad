#!/usr/bin/env python3
"""Bounded physical Rev.1 expansion transactions; never changes schematic data."""
from pathlib import Path
import argparse
import pcbnew

ROOT = Path(__file__).resolve().parents[3]
PCB = ROOT / "hardware/esp32-e220.kicad_pcb"
LOCAL = ROOT / "hardware/esp32-e220.pretty"
STD = Path("/usr/share/kicad/footprints")
IU = pcbnew.FromMM

def net(board, name):
    wanted = "/" + name
    for candidate in board.GetNetsByNetcode().values():
        if candidate.GetNetname() == wanted:
            return candidate
    item = pcbnew.NETINFO_ITEM(board, wanted)
    board.Add(item)
    return item

def fp(board, directory, name, ref, value, fpid, x, y, rot=0):
    item = pcbnew.FootprintLoad(str(directory), name)
    if item is None:
        raise RuntimeError(f"cannot load {directory}/{name}")
    item.SetReference(ref)
    item.SetValue(value)
    nickname, footprint_name = fpid.split(":", 1) if ":" in fpid else ("", fpid)
    item.SetFPID(pcbnew.LIB_ID(nickname, footprint_name))
    item.SetPosition(pcbnew.VECTOR2I(IU(x), IU(y)))
    item.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    board.Add(item)
    return item

def pad(item, number):
    for p in item.Pads():
        if p.GetNumber() == str(number):
            return p
    raise RuntimeError(f"{item.GetReference()}: pad {number} missing")

def assign(item, mapping, board):
    for number, name in mapping.items():
        pad(item, number).SetNet(net(board, name))

def pt(x, y): return pcbnew.VECTOR2I(IU(x), IU(y))

def track(board, net_name, a, b, width=0.25, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(*a)); t.SetEnd(pt(*b)); t.SetWidth(IU(width))
    t.SetLayer(layer); t.SetNet(net(board, net_name)); board.Add(t)
    return t

def via(board, net_name, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y)); v.SetWidth(IU(0.60)); v.SetDrill(IU(0.30))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net(board, net_name)); board.Add(v)
    return v

def power_via(board, net_name, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(x, y)); v.SetWidth(IU(0.80)); v.SetDrill(IU(0.40))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net(board, net_name)); board.Add(v)
    return v

def remove_tracks(board, net_name, endpoints=None):
    for item in list(board.GetTracks()):
        if not isinstance(item, pcbnew.PCB_TRACK) or item.GetNetname() != "/" + net_name:
            continue
        if endpoints is None:
            board.Remove(item); continue
        a, b = item.GetStart(), item.GetEnd()
        coords = {(round(a.x / 1e6, 3), round(a.y / 1e6, 3)), (round(b.x / 1e6, 3), round(b.y / 1e6, 3))}
        if any(tuple(x) in coords for x in endpoints): board.Remove(item)

def stage_a(board):
    # J8 exits at the lower service edge; its B.Cu BAT_FUSED approach avoids Q1 gate copper.
    j8 = fp(board, STD / "Connector_JST.pretty", "JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal",
            "J8", "B2PS-VH(LF)(SN)", "Connector_JST:JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal", 105.0, 78.0, 90)
    assign(j8, {1: "BAT_FUSED", 2: "BAT_SW"}, board)
    assign(board.FindFootprintByReference("Q1"), {3: "BAT_SW"}, board)
    # Only the post-F1 positive run is reworked. D3 remains directly upstream on BAT_FUSED.
    remove_tracks(board, "BAT_FUSED")
    track(board, "BAT_FUSED", (47.138, 76), (47.138, 72.5), 1.0)
    track(board, "BAT_FUSED", (47.138, 72.5), (44.05, 72.5), 1.0)
    track(board, "BAT_FUSED", (44.05, 72.5), (44.05, 70.5), 1.0)
    p1 = pad(j8, 1).GetPosition()
    track(board, "BAT_FUSED", (47.138, 76), (47.138, 84), 1.0)
    track(board, "BAT_FUSED", (47.138, 84), (100, 84), 1.0)
    track(board, "BAT_FUSED", (100, 84), (103, 80), 1.0)
    track(board, "BAT_FUSED", (103, 80), (p1.x/1e6, p1.y/1e6), 1.0)
    p2 = pad(j8, 2).GetPosition(); q3 = pad(board.FindFootprintByReference("Q1"), 3).GetPosition()
    track(board, "BAT_SW", (p2.x/1e6, p2.y/1e6), (70.0, 72.0), 1.0)
    power_via(board, "BAT_SW", 70.0, 72.0)
    track(board, "BAT_SW", (70.0, 72.0), (60.0, 74.0), 1.0, pcbnew.B_Cu)
    power_via(board, "BAT_SW", 60.0, 74.0)
    track(board, "BAT_SW", (60.0, 74.0), (q3.x/1e6, q3.y/1e6), 1.0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

def stage_b(board):
    jp1 = fp(board, STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical",
             "JP1", "TSW-102-07-G-S + SNT-100-BK-G", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", 96.0, 14.0, 270)
    assign(jp1, {1: "5V_SYS", 2: "DEVKIT_VIN"}, board)
    assign(board.FindFootprintByReference("J1"), {1: "DEVKIT_VIN"}, board)
    remove_tracks(board, "5V_SYS", [(96.0, 14.0), (111.0, 14.0)])
    # The endpoint-based removal also removes the former vertical termination;
    # restore that retained trunk exactly, now ending at JP1.1.
    track(board, "5V_SYS", (96.0, 43.5), (96.0, 14.0), 1.0)
    p2 = pad(jp1, 2).GetPosition()
    track(board, "DEVKIT_VIN", (p2.x/1e6, p2.y/1e6), (92.0, 20.0), 0.8, pcbnew.B_Cu)
    track(board, "DEVKIT_VIN", (92.0, 20.0), (103, 20.0), 0.8, pcbnew.B_Cu)
    track(board, "DEVKIT_VIN", (103, 20.0), (108.5, 15.2), 0.8, pcbnew.B_Cu)
    track(board, "DEVKIT_VIN", (108.5, 15.2), (111, 14), 0.8, pcbnew.B_Cu)

def stage_c(board):
    r3 = fp(board, LOCAL, "Resistor_0603_1608Metric", "R3", "RC0603FR-0710KL", "Carrier:Resistor_0603_1608Metric", 86.0, 66.0, 0)
    r4 = fp(board, LOCAL, "Resistor_0603_1608Metric", "R4", "RC0603FR-073K3L", "Carrier:Resistor_0603_1608Metric", 90.0, 66.0, 0)
    c8 = fp(board, LOCAL, "Murata_GRM188_1608Metric", "C8", "GRM188R71C104KA01D", "Carrier:Murata_GRM188_1608Metric", 88.0, 69.0, 0)
    assign(r3, {1: "BUCK_IN", 2: "BAT_SENSE"}, board)
    assign(r4, {1: "BAT_SENSE", 2: "GND"}, board)
    assign(c8, {1: "BAT_SENSE", 2: "GND"}, board)
    assign(board.FindFootprintByReference("J1"), {10: "BAT_SENSE"}, board)
    a, b = pad(r3, 1).GetPosition(), pad(r3, 2).GetPosition()
    c, d = pad(r4, 1).GetPosition(), pad(r4, 2).GetPosition()
    e, f = pad(c8, 1).GetPosition(), pad(c8, 2).GetPosition()
    track(board, "BUCK_IN", (65.5, 63.0), (a.x/1e6, a.y/1e6), 0.25)
    track(board, "BAT_SENSE", (b.x/1e6, b.y/1e6), (c.x/1e6, c.y/1e6), 0.25)
    track(board, "BAT_SENSE", (b.x/1e6, b.y/1e6), (e.x/1e6, e.y/1e6), 0.25)
    via(board, "GND", f.x/1e6, f.y/1e6)
    track(board, "GND", (d.x/1e6, d.y/1e6), (f.x/1e6, f.y/1e6), 0.25)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

def add_silk(board, text, x, y, size=0.8, angle=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text); t.SetPosition(pt(x, y)); t.SetTextSize(pcbnew.VECTOR2I(IU(size), IU(size)))
    t.SetTextThickness(IU(0.12)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T)); board.Add(t)

def stage_d(board):
    u4 = fp(board, STD / "Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", "U4", "TLV1117LV33DCYR", "Package_TO_SOT_SMD:SOT-223-3_TabPin2", 125.0, 68.0, 0)
    c9 = fp(board, LOCAL, "Murata_GRM21_2012Metric", "C9", "GRM21BR61E106KA73", "Carrier:Murata_GRM21_2012Metric", 115.0, 60.0, 180)
    c10 = fp(board, LOCAL, "Murata_GRM21_2012Metric", "C10", "GRM21BR61E106KA73", "Carrier:Murata_GRM21_2012Metric", 135.0, 68.0, 0)
    assign(u4, {1: "GND", 2: "AUX_3V3", 3: "5V_SYS"}, board)
    assign(c9, {1: "5V_SYS", 2: "GND"}, board)
    assign(c10, {1: "AUX_3V3", 2: "GND"}, board)
    assign(board.FindFootprintByReference("J5"), {2: "AUX_3V3"}, board)
    p3 = pad(u4, 3).GetPosition(); cin = pad(c9, 1).GetPosition(); cout = pad(c10, 1).GetPosition()
    track(board, "5V_SYS", (80, 64), (106, 64), 0.8, pcbnew.B_Cu)
    via(board, "5V_SYS", 106, 64)
    track(board, "5V_SYS", (106, 64), (106, p3.y/1e6), 0.8)
    track(board, "5V_SYS", (106, p3.y/1e6), (p3.x/1e6, p3.y/1e6), 0.8)
    track(board, "5V_SYS", (p3.x/1e6, p3.y/1e6), (cin.x/1e6, p3.y/1e6), 0.8)
    track(board, "5V_SYS", (cin.x/1e6, p3.y/1e6), (cin.x/1e6, cin.y/1e6), 0.8)
    # Output pad and tab are solid to the dedicated copper. Grounds remain
    # explicit in the ratsnest until the final return-zone review.
    for x, y in ((125.0, 66.0), (130.0, 66.0), (125.0, 70.0), (130.0, 70.0)):
        via(board, "AUX_3V3", x, y)
    # Zone generation is deliberately performed by pcbnew so it retains live fill/clearance behavior.
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetNet(net(board, "AUX_3V3")); z.SetLayer(layer)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetLocalClearance(IU(0.20)); z.SetMinThickness(IU(0.25))
        outline = z.Outline(); outline.NewOutline()
        for x, y in ((114, 57), (136, 57), (136, 79), (114, 79)):
            outline.Append(pt(x, y))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    add_silk(board, "U4 AUX 3V3\n300mA TOTAL", 125, 82.0, 0.8)

def mechanics_and_headers(board):
    if board.FindFootprintByReference("J6"):
        return
    j6 = fp(board, STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x05_P2.54mm_Vertical", "J6", "TSW-105-07-G-D", "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical", 84.0, 20.0, 0)
    j7 = fp(board, STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x06_P2.54mm_Vertical", "J7", "TSW-106-07-G-D", "Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical", 84.0, 38.0, 0)
    assign(j6, {1:"GND",2:"GPIO13",3:"GND",4:"GPIO14",5:"GND",6:"GPIO18",7:"GND",8:"GPIO19",9:"AUX_3V3",10:"GPIO23"}, board)
    assign(j7, {1:"GND",2:"AUX_3V3",3:"OLED_SDA",4:"OLED_SCL",5:"GPIO18",6:"GPIO23",7:"GPIO19",8:"GPIO13",9:"GPIO14",10:"GPIO33",11:"GND",12:"AUX_3V3"}, board)
    for ref, x, y in (("H1",37,7),("H2",90,7),("H3",107,83),("H4",138,83)):
        fp(board, LOCAL, "MountingHole_M3_NPTH", ref, "M3 NPTH", "Carrier:MountingHole_M3_NPTH", x, y)
    for ref, x, y in (("SR1",27,84),("SR2",42,84)):
        fp(board, LOCAL, "StrainRelief_NPTH_2p5mm", ref, "CABLE TIE NPTH", "Carrier:StrainRelief_NPTH_2p5mm", x, y)
    add_silk(board, "USER GPIO\n3V3 ONLY\n200mA MAX SHARED\n1G 2G13 3G 4G14 5G\n6G18 7G 8G19 9AUX 10G23", 91.5, 25, 0.65)
    add_silk(board, "DISPLAY AUX\n3V3 ONLY\n1G 2AUX 3SDA 4SCL\n5G18 6G23 7G19 8G13\n9G14 10G33 11G 12AUX", 91.5, 44, 0.65)
    add_silk(board, "POWER SW\nPIN 1 = BAT_FUSED", 56, 62, 0.75)
    add_silk(board, "DEVKIT PWR\nREMOVE FOR USB ISOLATION", 99, 24, 0.7)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("stage", choices=("a","b","c","d","mechanics"))
    args = parser.parse_args(); board = pcbnew.LoadBoard(str(PCB))
    {"a":stage_a,"b":stage_b,"c":stage_c,"d":stage_d,"mechanics":mechanics_and_headers}[args.stage](board)
    pcbnew.SaveBoard(str(PCB), board)

if __name__ == "__main__": main()
