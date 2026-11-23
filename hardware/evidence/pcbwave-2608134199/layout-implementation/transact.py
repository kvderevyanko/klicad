"""Apply one reviewer-approved PCBWAVE physical transaction with rollback."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
HARDWARE = SCOPE.parents[1]
PCB = 'esp32-e220.kicad_pcb'
SCH = 'esp32-e220.kicad_sch'
LIB = 'esp32-e220.pretty'
FOOTPRINTS = 'generate_stage7_footprints.py'
SCHEMATIC = 'generate_esp32_e220.py'
PLACEMENT = 'generate_stage8_placement.py'
PRELIMINARY = 'generate_stage7_preliminary_pcb.py'
BASE = SCOPE / 'baseline' / PCB
PROTECTED = SCOPE / 'l1-plan' / 'expected-protected.kicad_pcb'
TMP = HERE / 'tmp'
ENV = {**os.environ, 'TMPDIR': str(TMP), 'PYTHONDONTWRITEBYTECODE': '1'}

sys.path.insert(0, str(HARDWARE))
import check_schematic_pcb_sync as sync


def run(args, output):
    with output.open('w') as stream:
        subprocess.run(args, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)


def section(text, kind, indent):
    return re.findall(rf'^{indent}\({kind}\b.*?^{indent}\)', text, re.M | re.S)


def by_ref(text, kind, indent):
    return {sync.prop_map(sync.sexp(item))['Reference']: item for item in section(text, kind, indent)}


def replace(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f'expected one occurrence of {before!r}')
    return text.replace(before, after)


def zone_map(text):
    return {sync.first(sync.sexp(zone), 'uuid')[1]: zone for zone in section(text, 'zone', '\t')}


def refill(candidate, scratch):
    board_text = (candidate / PCB).read_text()
    path = scratch / PCB
    shutil.copy2(candidate / PCB, path)
    for name in (SCH, 'esp32-e220.kicad_pro', 'esp32-e220.kicad_sym', 'fp-lib-table', 'sym-lib-table'):
        shutil.copy2(candidate / name, scratch / name)
    (scratch / LIB).symlink_to(candidate / LIB, target_is_directory=True)
    run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--schematic-parity', '--refill-zones', '--save-board',
         '--format', 'json', '--output', str(scratch / 'drc.json'), str(path)], scratch / 'drc.log')
    drc_delta(scratch / 'drc.json')
    current, filled = zone_map(board_text), zone_map(path.read_text())
    assert current.keys() == filled.keys()
    baseline_refill = HERE / 'L1' / 'baseline-refill' / PCB
    unchanged = zone_map(baseline_refill.read_text()) if baseline_refill.exists() else {}
    changed = []
    for uid, zone in current.items():
        old_polygons = section(zone, 'filled_polygon', '\t\t')
        new_polygons = section(filled[uid], 'filled_polygon', '\t\t')
        original_refill = section(unchanged.get(uid, ''), 'filled_polygon', '\t\t')
        normalized = [sync.sexp(p) for p in new_polygons]
        if normalized in ([sync.sexp(p) for p in old_polygons], [sync.sexp(p) for p in original_refill]):
            continue
        changed.append(uid)
        original = zone
        for polygon in old_polygons:
            zone = replace(zone, '\n' + polygon, '')
        zone = zone[:-3] + ''.join('\n' + polygon for polygon in new_polygons) + '\n\t)'
        board_text = replace(board_text, original, zone)
    (candidate / PCB).write_text(board_text)
    return changed


def drc_delta(path):
    result = json.loads(path.read_text())
    baseline = json.loads((SCOPE / 'baseline' / 'drc.json').read_text())
    for field in ('violations', 'unconnected_items', 'schematic_parity'):
        assert result[field] == baseline[field], (path, field)


def check(project, reference, reports, stage):
    board, sch = project / PCB, project / SCH
    run(['python3', str(project / 'check_board_contract.py'), '--board', str(board), '--reference', str(reference),
         '--fast', '--json'], reports / f'{stage}-fast-contract.json')
    run(['python3', str(project / 'check_board_contract.py'), '--board', str(board), '--reference', str(reference),
         '--json'], reports / f'{stage}-contract.json')
    drc = reports / f'{stage}-drc.json'
    run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--schematic-parity', '--refill-zones', '--format', 'json',
         '--output', str(drc), str(board)], reports / f'{stage}-drc.log')
    drc_delta(drc)
    erc = reports / f'{stage}-erc.json'
    run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--exit-code-violations', '--output', str(erc), str(sch)],
        reports / f'{stage}-erc.log')
    run(['python3', str(project / 'check_schematic_pcb_sync.py'), '--pcb', str(board)], reports / f'{stage}-parity.json')
    assert json.loads((reports / f'{stage}-parity.json').read_text())['status'] == 'PASS'


def prepare(candidate, scope, refs, name, trial, description):
    board = (candidate / PCB).read_text()
    sheet = (candidate / SCH).read_text()
    old_board = by_ref(board, 'footprint', '\t')
    old_sheet = by_ref(sheet, 'symbol', '  ')
    planned_board = by_ref((trial / PCB).read_text(), 'footprint', '\t')
    planned_sheet = by_ref((trial / SCH).read_text(), 'symbol', '  ')
    for ref in refs:
        footprint = re.sub(r'\(descr "[^"]*"\)', f'(descr "{description}")', planned_board[ref], count=1)
        board = replace(board, old_board[ref], footprint)
        sheet = replace(sheet, old_sheet[ref], planned_sheet[ref])
    if scope == 'L1':
        for before, after in [('(end 73.15 58.2)', '(end 73.5 57.71)'), ('(start 73.15 54.85)', '(start 73.5 55.34)')]:
            board = replace(board, before, after)
    (candidate / PCB).write_text(board)
    (candidate / SCH).write_text(sheet)

    schematic = (candidate / SCHEMATIC).read_text()
    placement = (candidate / PLACEMENT).read_text()
    footprints = (candidate / FOOTPRINTS).read_text()
    if scope == 'L1':
        old_part, part = 'XFL4020-222MEB', 'XGL4020-222MEC'
        old_description = 'Coilcraft XFL4020-222MEB. Manufacturer recommended land pattern: two 0.98x3.40 mm lands on 3.35-mm centres; dashed mark identifies pin 1/start lead.'
        footprints = replace(footprints, old_description, description)
        footprints = footprints.replace('xfl4020()', 'xgl4020()').replace(old_part, part)
        footprints = footprints.replace('1.675, 0, 0.980', '1.185, 0, 0.980')
        line = '    (LIBRARY / "WorldSemi_WS2812B-V5_PLACEMENT_CANDIDATE_NOT_RELEASED.kicad_mod").unlink(missing_ok=True)\n'
        footprints = replace(footprints, line, line +
                             '    # Remove the obsolete land pattern with incorrectly spaced centres.\n'
                             f'    (LIBRARY / "Coilcraft_{old_part}.kicad_mod").unlink(missing_ok=True)\n')
        schematic = replace(schematic, f'("{old_part}", "Coilcraft_{old_part}")', f'("{part}", "Carrier:{name}")')
        schematic = schematic.replace(old_part, part).replace('https://www.coilcraft.com/getmedia/50632d43-da1e-4cdb-8ab4-3029cab51df3/xfl4020.pdf',
                                                                'https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf')
        placement = placement.replace(old_part, part)
        placement = replace(placement, '    # Straight-line pad-centre planning metrics are approximately: SW->L1.1\n'
                            '    # 3.57 mm, L1.2->C3.1 3.12 mm, VOS->C3.1 2.82 mm, and C3.2->nearest PGND\n'
                            '    # 1.86 mm.  These are planning metrics, not routed lengths or DRC proof.\n',
                            '    # Coilcraft drawing 1529-3 specifies a 2.37-mm land pitch.\n')
        preliminary = candidate / PRELIMINARY
        preliminary.write_text(replace(preliminary.read_text(), old_part, part))
    else:
        generator, width, height = ('uni_royal_0603w', '0.625', '0.80') if scope == 'R2' else ('vishay_crcw0603', '0.750', '1.00')
        insertion = ('def ' + generator + '() -> str:\n'
                     '    return passive(\n'
                     f'        "{name}",\n'
                     f'        "{description}",\n'
                     f'        1.60, 0.80, {width}, {height}, 1.50,\n'
                     '    )\n\n\n')
        anchor = 'def murata_grm21_c3() -> str:'
        footprints = replace(footprints, anchor, insertion + anchor)
        anchor = '        "Resistor_0603_1608Metric.kicad_mod": yageo_rc0603(),\n'
        footprints = replace(footprints, anchor, anchor + f'        "{name}.kicad_mod": {generator}(),\n')
        for ref in refs:
            value = '1M 1%' if ref == 'R2' else '10k 1%'
            schematic = replace(schematic, f'"{ref}": ("{value}", "Resistor_0603_1608Metric")',
                                f'"{ref}": ("{value}", "Carrier:{name}")')
            placement = replace(placement, f'"Resistor_0603_1608Metric", "{ref}"', f'"{name}", "{ref}"')
    for ref in refs:
        line = next(line for line in placement.splitlines() if f'{ref.lower()} = add_footprint' in line)
        placement = replace(placement, line, line + f'\n    {ref.lower()}.SetFPID(pcbnew.LIB_ID("Carrier", "{name}"))')
    for filename, contents in [(SCHEMATIC, schematic), (PLACEMENT, placement), (FOOTPRINTS, footprints)]:
        (candidate / filename).write_text(contents)


def main(scope):
    names = {
        'L1': (('L1',), 'Coilcraft_XGL4020-222MEC', 'l1-plan',
               'Coilcraft XGL4020-222MEC. Drawing 1529-3: two 0.98 x 3.40 mm lands on 2.37-mm centres. Silk marks the start lead at pad 1.'),
        'R2': (('R2',), 'UniRoyal_0603W_Reflow', 'resistor-plan',
               'UNI-ROYAL 0603W reflow lands, V.3 section 8. A=0.875, B=0.625, C=0.800, D=2.125 mm within the four published ranges.'),
        'R8-R9': (('R8', 'R9'), 'Vishay_CRCW0603_Reflow', 'resistor-plan',
                  'Vishay D/CRCW e3 0603 reflow land pattern, document 20035. G 0.75, Y 0.75, X 1.00, Z 2.25 mm.'),
    }
    refs, name, plan, description = names[scope]
    path = HERE / scope
    backup, candidate, scratch = (path / sub for sub in ('named-backup', 'candidate', 'refill'))
    for directory in (backup, candidate, scratch):
        directory.mkdir(parents=True)
    before = BASE if scope == 'L1' else PROTECTED
    check(HARDWARE, before, path, 'pre')
    sources = [PCB, SCH, FOOTPRINTS, SCHEMATIC, PLACEMENT]
    obsolete = f'{LIB}/Coilcraft_XFL4020-222MEB.kicad_mod'
    if scope == 'L1':
        sources.extend((PRELIMINARY, obsolete))
    library_file = f'{LIB}/{name}.kicad_mod'
    assert not (HARDWARE / library_file).exists()
    for filename in sources:
        (backup / filename).parent.mkdir(exist_ok=True)
        shutil.copy2(HARDWARE / filename, backup / filename)
    for filename in (PCB, SCH, FOOTPRINTS, SCHEMATIC, PLACEMENT, PRELIMINARY, 'fp-lib-table', 'sym-lib-table',
                     'esp32-e220.kicad_pro', 'esp32-e220.kicad_sym', 'board_contract.json', 'check_board_contract.py',
                     'check_schematic_pcb_sync.py'):
        shutil.copy2(HARDWARE / filename, candidate / filename)
    shutil.copytree(HARDWARE / LIB, candidate / LIB)
    prepare(candidate, scope, refs, name, SCOPE / plan / scope, description)
    run(['python3', str(candidate / FOOTPRINTS)], path / 'stage7.log')
    changed_zones = refill(candidate, scratch)
    check(candidate, PROTECTED, path, 'scratch')
    print(f'{scope}: isolated checks passed; changed filled zones: {changed_zones}', flush=True)
    try:
        for filename in sources:
            assert (HARDWARE / filename).read_bytes() == (backup / filename).read_bytes()
        for filename in [*sources, library_file]:
            if scope == 'L1' and filename == obsolete:
                (HARDWARE / filename).unlink()
            else:
                shutil.copy2(candidate / filename, HARDWARE / filename)
        check(HARDWARE, PROTECTED, path, 'post')
    except BaseException:
        for filename in sources:
            shutil.copy2(backup / filename, HARDWARE / filename)
        (HARDWARE / library_file).unlink(missing_ok=True)
        check(HARDWARE, before, path, 'restored')
        raise
    (path / 'transaction.json').write_text(json.dumps({'scope': scope, 'changed_footprints': refs,
        'changed_zone_fills': changed_zones, 'changed_route_endpoints': 2 if scope == 'L1' else 0,
        'contract': 'PASS', 'native_drc': 0, 'unconnected': 0, 'native_parity_baseline': 20, 'erc': 0}, indent=2) + '\n')


if __name__ == '__main__':
    main(sys.argv[1])
