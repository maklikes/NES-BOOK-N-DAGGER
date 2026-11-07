from pathlib import Path
import math
out=Path(__file__).parent/"build"
out.mkdir(exist_ok=True)
font={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'.':['000','000','000','000','000','011','011'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['010','110','010','010','010','010','111'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
':':['0','1','0','0','1','0','0'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
}
font[',']=['000','000','000','000','000','110','100']
font['K']=['10001','10010','10100','11000','10100','10010','10001']
font['/']=['00001','00001','00010','00100','01000','10000','10000']
font['!']=['010','010','010','010','010','000','010']
font['?']=['01110','10001','00001','00010','00100','00000','00100']
font['=']=['00000','00000','11111','00000','11111','00000','00000']
def tile(rows):
 rows=[[int(v) for v in row] for row in rows]
 return bytes(sum((v&1)<<(7-x) for x,v in enumerate(row)) for row in rows)+bytes(sum(((v>>1)&1)<<(7-x) for x,v in enumerate(row)) for row in rows)
chrtiles=[bytes(16) for _ in range(512)]
for ch,rows in font.items():chrtiles[ord(ch)]=tile([r.ljust(8,'0') for r in rows]+['00000000'])
patterns={
128:['11111111','11121111','11111111','11111111','12111111','11111111','11111211','11111111'], # grass
129:['11111111','11111111','11111111','11211111','11111111','11111111','11111111','11111111'], # earth
130:['22222222','21111112','21111112','21111112','22222222','11112111','11112111','11112111'], # plank
131:['33333333','22222222','11111111','11111111','11111111','11111111','11111111','22222222'],
132:['22222222','23333332','23111132','23111132','23111132','23111132','23333332','22222222'],
133:['11111111','11111111','11222111','12232211','11222111','11121111','11121111','11111111'], # flower
134:['11111111','11111111','11222211','12222221','12222221','11222211','11111111','11111111'], # rock
135:['11111111','11111111','12111111','11222211','11111111','11111111','11111211','11222111'], # water
136:['11111111','11111111','12111111','11222211','11111111','11111111','11111211','11222111'],
137:['33333333','32222223','32111123','32111123','32111123','32111123','32222223','33333333'],
138:['11111111','12121212','11212121','12121212','11111111','12121212','11212121','33333333'], # woven basket
139:['11111111','11111111','11111111','11111111','11111111','11111111','11111111','11111111'],
140:['11111111','11111111','11111111','11111111','11111111','11111111','33333333','22222222'], # bank
}
for i,rows in patterns.items():chrtiles[i]=tile(rows)
next_tile=144
maps=[bytearray(1024) for _ in range(3)]
solids=[bytearray([1]*1024) for _ in range(3)]
pals=[[[0]*16 for _ in range(15)] for _ in range(3)]
def cell(scene,x,y,t,pal,solid=False):
 if not (0<=x<32 and 0<=y<30):raise ValueError((x,y))
 maps[scene][y*32+x]=t;solids[scene][y*32+x]=int(solid)
 pals[scene][y//2][x//2]=pal

def fill(scene,x,y,w,h,t,pal,solid=False):
 for yy in range(y,y+h):
  for xx in range(x,x+w):cell(scene,xx,yy,t,pal,solid)

def obj(scene,x,y,pixels,pal,foot=None):
 global next_tile
 h=len(pixels);w=len(pixels[0]);assert w%8==0 and h%8==0
 for ty in range(h//8):
  for tx in range(w//8):
   # Deduplication shares tiles across every room and object.
   raw=tile([r[tx*8:tx*8+8] for r in pixels[ty*8:ty*8+8]])
   try:index=chrtiles.index(raw,128,next_tile)
   except ValueError:index=next_tile;chrtiles[index]=raw;next_tile+=1
   cell(scene,x+tx,y+ty,index,pal,False)
 if foot:
  fx,fy,fw,fh=foot
  for yy in range(fy,fy+fh):
   for xx in range(fx,fx+fw):solids[scene][yy*32+xx]=1

def canvas(w,h,c=0):return [[c]*w for _ in range(h)]
def rect(a,x,y,w,h,c):
 for yy in range(y,y+h):
  for xx in range(x,x+w):a[yy][xx]=c

def rows(a):return [''.join(map(str,r)) for r in a]

def text(scene,x,y,s):
 for i,c in enumerate(s):maps[scene][y*32+x+i]=ord(c)

# CABIN: timber, rug, hearth, bed and a storage basket.
fill(0,2,6,28,18,130,1,True)
fill(0,3,7,26,16,130,1)
for y in range(6,24):cell(0,2,y,137,1,True);cell(0,29,y,137,1,True)
fill(0,2,6,28,1,131,1,True);fill(0,2,23,28,1,131,1,True)
fill(0,14,23,4,1,139,1)
fill(0,11,13,10,7,138,2)
# Bed, 32x32, at left of back wall.
a=canvas(32,32,1);rect(a,0,0,32,3,3);rect(a,0,3,3,27,2);rect(a,29,3,3,27,2)
rect(a,4,4,24,8,3);rect(a,4,14,24,15,2);rect(a,4,16,24,2,3);rect(a,4,30,3,2,3);rect(a,25,30,3,2,3)
obj(0,4,8,rows(a),1,(4,9,4,3))
# Hearth: brick surround, orange flame suggested by palette.
a=canvas(32,32,1);rect(a,0,0,32,5,3);rect(a,3,5,5,25,2);rect(a,24,5,5,25,2);rect(a,8,7,16,23,0)
for yy in range(16,29):
 for xx in range(9,23):
  if abs(xx-16)<(yy-13)//2:a[yy][xx]=3 if (xx+yy)%3 else 2
rect(a,0,29,32,3,3)
obj(0,24,7,rows(a),1,(24,8,4,3))
# Basket deliberately clear, in front of the bed.
fill(0,5,15,3,2,138,1,True)
# A small wall window.
fill(0,14,8,4,3,132,3,True)

# PATH: grass and a gentle bend; the house entrance is at the north.
fill(1,0,6,32,18,128,2)
fill(1,13,6,5,11,129,1)
fill(1,13,13,19,5,129,1)
# The house entrance, framed rather than an obstructive large roof.
fill(1,11,6,9,3,131,1,True);fill(1,13,7,5,3,130,1)
fill(1,13,6,5,1,139,1)
for x in range(0,32):
 cell(1,x,6,128,2,True);cell(1,x,23,128,2,True)
fill(1,13,6,5,1,139,1)
for y in range(6,24):cell(1,0,y,128,2,True)
# River room.
fill(2,0,6,19,18,128,2)
fill(2,0,13,19,5,129,1)
fill(2,19,6,13,18,135,3,True)
for y in range(6,24):cell(2,18,y,140,2)
# A quiet opposite bank and rocks in the water.
fill(2,29,6,3,18,128,2,True)
fill(2,25,10,2,2,134,3,True)
fill(2,27,19,2,2,134,3,True)

# Trees use a 32x40 silhouette with a trunk; shared across outdoor rooms.
a=canvas(32,40,1)
for yy in range(32):
 for xx in range(32):
  radius=15-abs(yy-15)*.38
  if abs(xx-15.5)<radius:a[yy][xx]=2 if ((xx*3+yy*5)%13)<5 else 3
rect(a,13,29,6,11,2);rect(a,15,30,2,10,0)
tree=rows(a)
for sc,x,y in [(1,2,6),(1,23,6),(1,3,18),(1,24,19),(2,1,6),(2,10,6),(2,3,19),(2,11,19)]:
 obj(sc,x,y,tree,2,(x+1,y+3,2,2))
# Scattered flowers, weeds and rocks off the main paths.
for sc in (1,2):
 for x,y in [(8,9),(9,19),(6,17),(20,20),(21,9),(10,11),(7,21)]:
  if sc==2 and x>=18:continue
  if solids[sc][y*32+x]==0 and maps[sc][y*32+x]==128:cell(sc,x,y,133,2)
# Simple sign on the path.
fill(1,22,11,2,1,137,1,True);cell(1,23,12,131,1,True)
# Keep screen edges and HUD outside the walkable world.
for sc in range(3):
 for y in range(30):
  for x in range(32):
   if y<6 or y>=24:solids[sc][y*32+x]=1
 text(sc,3,2,['CABANA DO RIO','CAMINHO DO RIACHO','RIACHO TRANQUILO'][sc])
 # HUD row 3 will be populated by the program.
 for ay in range(8):
  for ax in range(8):
   value=0
   for qy in range(2):
    for qx in range(2):
     ty=ay*2+qy;tx=ax*2+qx
     pal=pals[sc][ty][tx] if ty<15 else 0
     if ty<3 or ty>=12:pal=0
     value|=pal<<(qy*4+qx*2)
   maps[sc][960+ay*8+ax]=value
 (out/f'room{sc}.nam').write_bytes(maps[sc])
 (out/f'solid{sc}.bin').write_bytes(solids[sc])
assert next_tile<=256,next_tile

# Character frames: 16x24, original hand drawn. Idle plus two walking poses.
hero=['0000011111100000','0000111111110000','0001111111111000','0001122222211000','0001222222221000','0001221221221000','0001222222221000','0000122222210000','0000033333300000','0000333333330000','0002333333332000','0002333333332000','0002333333332000','0002333333332000','0000333333330000','0000333333330000','0000333333330000','0000333333330000','0000011001100000','0000011001100000','0000011001100000','0000011001100000','0000111001110000','0000111001110000']
def metasprite(index,bitmap):
 for yy in range(3):
  for xx in range(2):chrtiles[256+index+yy*2+xx]=tile([r[xx*8:xx*8+8] for r in bitmap[yy*8:yy*8+8]])
metasprite(0,hero)
walk1=hero[:18]+['0000111001100000','0000111001100000','0000111001100000','0000111001100000','0001110001110000','0001110001110000']
walk2=hero[:18]+['0000011011100000','0000011011100000','0000011011100000','0000011011100000','0000111000111000','0000111000111000']
metasprite(6,walk1);metasprite(12,walk2)
mom=hero.copy();mom[16:]=['0003333333333000','0003333333333000','0003333333333000','0003333333333000','0003333333333000','0003333333333000','0000111001110000','0000111001110000'];metasprite(18,mom)
orc=hero.copy();orc[4]='0012222222222100';orc[5]='0012212222122100';metasprite(24,orc)
sprites={
30:['00000000','00000000','00300000','03330000','00300000','00000003','00000033','00000003'],
31:['00000000','00000000','00000300','00003330','00000300','30000000','33000000','30000000'],
32:['00000000','00000000','00030000','00333000','00030000','00000000','00000000','00000000'],
33:['00000000','00000000','00000000','00000000','00000000','00000000','00000000','00000000'],
34:['30000000','03000000','00300000','00030000','00003000','00000300','00000030','00000003'],
35:['30000000','03000000','00300000','00030000','00003000','00000300','00000030','00000003'],
}
for index,bitmap in sprites.items():chrtiles[256+index]=tile(bitmap)
(out/'graphics.chr').write_bytes(b''.join(chrtiles))

def panel(*lines):
 assert len(lines)==3
 assert all(len(line)<=28 for line in lines),lines
 return b''.join(('  '+line).ljust(32).encode('ascii') for line in lines)
messages=[
 panel('MAE: TRAGA DOIS PEIXES','PARA O JANTAR, MEU FILHO.','A OU B: CONTINUAR'), #0
 panel('A CONVERSAR OU EXAMINAR','CESTO: GUARDAR OS PEIXES','START: PAUSA'), #1 cabin
 panel('SIGA A TRILHA ATE O RIACHO.','A CONVERSAR OU EXAMINAR','START: PAUSA'), #2 path
 panel('A PESCAR JUNTO AO BRILHO','B OU DIRECIONAL: PARAR','BOLSA CHEIA? VOLTE A CABANA.'), #3 river
 panel('AINDA FALTAM PEIXES.','DOIS BASTAM PARA O JANTAR.','A OU B: CONTINUAR'), #4
 panel('MAE: OBRIGADA! O JANTAR','ESTA GARANTIDO. GUARDE','O QUE SOBROU NO CESTO.'), #5
 panel('MAE: JA TEMOS O JANTAR.','PODE PESCAR MAIS UM POUCO.','A OU B: CONTINUAR'), #6
 panel('VOCE GUARDOU OS PEIXES.','A BOLSA ESTA MAIS LEVE.','PODE VOLTAR AO RIACHO.'), #7
 panel('NAO HA PEIXES NA BOLSA.','O CESTO ESTA PRONTO.','A OU B: CONTINUAR'), #8
 panel('VOCE RECOLHE A LINHA.','O RIO CONTINUA SEU CAMINHO.','A: PESCAR NOVAMENTE'), #9
 panel('BOLSA CHEIA: 6 PEIXES.','VOLTE PARA GUARDAR OU','ENTREGAR O JANTAR.'), #10
 panel('O BRILHO MUDOU DE LUGAR.','PROCURE O NOVO PONTO.','A: PESCAR PERTO DO BRILHO'), #11
 panel('VOCE LANCA A LINHA.','AGUARDE A MORDIDA...','B OU DIRECIONAL: PARAR'), #12
 panel('UM PEIXE ENTROU NA BOLSA!','A PESCARIA CONTINUA.','B OU DIRECIONAL: PARAR'), #13
 panel('ORC: PROCURE O BRILHO.','O RIO SEMPRE MUDA.','A OU B: CONTINUAR'), #14
 panel('PESCO AQUI HA MUITO TEMPO.','ANTES DESTA MARGEM','SER CHAMADA DE HUMANA.'), #15
 panel('A PLACA APONTA PARA LESTE.','RIACHO - BOA PESCARIA!','A OU B: CONTINUAR'), #16
 panel('O FOGO AQUECE A CABANA.','A CASA CHEIRA A MADEIRA.','A OU B: CONTINUAR'), #17
 panel('NADA PARA EXAMINAR AQUI.','EXPLORE COM OS DIRECIONAIS.','A: INTERAGIR'), #18
 panel('ESSE PONTO NAO ESTA ATIVO.','PROCURE O BRILHO NA AGUA.','A: TENTAR NOVAMENTE'), #19
 panel('O CESTO CHEGOU A 999 PEIXES.','O EXCESSO FICOU NA BOLSA.','A OU B: CONTINUAR'), #20
]
raw=b''.join(messages)
for ch in set(raw)-{32}:assert any(chrtiles[ch]),f'Missing glyph {chr(ch)}'
(out/'messages.bin').write_bytes(raw)
# Original C-major / A-minor melody, 64 eighth notes; 24 NTSC frames per step.
melody=[64,67,69,67,64,62,60,0, 62,64,67,64,62,60,59,0,
        60,64,67,69,67,64,62,0, 59,62,64,62,59,57,55,0,
        64,67,72,71,69,67,64,0, 62,65,69,67,65,64,62,0,
        60,64,67,64,62,60,59,0, 57,60,64,62,60,59,60,0]
chords=[[48,52,55],[45,48,52],[53,57,60],[43,47,50]]
bass=[36,33,41,31]
period=lambda midi:round(1789773/(16*(440*2**((midi-69)/12)))-1) if midi else 0
low=[];high=[];al=[];ah=[];bl=[];bh=[]
for i,n in enumerate(melody):
 t=period(n);low.append(t&255);high.append((t>>8)&7)
 t=period(chords[(i//8)%4][i%3]);al.append(t&255);ah.append((t>>8)&7)
 # Triangle sounds one octave lower for the same timer period.
 t=period(bass[(i//8)%4]+12);bl.append(t&255);bh.append((t>>8)&7)
def data(label,v):return label+':\n .byte '+','.join(str(n) for n in v)+'\n'
(out/'music.inc').write_text(data('melody_low',low)+data('melody_high',high)+data('harmony_low',al)+data('harmony_high',ah)+data('bass_low',bl)+data('bass_high',bh))
print('BG tiles used:',next_tile,'Music steps:',len(melody))

# Actor feet participate in collision, but their full sprite does not block.
solids[0][13*32+22]=1
solids[1][16*32+9]=1
for sc in range(3):(out/f'solid{sc}.bin').write_bytes(solids[sc])
hud=[' ']*32
for x,t in [(2,'PEIXES 0/6'),(14,'CESTO 000'),(25,'J:0/2')]:hud[x:x+len(t)]=t
(out/'hud.inc').write_text('hud_label: .byte "'+''.join(hud)+'"\n')
