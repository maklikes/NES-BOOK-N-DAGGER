from pathlib import Path
import ast,json
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent/'build';out.mkdir(exist_ok=True)
source=json.loads((root/'art/characters/adventurer-static-v1/sprites.json').read_text())
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
palettes=[['.','D','G','S'],['.','D','B','G'],['.','D','M','G']]
frames={}
for direction,name in enumerate(['frente','costas','perfil']):
 idle=source['poses'][name]['pixels'];variants=[idle]
 for phase in range(4):
  a=[list(r) for r in idle]
  # Contact poses lower head/upper torso 1 pixel; passing poses return upright.
  if phase in (0,2):
   for y in range(14,0,-1):a[y]=list(idle[y-1])
   a[0]=list('.'*16)
  for y in range(17,24):a[y]=list('.'*16)
  def run(y,x,w,c):
   for xx in range(x,x+w):a[y][xx]=c
  if name=='perfil':
   if phase in (0,2):
    run(17,6,5,'M');run(18,5,3,'D');run(18,9,2,'M');run(19,4,3,'D');run(19,10,2,'M')
    run(20,3,4,'D');run(20,10,3,'M');run(21,3,4,'D');run(21,10,4,'D')
    if phase==2:
     run(19,4,2,'M');run(20,3,3,'M');run(20,10,3,'D')
   else:
    run(17,6,5,'M');run(18,7,3,'D');run(18,10,2,'M');run(19,7,3,'M');run(19,10,2,'D');run(20,7,3,'M');run(21,6,6,'D')
    if phase==3:run(18,6,2,'M');run(19,5,3,'D')
  else:
   run(17,4,3,'M');run(17,9,3,'M')
   if phase in (0,2):
    planted=4 if phase==0 else 9;raised=9 if phase==0 else 4
    run(18,planted,3,'M');run(19,planted,3,'M');run(20,planted,3,'M');run(21,planted-1,4,'D')
    run(18,raised,3,'D');run(19,raised,3,'M');run(20,raised,4,'D')
   else:
    planted=6 if phase==1 else 8;raised=9 if phase==1 else 4
    run(18,planted,2,'M');run(19,planted,2,'M');run(20,planted,2,'M');run(21,planted-1,4,'D')
    run(18,raised,2,'D');run(19,raised,3,'D')
  variants.append([''.join(r) for r in a])
 frames[name]=variants
 for pose,rows in enumerate(variants):
  parts=[]
  for ty in range(3):
   pal=palettes[ty]
   for tx in range(2):
    pixels=[]
    for yy in range(8):
     row=[]
     for xx in range(8):
      c=rows[ty*8+yy][tx*8+xx]
      if c=='S' and ty==1:c='.'
      assert c in pal,(name,pose,ty,c)
      row.append(pal.index(c))
     pixels.append(row)
    parts.append(tile(pixels))
  for tx in range(2):parts.append(tile([[3 if rows[8+y][tx*8+x]=='S' else 0 for x in range(8)] for y in range(8)]))
  for i,t in enumerate(parts):chrdata[256+direction*40+pose*8+i]=t
 # Exact idle data must remain equal to the approved static asset.
 expected=(root/'art/characters/adventurer-static-v1'/(name+'.chr')).read_bytes()
 assert b''.join(chrdata[256+direction*40:256+direction*40+8])==expected
(out/'graphics.chr').write_bytes(b''.join(chrdata))
(out/'frames.json').write_text(json.dumps(frames,indent=2))
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
for x,y,text in [(3,2,'AVENTUREIRO - CAMINHADA'),(3,3,'DIRECIONAIS: MOVER'),(3,25,'A: FUNDO   B: CAMERA LENTA'),(3,26,'START: PAUSA SELECT: CENTRO')]:
 for i,c in enumerate(text):nt[y*32+x+i]=ord(c)
(out/'screen.nam').write_bytes(nt)
print('15 poses, 8 sprites each; idle frames exactly match approved CHR assets.')
