from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
root=Path(__file__).parent
source=json.loads((root.parent/'adventurer-static-v1/sprites.json').read_text())
poses={name:list(p['pixels']) for name,p in source['poses'].items()}
pal_file=Path('/workspace/nes-tools/emulator/root/usr/share/fceux/palettes/Wavebeam.pal').read_bytes()
indices={'D':0x07,'G':0x27,'S':0x37,'B':0x11,'M':0x17}
colors={ch:tuple(pal_file[3*i:3*i+3]) for ch,i in indices.items()}
# Compact cap with small irregular fringe; symmetric short ears.
poses['frente'][:10]=[
'.....DD.DD......',
'....DGGDGGDD....',
'...DGGGGGGGGD...',
'...DGGGGGGGGD...',
'...DGGDGGDGDD...',
'....DSSSSSSD....',
'...DSSDSDSSSD...',
'....DSSSSSSD....',
'.....DSSSSD.....',
'.....DSSSSD.....']
# Same compact silhouette and short nape, with small tufts at the crown.
poses['costas'][:10]=[
'.....DD.DD......',
'....DGGDGGDD....',
'...DGGGGGGGGD...',
'...DGGGGGGGGD...',
'...DGGGGGGGDD...',
'....DGGGGGGD....',
'....DDGGGGDD....',
'.....DGGGGD.....',
'......DDDD......',
'......DSSD......']
# Short nose: face ends at x10. Straight torso: shirt ends at x10.
poses['perfil'][:18]=[
'......DDD.......',
'.....DGGDDD.....',
'....DGGGGGDD....',
'....DGGGGGGD....',
'.....DGGGGGD....',
'.....DGGDSSD....',
'.....DGGDSD.....',
'......DSDSSD....',
'......DSSSD.....',
'.......DSSD.....',
'.....DBSSBD.....',
'.....DBBGBD.....',
'.....DBBGGD.....',
'.....DBBSSD.....',
'.....DBBSSD.....',
'.....DBBGGD.....',
'.....DGGDDD.....',
'.....DMMDDMD....']
# Base tiles have one palette per 8px row. Skin below the first row is
# carried by two middle-row overlay sprites using palette 0.
palettes=[['.','D','G','S'],['.','D','B','G'],['.','D','M','G']]
records={};checks=[]
for name,rows in poses.items():
 assert len(rows)==24
 for y,row in enumerate(rows):assert len(row)==16,(name,y,len(row),row)
 image=Image.new('RGBA',(16,24),(0,0,0,0))
 for y,row in enumerate(rows):
  for x,c in enumerate(row):
   if c!='.':image.putpixel((x,y),colors[c]+(255,))
 image.save(root/(name+'.png'))
 entries=[];tiles=[]
 for ty in range(3):
  palette=palettes[ty]
  for tx in range(2):
   pixels=[]
   for yy in range(8):
    line=[]
    for xx in range(8):
     c=rows[ty*8+yy][tx*8+xx]
     if c=='S' and ty==1:c='.'
     assert c in palette,(name,tx,ty,c)
     line.append(palette.index(c))
    pixels.append(line)
   raw=bytes(sum((v&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)+bytes(sum(((v>>1)&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)
   entries.append({'x':tx*8,'y':ty*8,'tile':len(tiles),'palette':ty});tiles.append(raw)
 for tx in range(2):
  pixels=[[3 if rows[8+y][tx*8+x]=='S' else 0 for x in range(8)] for y in range(8)]
  raw=bytes(sum((v&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)+bytes(sum(((v>>1)&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)
  entries.append({'x':tx*8,'y':8,'tile':len(tiles),'palette':0});tiles.append(raw)
 (root/(name+'.chr')).write_bytes(b''.join(tiles))
 # Decode the exported NES bitplanes and palettes, not the source strings.
 rebuilt=Image.new('RGBA',(16,24),(0,0,0,0))
 for e in entries:
  raw=tiles[e['tile']];pal=palettes[e['palette']]
  for yy in range(8):
   for xx in range(8):
    i=((raw[yy]>>(7-xx))&1)|(((raw[8+yy]>>(7-xx))&1)<<1)
    if i:rebuilt.putpixel((e['x']+xx,e['y']+yy),colors[pal[i]]+(255,))
 assert rebuilt.tobytes()==image.tobytes(),name
 counts=[sum(e['y']<=y<e['y']+8 for e in entries) for y in range(24)]
 assert max(counts)<=8
 checks.append(f'{name}: 16x24 RGBA, 8 sprites 8x8, CHR round-trip exact, max {max(counts)} sprites per scanline')
 records[name]={'pixels':rows,'metasprite':entries}
(root/'sprites.json').write_text(json.dumps({'size':[16,24],'palette_indices':[[None]+[indices[c] for c in p[1:]] for p in palettes],'palette_preview':'Wavebeam','poses':records},indent=2))
(root/'validacao.txt').write_text('\n'.join(checks)+'\nNo ROM, emulator execution, animation or palette overlay integration was tested.\n')


board=Image.new('RGB',(960,780),'#f6f0e2');d=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(x,y,text,size=18,heavy=False):
 d.text((x,y),text,font=ImageFont.truetype(bold if heavy else font,size),fill='#3b251b')
label(30,20,'AVENTUREIRO — AJUSTES DE SILHUETA v2',28,True)
label(30,60,'Sprites reais 16 × 24 px • mesma paleta • ROMs preservadas',18)
for x,name,title in [(160,'frente','FRENTE'),(430,'costas','COSTAS'),(700,'perfil','PERFIL DIREITO')]:
 label(x,105,title,18,True)
 for y,folder in [(148,root.parent/'adventurer-static-v1'),(430,root)]:
  d.rectangle((x-12,y-10,x+140,y+202),fill='#e5decf')
  im=Image.open(folder/(name+'.png')).convert('RGBA')
  big=im.resize((128,192),Image.Resampling.NEAREST)
  board.paste(big,(x,y),big)
  d.rectangle((x-12,y+214,x+140,y+258),fill='#398f32')
  board.paste(im,(x+56,y+223),im)
label(25,210,'ANTES',20,True)
label(25,492,'REVISADO',20,True)
label(30,715,'Ampliação 8× sem suavização; amostras sobre verde em escala 1×.',17)
label(30,744,'Prévia de paleta Wavebeam. Na CRT, o sinal de vídeo muda a leitura das cores.',16)
board.save(root/'prancha-aventureiro-v2-comparacao.png')
print('CHR round-trip exact for all three static poses. No ROM changed.')
