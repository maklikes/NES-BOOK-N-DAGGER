import os,signal,subprocess,time,re
from pathlib import Path
base=Path(__file__).resolve().parent;repo=base.parents[1]
out=Path('/workspace/artifacts/tutorial-garden');out.mkdir(parents=True,exist_ok=True)
(out/'validation.txt').unlink(missing_ok=True)
env=os.environ.copy();env['NES_GARDEN_OUTPUT']=str(out)
cmd=['/workspace/nes-tools/emulator/bin/fceux-headless','--no-config','1','--loadlua',str(base/'check.lua'),str(repo/'downloads/exercicio-pixelorama-jardim-v0.1.nes')]
with (out/'fceux.log').open('w') as log:
 p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  start=time.monotonic()
  while p.poll() is None:
   time.sleep(.25)
   text=(out/'fceux.log').read_text()
   if 'Lua thread bombed out' in text or time.monotonic()-start>180:
    raise RuntimeError(text[-2500:])
  assert p.returncode==0,p.returncode
 finally:
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=5)
text=(out/'validation.txt').read_text()
assert re.search(r'TOTAL \d+ checks passed\s*$',text),text[-1500:]
print(text)
