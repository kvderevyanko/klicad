"""Build isolated KiCad projects to test prescribed footprint and endpoint deltas."""
from pathlib import Path
import re
import shutil
import sys

scope = Path(__file__).resolve().parents[1]
hw = scope.parents[1]
baseline = scope / 'baseline'
which = sys.argv[1]
dest = scope / ('l1-plan' if which == 'L1' else 'resistor-plan') / which
dest.mkdir(exist_ok=True)
for name in ['esp32-e220.kicad_pro', 'esp32-e220.kicad_sym', 'fp-lib-table', 'sym-lib-table']:
    shutil.copy2(hw/name,dest/name)
lib = dest / 'esp32-e220.pretty'
shutil.copytree(hw/'esp32-e220.pretty', lib, dirs_exist_ok=True)
basepcb = (baseline/'esp32-e220.kicad_pcb').read_text()
sch = (baseline/'esp32-e220.kicad_sch').read_text()
libname = 'Resistor_0603_1608Metric'
if which == 'L1':
    libname = 'Coilcraft_XFL4020-222MEB'
    name = 'Coilcraft_XGL4020-222MEC'
    previous, target = '1.675','1.185'
    size, newsize = ('0.98','3.4'),('0.98','3.4')
    desc = 'Coilcraft XGL4020-222MEC. Document 1529-3. Land centres 2.37 mm. Marked start lead at pad 1.'
    refs = {'L1'}
elif which == 'R8-R9':
    name = 'Vishay_CRCW0603_Reflow'
    previous, target = '0.85','0.75'
    size, newsize = ('0.9','0.8'),('0.75','1')
    desc = 'Vishay D/CRCW e3 0603 reflow land pattern, document 20035. G 0.75, Y 0.75, X 1.00, Z 2.25 mm.'
    refs = {'R8','R9'}
elif which == 'R2':
    name='UniRoyal_0603W_Reflow'
    previous, target = '0.85',sys.argv[2]
    size, newsize = ('0.9','0.8'),(sys.argv[3],sys.argv[4])
    desc='UNI-ROYAL 0603W reflow land pattern.'
    refs={'R2'}
else:
    raise ValueError(which)
def update_geometry(s):
    s = re.sub(r'\(at (-?)'+re.escape(previous)+r'0* 0(?=[ .)])',
               lambda m: f'(at {m[1]}{target} 0', s)
    s = re.sub(r'\(size '+re.escape(size[0])+r'0* '+re.escape(size[1])+r'0*\)',
               f'(size {newsize[0]} {newsize[1]})',s)
    s=re.sub(r'\(descr "[^"]*"\)',f'(descr "{desc}")',s)
    if which == 'L1':
        s=s.replace('XFL4020-222MEB', 'XGL4020-222MEC')
    return s
lib_text=update_geometry((lib/(libname+'.kicad_mod')).read_text()).replace(f'"{libname}"',f'"{name}"')
(lib/(name+'.kicad_mod')).write_text(lib_text)
def change_fp(m):
    s=m[0]
    if not any(f'(property "Reference" "{r}"' in s for r in refs):return s
    return update_geometry(s.replace(f'(footprint "{libname}"',f'(footprint "Carrier:{name}"'))
pcb=re.sub(r'^\t\(footprint .*?^\t\)',change_fp,basepcb,flags=re.M|re.S)
if which=='L1':
    for a,b in [('(end 73.15 58.2)','(end 73.5 57.71)'),('(start 73.15 54.85)','(start 73.5 55.34)')]:
        assert pcb.count(a)==1,a
        pcb=pcb.replace(a,b)
def change_sch(m):
    s=m[0]
    if any(f'(property "Reference" "{r}"' in s for r in refs):
        s=s.replace(f'"{libname}"',f'"Carrier:{name}"')
        if which=='L1':s=s.replace('XFL4020-222MEB','XGL4020-222MEC')
    return s
sch=re.sub(r'^  \(symbol \(lib_id .*?^  \)',change_sch,sch,flags=re.M|re.S)
(dest/'esp32-e220.kicad_pcb').write_text(pcb)
(dest/'esp32-e220.kicad_sch').write_text(sch)
