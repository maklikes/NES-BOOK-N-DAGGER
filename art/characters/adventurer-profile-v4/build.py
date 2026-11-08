from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
root=Path(__file__).parent
pal_file=Path('/workspace/nes-tools/emulator/root/usr/share/fceux/palettes/Wavebeam.pal').read_bytes()
indices={'D':0x07,'G':0x27,'S':0x37,'B':0x11,'M':0x17}
colors={ch:tuple(pal_file[3*i:3*i+3]) for ch,i in indices.items()}
# Transcription of the user's manual correction onto the native 16x24 grid.
# Keep shoulder/chest depth and a visible arm in front of the tunic.
poses={'perfil':[
'................',
'.....DDDDDD.....',
'....DDGGGGGDD...',
'...DDGGGGGGGDD..',
'...DGGGGGGGGGD..',
'...DGGGDGDGGDD..',
'....DGGDDSSSD...',
'....DGDSDSDSD...',
'....DDSSSSSSD...',
'.....DDSSSSD....',
'......DSSSD.....',
'.....DBBSSBD....',
'.....DBBGBBD....',
'.....DBBBGBD....',
'.....DBBDBGD....',
'.....DBBDBBD....',
'.....DSSDGGD....',
'.....DSSDMMD....',
'.....DDDDMMD....',
'......DMMMD.....',
'......DMMDD.....',
'......DMMDD.....',
'.....DMMMMMD....',
'.....DDDDDDD....']}
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
     if c=='S' and ty>0:c='.'
     assert c in palette,(name,tx,ty,c)
     line.append(palette.index(c))
    pixels.append(line)
   raw=bytes(sum((v&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)+bytes(sum(((v>>1)&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)
   entries.append({'x':tx*8,'y':ty*8,'tile':len(tiles),'palette':ty});tiles.append(raw)
 for ty in (1,2):
  for tx in range(2):
   pixels=[[3 if rows[ty*8+y][tx*8+x]=='S' else 0 for x in range(8)] for y in range(8)]
   raw=bytes(sum((v&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)+bytes(sum(((v>>1)&1)<<(7-i) for i,v in enumerate(r)) for r in pixels)
   entries.append({'x':tx*8,'y':ty*8,'tile':len(tiles),'palette':0});tiles.append(raw)
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
 checks.append(f'{name}: 16x24 RGBA, 10 sprites 8x8, CHR round-trip exact, max {max(counts)} sprites per scanline')
 records[name]={'pixels':rows,'metasprite':entries}
(root/'sprites.json').write_text(json.dumps({'size':[16,24],'palette_indices':[[None]+[indices[c] for c in p[1:]] for p in palettes],'palette_preview':'Wavebeam','poses':records},indent=2))
(root/'validacao.txt').write_text('\n'.join(checks)+'\nNo ROM, emulator execution, animation or palette overlay integration was tested.\n')



board=Image.new('RGB',(880,655),'#f6f0e2');d=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(x,y,text,size=18,heavy=False):
 d.text((x,y),text,font=ImageFont.truetype(bold if heavy else font,size),fill='#3b251b')
label(30,20,'AVENTUREIRO — PERFIL ESTÁTICO v4',27,True)
label(30,61,'Nariz removido e cabelo suavizado conforme a edição manual',17)
for x,folder,title in [(130,root.parent/'adventurer-profile-v3','ANTERIOR — v3'),(500,root,'AJUSTADO — v4')]:
 label(x,112,title,20,True)
 d.rectangle((x,150,x+255,533),fill='#e4ded1')
 im=Image.open(folder/'perfil.png').convert('RGBA')
 big=im.resize((256,384),Image.Resampling.NEAREST)
 board.paste(big,(x,150),big)
 d.rectangle((x,550,x+255,650),fill='#398f32')
 board.paste(im,(x+50,588),im)
 scaled=im.resize((64,96),Image.Resampling.NEAREST)
 board.paste(scaled,(x+145,552),scaled)
label(35,555,'1× / 4×',16)
board.save(root/'prancha-perfil-v4.png')
print('Perfil 16x24; 10 sprites; max 4 sprites per scanline; exact CHR round-trip.')
