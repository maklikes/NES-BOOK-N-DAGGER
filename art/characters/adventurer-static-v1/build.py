from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
root=Path(__file__).parent
pal_file=Path('/workspace/nes-tools/emulator/root/usr/share/fceux/palettes/Wavebeam.pal').read_bytes()
indices={'D':0x07,'G':0x27,'S':0x37,'B':0x11,'M':0x17}
colors={ch:tuple(pal_file[3*i:3*i+3]) for ch,i in indices.items()}
poses={
'frente':[
'....DD..........',
'...DGDDDDDDD....',
'..DDGGGGGGGDD...',
'.DDGGGGGGGGGGD..',
'.DGGGGGGGGGGGDD.',
'..DGGGDGGGDDD...',
'..DDGSSDGSSSD...',
'..DSSSDSSDSSD...',
'...DSSSSSSD.....',
'....DSSSSD......',
'....DSSSSD......',
'...DBSSSSBD.....',
'..DBBBGGGGBBD...',
'..DSBBBGGBBSD...',
'..DSBBGGBBBSD...',
'...DBGBBBBBD....',
'...DGGDDGGGD....',
'...DMMDDMMMD....',
'....DMDDMD......',
'....DMDDMD......',
'...DMMDDMMD.....',
'...DMMDDMMMD....',
'...DDDD.DDDD....',
'................'],
'costas':[
'....DD..........',
'...DGDDDDDDD....',
'..DDGGGGGGGDD...',
'.DDGGGGGGGGGGD..',
'.DGGGGGGGGGGGDD.',
'..DGGGGGGGGGDD..',
'..DDGGGGGGGDD...',
'...DGGGGGGGD....',
'....DDGGGDD.....',
'.....DSSSD......',
'....DBSSSBD.....',
'...DBBBBBBBD....',
'..DBGBBBBBBBD...',
'..DSBGGBBBBSD...',
'..DSBBGGBBBSD...',
'...DBBBGGBBD....',
'...DGGDDGGGD....',
'...DMMDDMMMD....',
'....DMDDMD......',
'....DMDDMD......',
'...DMMDDMMD.....',
'...DMMDDMMMD....',
'...DDDD.DDDD....',
'................'],
'perfil':[
'.....DD.........',
'....DGDDDDD.....',
'...DDGGGGGDD....',
'..DDGGGGGGGDD...',
'..DGGGGGGGGGD...',
'...DGGGGDGGDD...',
'...DDGGDSSSD....',
'....DGGDSSDSS...',
'.....DDSSSSSD...',
'......DSSSSD....',
'.....DBSSSD.....',
'.....DBBGBBD....',
'.....DBBGGBBD...',
'.....DBBSSBBD...',
'.....DBBSSBGD...',
'.....DBBBBGGD...',
'.....DGGDDGDD...',
'.....DMMDGMD....',
'......DMDDMD....',
'......DMDDMD....',
'.....DMMMMD.....',
'.....DMMMMMD....',
'.....DDDDDDD....',
'................']}
# Proportion pass: shorten the chin/neck and boots, preserving the selected identity.
poses['frente'][6:16]=[
'..DDSSSSSSDD....','..DSSSDSSDSSD...','...DSSSSSSD.....','...DDSSSSDD.....',
'..DBBSSSSBBBD...','..DBBBBGGBBBD...','..DSBBBGGBBSD...','..DSBBGGBBBSD...',
'...DBGBBBBBD....','...DGGDDGGGD....']
poses['costas'][10:16]=[
'..DBBSSSSBBBD...','..DBGBBBBBBBD...','..DSBGGBBBBSD...','..DSBBGGBBBSD...',
'...DBBBGGBBD....','...DGGDDGGGD....']
for name in ('frente','costas'):
 poses[name][16:24]=['...DMMDDMMGD....','...DMMDDMMMD....','....DMDDMD......','....DMDDMD......','...DMMDDMMD.....','...DDDD.DDDD....','................','................']
poses['perfil'][6:11]=['....DGGDSSSD....','....DGGDSDSSD...','.....DDSSSSSD...','......DSSSD.....','.....DBSSBD.....']
poses['perfil'][16:24]=['.....DGGDDGDD...','.....DMMDGMD....','......DMDDMD....','......DMDDMD....','.....DMMMMMD....','.....DDDDDDD....','................','................']

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

board=Image.new('RGB',(1100,860),'#f6f0e2');d=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def label(x,y,text,size=20,heavy=False):d.text((x,y),text,font=ImageFont.truetype(bold if heavy else font,size),fill='#3b251b')
label(40,24,'AVENTUREIRO — RECONSTRUÇÃO ESTÁTICA',29,True)
label(40,67,'Pixels reais: 16 × 24 por vista • sem alteração da ROM',20)
label(40,105,'Ampliação 12× • linhas marcam os blocos de 8×8 pixels',16)
for x,name,title in [(100,'frente','FRENTE'),(454,'costas','COSTAS'),(808,'perfil','PERFIL DIREITO')]:
 label(x,143,title,18,True)
 for gy in range(3):
  for gx in range(2):d.rectangle((x+gx*96,174+gy*96,x+(gx+1)*96-1,174+(gy+1)*96-1),fill=('#e4ded1' if (gx+gy)%2 else '#ede7da'))
 im=Image.open(root/(name+'.png')).convert('RGBA')
 board.paste(im.resize((192,288),Image.Resampling.NEAREST),(x,174),im.resize((192,288),Image.Resampling.NEAREST))
 for gx in range(3):d.line((x+gx*96,174,x+gx*96,462),fill='#b5aea1',width=1)
 for gy in range(4):d.line((x,174+gy*96,x+192,174+gy*96),fill='#b5aea1',width=1)
 label(x,484,'16 × 24 px',16)
 # A flat neutral green is only a contrast swatch, not game artwork.
 d.rectangle((x-16,540,x+208,688),fill='#398f32')
 small=im.resize((64,96),Image.Resampling.NEAREST)
 board.paste(small,(x+64,565),small)
 board.paste(im,(x+88,721),im)
label(40,514,'Leitura sobre verde • ampliação 4×',18)
label(40,720,'Escala 1× →',17)
label(40,772,'5 cores NES no conjunto • 3 cores + transparência por sprite de hardware',17)
label(40,803,'6 blocos de base + 2 sobreposições para pele/colar • prévia de paleta: Wavebeam',16)
board.save(root/'prancha-aventureiro-16x24.png')
print('\n'.join(checks));print(root/'prancha-aventureiro-16x24.png')
