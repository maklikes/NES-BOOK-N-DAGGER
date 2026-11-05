"""Run the current binary's checks with matching assembler labels."""
import os
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
repo = base.parents[1]
output = Path('/workspace/artifacts/rom-link')
output.mkdir(parents=True, exist_ok=True)
label = next(line.split()[1] for line in (base / 'build/room.lbl').read_text().splitlines()
             if line.split()[-1] == '.load_scene')
environment = os.environ.copy()
environment['NES_LOADER_PC'] = str(int(label, 16))
environment['NES_LINK_OUTPUT'] = str(output)
report = output / 'validation.txt'
report.unlink(missing_ok=True)
command = ['/workspace/nes-tools/emulator/bin/fceux-headless', '--no-config', '1',
           '--loadlua', str(base / 'check.lua'), str(repo / 'downloads/vinculo-v0.1.nes')]
with (output / 'fceux.log').open('w') as log:
    process = subprocess.run(command, env=environment, stdout=log,
                             stderr=subprocess.STDOUT, timeout=120)
assert process.returncode == 0, 'Emulator exited with an error; inspect fceux.log'
text = report.read_text()
assert text.rstrip().endswith('TOTAL 71 checks passed'), 'Validation incomplete; inspect logs'
print(text)
