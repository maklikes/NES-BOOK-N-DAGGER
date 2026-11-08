from pathlib import Path
import ast,json
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent/'build';out.mkdir(exist_ok=True)
font={}
for n in ast.parse((root/'game/first-river/assets.py').read_text()).body:
 if isinstance(n,ast.Assign):
  t=n.targets[0]
  if isinstance(t,ast.Name) and t.id=='font':font=ast.literal_eval(n.value)
  elif isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='font':font[ast.literal_eval(t.slice)]=ast.literal_eval(n.value)
def tile(pixels):return bytes(sum((v&1)<<(7-x) for x,v in enumerate(r)) for r in pixels)+bytes(sum(((v>>1)&1)<<(7-x) for x,v in enumerate(r)) for r in pixels)
chrdata=[bytes(16) for _ in range(512)]
for ch,rows in font.items():chrdata[ord(ch)]=tile([[int(c) for c in r.ljust(8,'0')] for r in rows]+[[0]*8])
chrdata[128]=tile([[1]*8 for _ in range(8)])
chrdata[129]=tile([[2 if y==7 and 2<=x<=5 else 1 for x in range(8)] for y in range(8)])
layout=json.loads((root/'art/characters/official-walk-v1/layout.json').read_text())
for pose,name in enumerate(layout['order']):
 data=(root/'art/characters/official-walk-v1'/(name+'.chr')).read_bytes()
 assert len(data)==96
 for i in range(6):chrdata[256+pose*6+i]=data[i*16:(i+1)*16]
(out/'graphics.chr').write_bytes(b''.join(chrdata))
nt=bytearray(1024)
for y in range(6,24):
 for x in range(2,30):nt[y*32+x]=129 if y%4==3 and x%4==3 else 128
for ay in range(8):
 for ax in range(8):
  value=0
  for qy in range(2):
   for qx in range(2):
    tx=ax*4+qx*2;ty=ay*4+qy*2
    if 2<=tx<30 and 6<=ty<24:value|=1<<(qy*4+qx*2)
  nt[960+ay*8+ax]=value
for x,y,text in [(3,2,'CAMINHADA EXTERNA - LAB 01'),(3,3,'DIRECIONAIS: MOVER'),(3,25,'A: FUNDO   B: CAMERA LENTA'),(3,26,'START: PAUSA SELECT: CENTRO')]:
 for i,c in enumerate(text):nt[y*32+x+i]=ord(c)
(out/'screen.nam').write_bytes(nt)
print('15 externally authored poses, copied exactly into sprite pattern table.')
