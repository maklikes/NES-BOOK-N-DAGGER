"""Check actual build artifacts for the NES art study."""
from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parent;build=base/'build';repo=base.parents[1]
def unpack(data):
 out=bytearray();i=0
 while True:
  assert i<len(data),'Missing terminator'
  count=data[i];i+=1
  if count==0:break
  if count&128:
   n=count&127;assert n and i+n<=len(data)
   out.extend(data[i:i+n]);i+=n
  else:
   assert i<len(data);out.extend([data[i]]*count);i+=1
 assert i==len(data),'Unused packed bytes'
 return bytes(out)
rom=(repo/'downloads/primeira-pescaria-arte-v0.2.nes').read_bytes()
assert len(rom)==32784 and rom[:16]==b'NES\x1a\x02\x00'+bytes(10)
font=None
for scene in range(3):
 raw=(build/f'background{scene}.chr').read_bytes()
 assert len(raw)==4096 and unpack((build/f'background{scene}.pkb').read_bytes())==raw
 nt=(build/f'room{scene}.nam').read_bytes();assert len(nt)==1024
 assert len((build/f'solid{scene}.bin').read_bytes())==1024
 # The live HUD/dialogues use these ASCII positions in every room.
 glyphs=b''.join(raw[i*16:(i+1)*16] for i in [32,44,46,47,*range(48,59),61,63,*range(65,91)])
 if font is None:font=glyphs
 else:assert glyphs==font,'Font changed between rooms'
sprites=(build/'sprites.chr').read_bytes()
assert len(sprites)==4096 and unpack((build/'sprites.pkb').read_bytes())==sprites
for start in (0,18,36):
 poses=[sprites[(start+i*6)*16:(start+(i+1)*6)*16] for i in range(3)]
 assert len(set(poses))==3,'Walk frames are not distinct'
assert len({sprites[i*16:(i+6)*16] for i in (0,18,36)})==3
labels={line.split()[-1]:int(line.split()[1],16) for line in (build/'river.lbl').read_text().splitlines() if line.strip()}
for name in ('palettes0','palettes1','palettes2'):
 offset=16+labels['.'+name]-0x8000;palette=rom[offset:offset+32]
 assert len(palette)==32 and all(c<64 and c!=0x0d for c in palette)
 assert all(palette[i]==0x0f for i in range(0,32,4))
print('PASS iNES mapper 0, CHR RAM, 32784-byte ROM')
print('PASS PackBits round-trip: three 4 KiB backgrounds and common sprite table')
print('PASS 1 KiB nametables/collision maps and common font')
print('PASS distinct front/back/profile and complete stride poses')
print('PASS legal NES palette entries and shared universal backdrop')
print((build/'art-stats.txt').read_text())
print('SHA256',hashlib.sha256(rom).hexdigest())
