"""Check the final bounded PCB changes and regenerated footprint sources."""

import json
from pathlib import Path
import shutil
import tempfile

from transact import BASE, ENV, HARDWARE, HERE, LIB, PCB, PLACEMENT, SCHEMATIC, SCH, SCOPE, run, sync


def footprint_map(root):
    return {sync.prop_map(item)['Reference']: item for item in sync.forms(root, 'footprint')}


def geometry(footprint):
    return {
        pad[1]: {
            'type': pad[2:4],
            'centre': list(map(float, sync.first(pad, 'at')[1:3])),
            'size': list(map(float, sync.first(pad, 'size')[1:])),
            'layers': sorted(sync.first(pad, 'layers')[1:]),
            'roundrect_ratio': float((sync.first(pad, 'roundrect_rratio') or [None, 0])[1]),
        }
        for pad in sync.forms(footprint, 'pad')
    }


def by_uuid(root, tag):
    return {sync.first(item, 'uuid')[1]: item for item in sync.forms(root, tag)}


def netlist(path):
    sync.SCH = path
    return sync.netlist()


def main():
    old = sync.sexp(BASE.read_text())
    board = sync.sexp((HARDWARE / PCB).read_text())
    old_fps, new_fps = footprint_map(old), footprint_map(board)
    changed_fps = {ref for ref in new_fps if new_fps[ref] != old_fps[ref]}
    assert changed_fps == {'L1', 'R2', 'R8', 'R9'}, changed_fps
    old_nets = {ref: item['pads'] for ref, item in sync.board(BASE).items()}
    new_nets = {ref: item['pads'] for ref, item in sync.board(HARDWARE / PCB).items()}
    assert old_nets == new_nets
    old_routes, new_routes = by_uuid(old, 'segment'), by_uuid(board, 'segment')
    changed_routes = {uid for uid in new_routes if old_routes[uid] != new_routes[uid]}
    endpoints = {
        'fdb0c9da-4ac0-48ab-8e20-b8d4a9e4f70b': ('end', '73.5', '57.71'),
        '390b8209-3bbd-4be0-8326-116a543cd20e': ('start', '73.5', '55.34'),
    }
    assert old_routes.keys() == new_routes.keys()
    assert changed_routes == endpoints.keys()
    for uid, (tag, x, y) in endpoints.items():
        assert sync.first(new_routes[uid], tag) == [tag, x, y]
        assert [part for part in new_routes[uid] if part[0] != tag] == [part for part in old_routes[uid] if part[0] != tag]
    assert [part for part in board if part[0] not in {'footprint', 'segment'}] == [part for part in old if part[0] not in {'footprint', 'segment'}]
    assert netlist(HARDWARE / SCH) == netlist(SCOPE / 'baseline' / SCH)

    directory = HERE / 'reproduction'
    directory.mkdir()
    for name in ('generate_stage7_footprints.py', PLACEMENT, SCHEMATIC, 'generate_stage7_preliminary_pcb.py'):
        shutil.copy2(HARDWARE / name, directory / name)
    run(['python3', str(directory / 'generate_stage7_footprints.py')], directory / 'stage7.log')
    run(['python3', str(directory / SCHEMATIC)], directory / 'schematic.log')
    with tempfile.TemporaryDirectory(dir=HERE / 'tmp') as temp:
        scratch = Path(temp)
        shutil.copy2(directory / 'generate_stage7_preliminary_pcb.py', scratch)
        (scratch / LIB).symlink_to(directory / LIB, target_is_directory=True)
        run(['/usr/bin/python3', str(scratch / 'generate_stage7_preliminary_pcb.py')], directory / 'preliminary-placement.log')
        preliminary = footprint_map(sync.sexp((scratch / PCB).read_text()))
        assert geometry(preliminary['L1']) == geometry(new_fps['L1'])
    ENV['PLACEMENT_OUTPUT'] = str(directory / 'stage8.kicad_pcb')
    run(['/usr/bin/python3', str(directory / PLACEMENT)], directory / 'stage8.log')
    stage8 = footprint_map(sync.sexp((directory / 'stage8.kicad_pcb').read_text()))
    assert netlist(directory / SCH) == netlist(HARDWARE / SCH)
    sync.SCH = directory / SCH
    regenerated = sync.symbols()
    refs = ['L1', 'Q1', 'R1', 'R2', 'R8', 'R9', 'U3']
    actual = {}
    for ref in refs:
        footprint = new_fps[ref]
        source = f"{footprint[1].split(':', 1)[-1]}.kicad_mod"
        local, rendered = (HARDWARE / LIB / source).read_bytes(), (directory / LIB / source).read_bytes()
        assert local == rendered, source
        assert geometry(footprint) == geometry(sync.sexp(rendered.decode())) == geometry(stage8[ref]), ref
        assert footprint[1] == regenerated[ref]['properties']['Footprint']
        actual[ref] = {'identity': footprint[1], 'pads': geometry(footprint), 'net_mapping': new_nets[ref]}
    assert not (directory / LIB / 'Coilcraft_XFL4020-222MEB.kicad_mod').exists()
    report = {'status': 'PASS', 'changed_footprints': sorted(changed_fps), 'changed_endpoints_mm': endpoints,
              'all_other_board_geometry_identical': True, 'schematic_netlist_identical_to_baseline': True,
              'reproduced_stage7_preliminary_and_stage8': True, 'tested_footprints': actual}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
