"""Compare plotted land dimensions for all 30 populated parts to the reviewed PCB."""
from collections import defaultdict
import json
from pathlib import Path
import re
import pcbnew

here = Path(__file__).resolve().parent
hw = here.parents[2]
fab = here.parent / 'candidate' / 'fabrication'
board = pcbnew.LoadBoard(str(hw / 'esp32-e220.kicad_pcb'))
parts = json.loads((hw / 'production-metadata.json').read_text())['assembly_classes']['PCBA_POPULATE']

def apertures_at(path):
    sizes = {}
    flashes = defaultdict(set)
    selected = None
    for line in path.read_text().splitlines():
        definition = re.fullmatch(r'%ADD(\d+)(RoundRect|R|C|O),(.+)\*%', line)
        if definition:
            number, shape, args = definition.groups()
            dims = [float(n) for n in args.split('X')]
            if shape == 'RoundRect':
                r, *points, rot = dims
                assert rot == 0
                xs, ys = points[::2], points[1::2]
                w = max(xs) - min(xs) + 2*r
                h = max(ys) - min(ys) + 2*r
            elif shape == 'C':
                w = h = dims[0]
            else:
                w, h = dims[:2]
            sizes[number] = round(w*1e6), round(h*1e6)
        aperture = re.fullmatch(r'D(\d+)\*', line)
        if aperture:
            selected = aperture[1]
        point = re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*', line)
        if point and selected in sizes:
            flashes[tuple(map(int,point.groups()))].add(sizes[selected])
    return flashes

counts = {}
for ext, layer in [('gtl',pcbnew.F_Cu),('gbl',pcbnew.B_Cu),('gtp',pcbnew.F_Paste),('gts',pcbnew.F_Mask),('gbs',pcbnew.B_Mask)]:
    path, = fab.glob('*.' + ext)
    flashes = apertures_at(path)
    byref = {}
    for ref in sorted(parts):
        count = 0
        for pad in board.FindFootprintByReference(ref).Pads():
            if not pad.IsOnLayer(layer):
                continue
            w,h = pad.GetSizeX(),pad.GetSizeY()
            if layer in (pcbnew.F_Mask, pcbnew.B_Mask):
                expansion = pad.GetSolderMaskExpansion(layer)
                w,h = w+2*expansion,h+2*expansion
            elif layer == pcbnew.F_Paste:
                margin = pad.GetSolderPasteMargin(layer)
                w,h = w+2*margin.x,h+2*margin.y
            angle = pad.GetOrientationDegrees()
            assert abs(angle / 90 - round(angle / 90)) < 1e-9
            if round(angle/90)%2:
                w,h = h,w
            pos = pad.GetPosition()
            assert (w,h) in flashes[(pos.x,-pos.y)], (ext,ref,pad.GetNumber(),pos,w,h)
            count += 1
        if count: byref[ref] = count
    counts[ext] = {'parts':len(byref),'pad_flashes':sum(byref.values()),'per_part':byref}
print(json.dumps(counts,indent=2))
