"""Export the externally authored matrices exactly; no visual alterations."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('official',ROOT.parent/'main-official-v1/spec.py')
official=importlib.util.module_from_spec(spec);spec.loader.exec_module(official)
poses=json.loads((ROOT/'matrizes.json').read_text())['poses']
order=[f'{phase}_{direction}' for direction in ['DIREITO','FRENTE','COSTAS'] for phase in ['REPOUSO','PASSO_1','PASSO_2','PASSO_3','PASSO_4']]
expected={'DIREITO':official.PROFILE,'FRENTE':official.FRONT,'COSTAS':official.BACK}
images={};records={};report=[]
for pose,name in enumerate(order):
 rows=poses[name]
 assert len(rows)==24 and all(len(r)==16 for r in rows),name
 assert rows[23]=='.'*16
 if name.startswith('REPOUSO'):assert rows==expected[name.split('_')[1]],name
 image=Image.new('RGBA',(16,24))
 for y,row in enumerate(rows):
  for x,char in enumerate(row):image.putpixel((x,y),official.COLORS[char])
 data=bytearray();entries=[]
 for ty in range(3):
  pal=official.PALETTE_SYMBOLS[ty]
  for tx in range(2):
   pix=[]
   for y in range(8):
    row=rows[ty*8+y][tx*8:tx*8+8]
    assert set(row)<=set(pal),(name,ty,row)
    pix.append([pal.index(c) for c in row])
   data.extend(sum((v&1)<<(7-x) for x,v in enumerate(r)) for r in pix)
   data.extend(sum(((v>>1)&1)<<(7-x) for x,v in enumerate(r)) for r in pix)
   entries.append({'x':tx*8,'y':ty*8,'tile':len(entries),'palette':ty})
 assert len(data)==96 and len(entries)==6
 decoded=Image.new('RGBA',(16,24))
 for e in entries:
  raw=data[e['tile']*16:(e['tile']+1)*16];pal=official.PALETTE_SYMBOLS[e['palette']]
  for y in range(8):
   for x in range(8):
    i=((raw[y]>>(7-x))&1)|(((raw[y+8]>>(7-x))&1)<<1)
    decoded.putpixel((e['x']+x,e['y']+y),official.COLORS[pal[i]])
 assert decoded.tobytes()==image.tobytes()
 assert max(sum(e['y']<=y<e['y']+8 for e in entries) for y in range(24))==2
 image.save(ROOT/(name+'.png'));(ROOT/(name+'.chr')).write_bytes(data)
 records[name]={'base_tile':pose*6,'ppu_address':0x1000+pose*96,'metasprite':entries}
 images[name]=image
 report.append(f'{name}: exact 16x24 / 96 bytes CHR; exact decoded RGBA; 6 sprites; 2 per scanline; legal subpalettes; Y23 transparent')
(ROOT/'layout.json').write_text(json.dumps({'palette_indices':official.PALETTE_INDICES,'order':order,'poses':records},indent=2))
(ROOT/'validacao.txt').write_text('\n'.join(report)+'\nAll three idle poses equal immutable official matrices.\n')
board=Image.new('RGB',(1120,1010),'#f6f0e2');draw=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def label(x,y,s,size=18):draw.text((x,y),s,font=ImageFont.truetype(font,size),fill='#30251b')
label(25,15,'MATRIZES EXTERNAS OFICIAIS — CAMINHADA',28)
label(25,55,'Pixels recebidos do usuário; somente correção expressamente indicada em Y=10 das costas.',16)
for col,phase in enumerate(['REPOUSO','PASSO_1','PASSO_2','PASSO_3','PASSO_4']):
 label(170+col*185,100,phase.replace('_',' '),16)
 for row,direction in enumerate(['DIREITO','FRENTE','COSTAS']):
  x=170+col*185;y=145+row*280
  if col==0:label(15,y+90,direction,16)
  im=images[f'{phase}_{direction}'];large=im.resize((128,192),Image.Resampling.NEAREST)
  board.paste(large,(x,y),large)
  draw.rectangle((x,y+200,x+150,y+260),fill='#398f32')
  board.paste(im,(x+20,y+220),im)
  small=im.resize((32,48),Image.Resampling.NEAREST);board.paste(small,(x+90,y+205),small)
label(25,985,'Ampliação 8×; amostras 1× / 2× sobre verde. Não é captura de ROM.',15)
board.save(ROOT/'prancha-matrizes.png')
print('\n'.join(report))
