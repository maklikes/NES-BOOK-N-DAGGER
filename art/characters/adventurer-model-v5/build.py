from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
root=Path(__file__).parent
pal_file=Path('/workspace/nes-tools/emulator/root/usr/share/fceux/palettes/Wavebeam.pal').read_bytes()
indices={'D':0x07,'G':0x27,'S':0x37,'B':0x11,'M':0x17}
colors={ch:tuple(pal_file[3*i:3*i+3]) for ch,i in indices.items()}
# Front and back reconstructed to match the user-approved profile v4.
reference=json.loads((root.parent/'adventurer-profile-v4/sprites.json').read_text())
poses={
'frente': [
 '................',
 '.....DDDDDD.....',
 '...DDGGGGGGDD...',
 '..DDGGGGGGGGDD..',
 '..DGGGGGGGGGGD..',
 '..DGGDGGDGGGGD..',
 '...DGSSSSSSGD...',
 '...DSSSSSSSSD...',
 '...DSDSSSSDSD...',
 '....DSSSSSSD....',
 '.....DSSSSD.....',
 '...DBBSSSSBBD...',
 '...DBBBBGGBBD...',
 '...DSBBGGBBSD...',
 '...DSBGGBBBSD...',
 '...DSBGBBBBSD...',
 '...DSGGGGGGSD...',
 '...DSMMMMMMSD...',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '...DMMMDDMMMD...',
 '...DDDD..DDDD...',
],
'costas': [
 '................',
 '.....DDDDDD.....',
 '...DDGGGGGGDD...',
 '..DDGGGGGGGGDD..',
 '..DGGGGGGGGGGD..',
 '..DGGGGGGGGGGD..',
 '...DGGGGGGGGD...',
 '...DGGGGGGGGD...',
 '....DGGGGGGD....',
 '.....DDGGDD.....',
 '.....DSSSSD.....',
 '...DBBSSSSBBD...',
 '...DBGBBBBBBD...',
 '...DSBGGBBBSD...',
 '...DSBBGGBBSD...',
 '...DSBBBGGBSD...',
 '...DSGGGGGGSD...',
 '...DSMMMMMMSD...',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '....DMMDDMMD....',
 '...DMMMDDMMMD...',
 '...DDDD..DDDD...',
],
}
poses['perfil']=reference['poses']['perfil']['pixels']
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



board=Image.new('RGB',(1050,735),'#f6f0e2');d=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(x,y,text,size=18,heavy=False):
 d.text((x,y),text,font=ImageFont.truetype(bold if heavy else font,size),fill='#3b251b')
label(30,20,'AVENTUREIRO — MODELO ESTÁTICO v5',29,True)
label(30,66,'Frente e costas propostas • perfil v4 preservado • sprites reais de 16 × 24 px',18)
for x,name,title in [(90,'frente','FRENTE'),(420,'costas','COSTAS'),(750,'perfil','PERFIL DIREITO')]:
 label(x,115,title,20,True)
 d.rectangle((x,155,x+191,442),fill='#e4ded1')
 im=Image.open(root/(name+'.png')).convert('RGBA')
 big=im.resize((192,288),Image.Resampling.NEAREST)
 board.paste(big,(x,155),big)
 for y,color in [(474,'#398f32'),(580,'#eed8ac')]:
  d.rectangle((x,y,x+191,y+99),fill=color)
  board.paste(im,(x+30,y+38),im)
  scaled=im.resize((64,96),Image.Resampling.NEAREST)
  board.paste(scaled,(x+110,y+2),scaled)
label(30,456,'Ampliação 12× acima; amostras 1× e 4× em cada fundo abaixo.',16)
label(30,704,'Mesma paleta NES • prévia Wavebeam • nenhuma alteração de ROM ou animação',17)
board.save(root/'prancha-modelo-v5.png')
assert (root/'perfil.png').read_bytes()==(root.parent/'adventurer-profile-v4/perfil.png').read_bytes()
assert (root/'perfil.chr').read_bytes()==(root.parent/'adventurer-profile-v4/perfil.chr').read_bytes()
print('Three poses exported and decoded exactly; profile v4 PNG and CHR unchanged.')
