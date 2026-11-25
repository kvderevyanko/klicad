"""Check the J6/J9-only controlled metadata delta and native marker identity."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import sys

out = Path(__file__).resolve().parent
hw = out.parents[2]
sys.path.insert(0, str(hw))
from check_board_contract import forms, first, prop_map, sexp

def electrical_netlist(path):
    root = sexp(path.read_text())
    return sorted((first(net, "name")[1],
                   sorted((first(node, "ref")[1], first(node, "pin")[1])
                          for node in forms(net, "node")))
                  for net in forms(first(root, "nets"), "net"))

def native_markers(name):
    data = json.loads((out / name).read_text())
    assert not data['violations'] and not data['unconnected_items']
    return Counter((marker['type'], marker['description'],
                    tuple((item['uuid'], item['description']) for item in marker['items']))
                   for marker in data['schematic_parity'])

pre = out / 'pre-dnp'
board = 'esp32-e220.kicad_pcb'
schematic = 'esp32-e220.kicad_sch'
old_board = (pre / board).read_text()
new_board = (hw / board).read_text()
old_sch = (pre / schematic).read_text()
new_sch = (hw / schematic).read_text()
for ref in ('J6', 'J9'):
    old = next(fp for fp in forms(sexp(old_board), 'footprint') if prop_map(fp)['Reference'] == ref)
    new = next(fp for fp in forms(sexp(new_board), 'footprint') if prop_map(fp)['Reference'] == ref)
    added = [p for p in forms(new, 'property') if p[1] == 'DNP']
    assert 'dnp' in first(old, 'attr') and 'dnp' in first(new, 'attr')
    assert len(added) == 1 and added[0][2] == 'YES' and first(added[0], 'hide')[1] == 'yes'
    assert first(added[0], 'layer')[1] == 'F.Fab'
    new.remove(added[0])
    assert new == old, ref
    old_symbol = next(s for s in forms(sexp(old_sch), 'symbol') if prop_map(s).get('Reference') == ref)
    new_symbol = next(s for s in forms(sexp(new_sch), 'symbol') if prop_map(s).get('Reference') == ref)
    native_flag = first(new_symbol, 'dnp')
    assert native_flag == ['dnp','yes']
    new_symbol.remove(native_flag)
    assert new_symbol == old_symbol and prop_map(old_symbol)['DNP'] == 'YES', ref

assert new_sch.replace(' (dnp yes)', '') == old_sch
normalized_board, count = re.subn(r'^\t\t\(property "DNP" "YES" .*?\n', '', new_board, flags=re.MULTILINE)
assert count == 2 and normalized_board == old_board
nets = electrical_netlist(out/'pre.net')
assert nets == electrical_netlist(out/'post.net')
before = native_markers('pre-native-parity.json')
after = native_markers('post-native-parity.json')
removed = before - after
assert not (after - before)
expected = Counter((kind, 'Footprint ' + ref)
                   for ref in ('J6','J9')
                   for kind in ('footprint_symbol_mismatch','footprint_symbol_field_mismatch'))
assert Counter((kind, items[0][1]) for kind, _, items in removed.elements()) == expected
assert sum(before.values()) == 20 and sum(after.values()) == 16
for name in ('pre-contract','post-contract'):
    assert json.loads((out / (name+'.json')).read_text())['overall_status'] == 'PASS'
for name in ('pre-project-parity','post-project-parity'):
    assert json.loads((out / (name+'.json')).read_text())['status'] == 'PASS'
for name in ('pre-erc','post-erc'):
    d = json.loads((out / (name+'.json')).read_text())
    assert all(not page['violations'] for page in d['sheets'])
for name in (schematic,'esp32-e220.kicad_sym','sym-lib-table'):
    assert (hw/name).read_bytes() == (out/'post-generator'/name).read_bytes(), name

report = {'status':'PASS','native_parity_before':sum(before.values()),
          'native_parity_after':sum(after.values()),'removed':sorted(list(expected.elements())),
          'pin_net_pairs':sum(len(nodes) for _, nodes in nets),'net_count':len(nets),
          'schematic_generator_exact':True,'electrical_connectivity_identical':True,
          'board_delta':'two hidden F.Fab footprint properties DNP=YES',
          'schematic_delta':'two assembly-only DNP flags, J6 and J9',
          'board_sha256':hashlib.sha256((hw/board).read_bytes()).hexdigest(),
          'schematic_sha256':hashlib.sha256((hw/schematic).read_bytes()).hexdigest()}
print(json.dumps(report, indent=2))
