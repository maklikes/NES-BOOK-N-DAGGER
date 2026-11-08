"""Four exact-pixel lateral walking frames; official idle remains immutable."""
from pathlib import Path
import importlib.util
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
spec_path=ROOT.parent/'main-official-v1/spec.py'
module=importlib.util.spec_from_file_location('official',spec_path)
spec=importlib.util.module_from_spec(module);module.loader.exec_module(spec)
COLORS=spec.COLORS
# Each leg is drawn as a one-pixel brown core with black outline. The
# visible pair trades leading/trailing roles in the second half of the cycle.
legs=[
 ['.....KBBBK......','....KBBKBBK.....','....KBKKBBK.....','...KBK..KBBK....','...KBK...KBK....','..KBBK...KBBK...','..KKKK...KKKK...'],
 ['.....KBBBK......','.....KBBBK......','....KBBKBK......','....KBKKBK......','....KK.KBK......','.......KBBK.....','.......KKKK.....'],
 ['.....KBBBK......','.....KBBKBBK....','....KBBKKBBK....','....KBK..KBBK...','...KBK....KBK...','..KBBK....KBBK..','..KKKK....KKKK..'],
 ['.....KBBBK......','.....KBBBK......','.....KBKBBK.....','.....KBKKBBK....','.....KBK.KK.....','.....KBBK.......','.....KKKK.......'],
]
# Small arm swing, confined to the torso palette band. Keep the tunic hem
# and head fixed; avoid changing hair or shifting tiles across palette bands.
arm_rows=[
 {10:'..KUUUKUUUSK....',11:'..KUUKUUUUSK....',12:'...KSSSUUUUK....'},
 {10:spec.PROFILE[10],11:spec.PROFILE[11],12:spec.PROFILE[12]},
 {10:'..KUUUKUUUSK....',11:'..KUUUUKUUSK....',12:'...KUUUUSSSK....'},
 {10:'..KUUUKUUUSK....',11:'..KUUUUKUUSK....',12:'...KUUSSSUUK....'},
]
frames={'repouso':list(spec.PROFILE)}
for i in range(4):
 rows=list(spec.PROFILE)
 rows[16:23]=legs[i]
 for y,row in arm_rows[i].items():rows[y]=row
 frames[f'passo-{i+1}']=rows
records={};images={};report=[]
for name,rows in frames.items():
 assert len(rows)==24 and all(len(r)==16 for r in rows),(name,[(i,len(r)) for i,r in enumerate(rows) if len(r)!=16])
 assert rows[:8]==spec.PROFILE[:8] and rows[15]==spec.PROFILE[15] and rows[23]=='.'*16
 image=Image.new('RGBA',(16,24))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):image.putpixel((x,y),COLORS[c])
 tiles=[];entries=[]
 for ty in range(3):
  pal=spec.PALETTE_SYMBOLS[ty]
  for tx in range(2):
   pix=[]
   for y in range(8):
    row=rows[ty*8+y][tx*8:tx*8+8]
    assert set(row)<=set(pal),(name,ty,row)
    pix.append([pal.index(c) for c in row])
   raw=bytes(sum((v&1)<<(7-x) for x,v in enumerate(r)) for r in pix)
   raw+=bytes(sum(((v>>1)&1)<<(7-x) for x,v in enumerate(r)) for r in pix)
   entries.append({'x':tx*8,'y':ty*8,'tile':len(tiles),'palette':ty});tiles.append(raw)
 data=b''.join(tiles)
 assert len(data)==96 and len(entries)==6
 decoded=Image.new('RGBA',(16,24))
 for e in entries:
  raw=tiles[e['tile']];pal=spec.PALETTE_SYMBOLS[e['palette']]
  for y in range(8):
   for x in range(8):
    index=((raw[y]>>(7-x))&1)|(((raw[y+8]>>(7-x))&1)<<1)
    decoded.putpixel((e['x']+x,e['y']+y),COLORS[pal[index]])
 assert decoded.tobytes()==image.tobytes()
 assert max(sum(e['y']<=y<e['y']+8 for e in entries) for y in range(24))==2
 image.save(ROOT/(name+'.png'));(ROOT/(name+'.chr')).write_bytes(data)
 records[name]={'pixels':rows,'metasprite':entries};images[name]=image
 report.append(f'{name}: 16x24; 6 sprites; 2 sprites/scanline; no overlays; exact CHR round-trip; head/hem unchanged')
assert (ROOT/'repouso.chr').read_bytes()==(ROOT.parent/'main-official-v1/perfil.chr').read_bytes()
assert (ROOT/'repouso.png').read_bytes()==(ROOT.parent/'main-official-v1/perfil.png').read_bytes()
assert len({tuple(frames[f'passo-{i}']) for i in range(1,5)})==4
(ROOT/'frames.json').write_text(json.dumps({'size':[16,24],'palette_indices':spec.PALETTE_INDICES,'frame_ticks':8,'target_fps':60,'sequence':['passo-1','passo-2','passo-3','passo-4'],'frames':records},indent=2))
(ROOT/'validacao.txt').write_text('\n'.join(report)+'\nOfficial idle PNG and CHR identical; no ROM or execution test.\n')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def text(draw,x,y,s,size=18,strong=False):draw.text((x,y),s,font=ImageFont.truetype(bold if strong else font,size),fill='#30251b')
board=Image.new('RGB',(1140,610),'#f6f0e2');d=ImageDraw.Draw(board)
text(d,25,18,'AVENTUREIRO — CAMINHADA LATERAL v1',28,True)
text(d,25,60,'Repouso oficial intacto + quatro fases propostas • 16 × 24 px • sem overlays',18)
for i,(name,title) in enumerate([('repouso','REPOUSO'),('passo-1','1 — CONTATO A'),('passo-2','2 — PASSAGEM A'),('passo-3','3 — CONTATO B'),('passo-4','4 — PASSAGEM B')]):
 x=30+i*220;text(d,x,107,title,16,True)
 im=images[name];large=im.resize((160,240),Image.Resampling.NEAREST)
 d.rectangle((x,145,x+159,384),fill='#e4ded1');board.paste(large,(x,145),large)
 for y,color in [(405,'#398f32'),(500,'#eed8ac')]:
  d.rectangle((x,y,x+179,y+89),fill=color)
  board.paste(im,(x+20,y+33),im)
  small=im.resize((48,72),Image.Resampling.NEAREST);board.paste(small,(x+100,y+10),small)
text(d,25,592,'Acima 10×; abaixo 1× / 3×. Cabeça fixa; ciclo 1 → 2 → 3 → 4.',13)
board.save(ROOT/'prancha-caminhada-lateral.png')
# Compare silhouettes against the same fixed backgrounds; no CRT filtering.
gifframes=[]
for name in ['passo-1','passo-2','passo-3','passo-4']:
 canvas=Image.new('RGB',(760,370),'#f6f0e2');g=ImageDraw.Draw(canvas)
 text(g,20,15,'CAMINHADA LATERAL — PRÉVIA DE PIXELS',22,True)
 text(g,20,48,'1× / 4× / 5× • ciclo no lugar • mesma cadência em todas as escalas',15)
 for y,color in [(85,'#398f32'),(225,'#eed8ac')]:
  g.rectangle((20,y,740,y+129),fill=color)
  im=images[name]
  for x,scale in [(95,1),(245,4),(490,5)]:
   pic=im.resize((16*scale,24*scale),Image.Resampling.NEAREST)
   canvas.paste(pic,(x,y+126-24*scale),pic)
 gifframes.append(canvas)
# Keep exact RGB colors: one common palette, no dithering, no blending.
palette=Image.new('P',(1,1))
colors=[tuple(c[:3]) for k,c in COLORS.items() if k!='.']
colors += [(57,143,50),(238,216,172),(246,240,226),(48,37,27)]
quantized=gifframes[0].quantize(colors=64,method=Image.Quantize.MEDIANCUT).getpalette()
for i in range(0,len(quantized),3):
 c=tuple(quantized[i:i+3])
 if c not in colors:colors.append(c)
colors=colors[:256];colors += [(0,0,0)]*(256-len(colors))
palette.putpalette([v for c in colors for v in c])
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in gifframes]
for frame,name in zip(indexed,['passo-1','passo-2','passo-3','passo-4']):
 original=images[name]
 rgb=frame.convert('RGB')
 for y in range(24):
  for x in range(16):
   rgba=original.getpixel((x,y))
   if rgba[3]:assert rgb.getpixel((95+x,85+126-24+y))==rgba[:3]
indexed[0].save(ROOT/'caminhada-lateral.gif',save_all=True,append_images=indexed[1:],duration=130,loop=0,disposal=2,optimize=False)
indexed[0].save(ROOT/'caminhada-lateral-lenta.gif',save_all=True,append_images=indexed[1:],duration=260,loop=0,disposal=2,optimize=False)
print('\n'.join(report))
