"""Original, deterministic NES tiles and room; no external artwork or font."""
from pathlib import Path
out=Path(__file__).parent/'build';out.mkdir(exist_ok=True)
# Five columns, seven rows, drawn by hand; glyphs occupy an 8x8 NES tile.
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
def tile(rows):
 rows=[[int(v) for v in row] for row in rows]
 return bytes(sum((v&1)<<(7-x) for x,v in enumerate(row)) for row in rows)+bytes(sum(((v>>1)&1)<<(7-x) for x,v in enumerate(row)) for row in rows)
chars=[bytes(16) for _ in range(512)]
for ch,rows in font.items():chars[ord(ch)]=tile([r.ljust(8,'0') for r in rows]+['00000000'])
patterns={
128:['22222222','20000002','20000002','22222222','00020000','00020000','22222222','00000000'],
129:['11111111','11111111','12111111','11111111','11111111','11111211','11111111','33333333'],
130:['33333333','32222223','32111123','32111123','32111123','32111123','32222223','33333333'],
131:['33333333','32222223','32222223','33333333','32222223','32222223','32222223','33333333'],
132:['33333333','33333333','11111111','11111111','22222222','22222222','22222222','22222222'],
133:['22222222','21111112','21111112','21111112','21111112','21111112','21111112','22222222'],
134:['00000000','00000000','00033000','00333300','00033000','00000000','00000000','00000000'],
135:['00000000','00000000','00022000','00233200','00022000','00000000','00000000','00000000'],
}
for i,rows in patterns.items():chars[i]=tile(rows)
chars[ord('>')]=tile(['01000000','00100000','00010000','00001000','00010000','00100000','01000000','00000000'])
# Original 16x24 sprite: hair, face, burgundy coat, boots.
hero=[
'0000011111100000','0000111111110000','0001111111111000','0001122222211000',
'0001222222221000','0001221221221000','0001222222221000','0000122222210000',
'0000033333300000','0000333333330000','0002333333332000','0002333333332000',
'0002333333332000','0002333333332000','0000333333330000','0000333333330000',
'0000333333330000','0000333333330000','0000011001100000','0000011001100000',
'0000011001100000','0000011001100000','0000111001110000','0000111001110000']
for row in range(3):
 for col in range(2):chars[256+row*2+col]=tile([v[col*8:col*8+8] for v in hero[row*8:row*8+8]])
(out/'graphics.chr').write_bytes(b''.join(chars))
nt=bytearray(1024)
def put(x,y,s):
 for i,c in enumerate(s):nt[y*32+x+i]=ord(c)
put(5,2,'A ADAGA E O LIVRO')
put(5,3,'LIVRO: NAO ADAGA: NAO')
for y in range(6,25):
 for x in range(2,30):nt[y*32+x]=128 if y<12 else 129
for y in range(6,25):nt[y*32+2]=nt[y*32+29]=130
for x in range(2,30):nt[6*32+x]=nt[24*32+x]=132
# Desk collision box x=112..159, y=128..151.
for y in range(16,19):
 for x in range(14,20):nt[y*32+x]=132 if y==16 else 133
put(3,4,'A: EXAMINAR B: VOLTAR')
# Palette1 for room, palette2 for desk. Attribute fields cover 16x16 quadrants.
for ay in range(8):
 for ax in range(8):
  value=0
  for qy in range(2):
   for qx in range(2):
    tx=ax*4+qx*2;ty=ay*4+qy*2
    pal=1 if 2<=tx<30 and 6<=ty<24 else 0
    if 14<=tx<20 and 16<=ty<20:pal=2
    value|=pal<<(qy*4+qx*2)
  nt[960+ay*8+ax]=value
(out/'room.nam').write_bytes(nt)

# Three 48x48 wardrobe states: closed oval mirror, open shelf, empty shelf.
# Pixels use the existing wooden room subpalette (no image quantization).
def wardrobe(state):
 canvas=[[1]*48 for _ in range(48)]
 def rect(x,y,w,h,c):
  for yy in range(y,y+h):
   for xx in range(x,x+w):canvas[yy][xx]=c
 rect(0,0,48,3,3);rect(0,45,48,3,3)
 for x in (1,9,37,45):rect(x,3,2,42,3)
 rect(12,4,24,34,0)
 if state==0:
  # Oval inset. Its reflection contains a small handle not on the real drawer.
  for yy in range(30):
   for xx in range(22):
    q=((xx-10.5)/10.5)**2+((yy-14.5)/14.5)**2
    if q<=1:canvas[yy+5][xx+13]=3 if q>.75 else 2
  rect(21,28,6,2,3)
 else:
  rect(13,31,22,2,3)
  if state==1:
   rect(16,10,15,17,2);rect(16,10,2,17,3)
   rect(19,13,9,1,3);rect(19,17,9,1,3)
   rect(18,36,15,2,3);rect(29,34,2,6,2)
 rect(11,41,26,3,2)
 return canvas
maps=[]
for state in range(3):
 canvas=wardrobe(state);mapping=[]
 for ty in range(6):
  for tx in range(6):
   index=140+state*36+ty*6+tx
   chars[index]=tile([row[tx*8:tx*8+8] for row in canvas[ty*8:ty*8+8]])
   mapping.append(index)
 maps.append(bytes(mapping))
for ty in range(6):
 for tx in range(6):nt[(7+ty)*32+23+tx]=maps[0][ty*6+tx]
(out/'wardrobe.bin').write_bytes(b''.join(maps))
(out/'graphics.chr').write_bytes(b''.join(chars))
(out/'room.nam').write_bytes(nt)

# Each message is three complete nametable rows. Two-column safe margin.
def panel(*lines):
 assert len(lines)==3
 assert all(len(line)<=28 for line in lines),lines
 return b''.join(('  '+line).ljust(32).encode('ascii') for line in lines)
messages=[
 panel('A EXAMINAR   START PAUSA','APROXIME-SE DO ARMARIO','SELECT: REPOSICIONAR'),
 panel('> ESPELHO','  GAVETA','  PORTA'),
 panel('  ESPELHO','> GAVETA','  PORTA'),
 panel('  ESPELHO','  GAVETA','> PORTA'),
 panel('NADA AO ALCANCE.','PROCURE MAIS PERTO.','A OU B: CONTINUAR'),
 panel('UMA MESA PESADA.','MARCAS ANTIGAS NA MADEIRA.','A OU B: CONTINUAR'),
 panel('NO REFLEXO HA UM PUXADOR.','A GAVETA NAO TEM PUXADOR.','A OU B: CONTINUAR'),
 panel('A GAVETA PARECE PRESA.','TALVEZ HAJA ALGO DIFERENTE.','A OU B: CONTINUAR'),
 panel('ATRAS DA GAVETA: UM FECHO.','VOCE SOLTA O TRINCO.','A OU B: CONTINUAR'),
 panel('A PORTA ESTA PRESA.','ALGO A MANTEM FECHADA.','A OU B: CONTINUAR'),
 panel('A PORTA CEDE. LA DENTRO:','UM LIVRO ANTIGO E UMA ADAGA.','A OU B: VOLTAR'),
 panel('VOCE PEGA O LIVRO E A ADAGA.','O REFLEXO PARECE OBSERVAR.','A OU B: CONTINUAR'),
 panel('O PUXADOR ESTA NO VIDRO.','VALE EXAMINAR A GAVETA.','A OU B: CONTINUAR'),
 panel('O FECHO JA ESTA SOLTO.','A PORTA AGORA PODE ABRIR.','A OU B: CONTINUAR'),
 panel('O COMPARTIMENTO ESTA VAZIO.','VOCE GUARDOU LIVRO E ADAGA.','A OU B: CONTINUAR'),
]
(out/'messages.bin').write_bytes(b''.join(messages))

# Room 2: a cold antechamber, return doorway and sealed far doorway.
room2=bytearray(nt)
for y in range(6,25):
 for x in range(2,30):room2[y*32+x]=128 if y<12 else 129
for y in range(6,25):room2[y*32+2]=room2[y*32+29]=130
for x in range(2,30):room2[6*32+x]=room2[24*32+x]=132
for x in range(3,29):room2[4*32+x]=0
for i,c in enumerate('ANTECAMARA - B: OBJETOS'):room2[4*32+3+i]=ord(c)
# Palette 3 produces a colder room, without changing the room 1 palette.
for ay in range(1,6):
 for ax in range(8):room2[960+ay*8+ax]=255
# Keep row 4 instructions in text palette, room starts on row 6.
for ax in range(8):room2[960+8+ax]=240
# Leave top HUD / dialogue in text palette, as in room 1.
for y in range(13,19):
 for x in range(3,6):room2[y*32+x]=130 if x in (3,5) else 0
closed=[];opened=[]
for y in range(6):
 for x in range(3):
  closed.append(131)
  opened.append(132 if y==0 else (130 if x in (0,2) else 0))
for y in range(6):
 for x in range(3):room2[(13+y)*32+26+x]=closed[y*3+x]
chars[136]=tile(['11111111','11111111','12111111','32323232','23232323','11111211','11111111','33333333'])
(out/'room2.nam').write_bytes(room2)
(out/'gate.bin').write_bytes(bytes(closed+opened))
messages += [
 panel('HA UMA PASSAGEM NO ARMARIO.','A: ENTRAR   B: VOLTAR','VOCE TEM LIVRO E ADAGA.'),
 panel('A EXAMINAR    B OBJETOS','LIVRO REVELA. ADAGA CORTA.','PORTA ESQUERDA: VOLTAR'),
 panel('> LIVRO: REVELAR','  ADAGA: CORTAR','A USAR   B VOLTAR'),
 panel('  LIVRO: REVELAR','> ADAGA: CORTAR','A USAR   B VOLTAR'),
 panel('VOCE AINDA NAO TEM OBJETOS.','PROCURE NO ARMARIO.','A OU B: CONTINUAR'),
 panel('NAO HA VINCULO VISIVEL AQUI.','OS OBJETOS SILENCIAM.','A OU B: CONTINUAR'),
 panel('AS LETRAS REVELAM UM FIO.','ELE PRENDE A PORTA A PAREDE.','A OU B: CONTINUAR'),
 panel('O VINCULO ESTA INTEIRO.','APROXIME-SE PARA CORTAR.','A OU B: CONTINUAR'),
 panel('VOCE NAO VE O QUE CORTAR.','TENTE COMPREENDER A PORTA.','A OU B: CONTINUAR'),
 panel('A ADAGA NAO ALCANCA.','APROXIME-SE DO VINCULO.','A OU B: CONTINUAR'),
 panel('O FIO CEDE AO CORTE.','A PORTA ESTA LIVRE.','A OU B: CONTINUAR'),
 panel('A PORTA NAO SE MOVE.','ALGO A MANTEM FECHADA.','A OU B: CONTINUAR'),
 panel('VOCE ABRIU O CAMINHO.','FIM DESTE TESTE.','A OU B: CONTINUAR'),
 panel('HA ALGO ESTRANHO NA PORTA.','O LIVRO PODE AJUDAR.','A OU B: CONTINUAR'),
 panel('O VINCULO FOI ROMPIDO.','NAO HA MAIS O QUE CORTAR.','A OU B: CONTINUAR'),
]
(out/'messages.bin').write_bytes(b''.join(messages))
for ch in set(b''.join(messages))-{32}:
 assert any(chars[ch]), f'Missing glyph {chr(ch)}'
(out/'graphics.chr').write_bytes(b''.join(chars))
