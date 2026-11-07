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

# Art study: each room gets a full 4 KiB background pattern table in CHR RAM.
# Palettes are assigned to 16x16 regions before encoding, never per pixel.
W,H=256,240
canvases=[[[0]*W for _ in range(H)] for _ in range(3)]
attributes=[[[0]*16 for _ in range(15)] for _ in range(3)]
solids=[bytearray([1]*1024) for _ in range(3)]
def rect(a,x,y,w,h,c):
 for yy in range(max(0,y),min(H,y+h)):
  for xx in range(max(0,x),min(W,x+w)):a[yy][xx]=c

def line(a,x0,y0,x1,y1,c):
 dx=abs(x1-x0);sx=1 if x0<x1 else -1;dy=-abs(y1-y0);sy=1 if y0<y1 else -1;err=dx+dy
 while True:
  if 0<=x0<W and 0<=y0<H:a[y0][x0]=c
  if x0==x1 and y0==y1:break
  e=2*err
  if e>=dy:err+=dy;x0+=sx
  if e<=dx:err+=dx;y0+=sy

def polygon(a,points,c):
 for yy in range(max(0,min(p[1] for p in points)),min(H,max(p[1] for p in points)+1)):
  xs=[]
  for i,(x1,y1) in enumerate(points):
   x2,y2=points[(i+1)%len(points)]
   if (y1<=yy<y2) or (y2<=yy<y1):xs.append(x1+(yy-y1)*(x2-x1)/(y2-y1))
  xs.sort()
  for i in range(0,len(xs)-1,2):
   for xx in range(max(0,math.ceil(xs[i])),min(W,math.floor(xs[i+1])+1)):a[yy][xx]=c

def oval(a,x,y,w,h,c):
 for yy in range(y,y+h):
  for xx in range(x,x+w):
   if ((xx-x-(w-1)/2)/(w/2))**2+((yy-y-(h-1)/2)/(h/2))**2<=1 and 0<=xx<W and 0<=yy<H:a[yy][xx]=c

def zone(sc,x,y,w,h,p):
 for by in range(max(0,y//16),min(15,(y+h+15)//16)):
  for bx in range(max(0,x//16),min(16,(x+w+15)//16)):attributes[sc][by][bx]=p

def collision_fill(sc,x,y,w,h,value):
 for yy in range(y,y+h):
  for xx in range(x,x+w):solids[sc][yy*32+xx]=value

# Preserve approved collision layout, with the path cottage facade made solid.
collision_fill(0,3,7,26,16,0);collision_fill(0,14,23,4,1,0)
for x,y,w,h in [(4,9,4,3),(24,8,4,3),(5,15,3,2),(14,8,4,3)]:collision_fill(0,x,y,w,h,1)
collision_fill(1,0,6,32,18,0);collision_fill(1,11,6,9,3,1);collision_fill(1,13,7,5,3,0)
collision_fill(1,0,6,32,1,1);collision_fill(1,13,6,5,1,0);collision_fill(1,0,23,32,1,1);collision_fill(1,0,6,1,18,1)
collision_fill(1,10,8,12,4,1);collision_fill(1,13,8,5,4,0)
collision_fill(1,22,11,2,1,1);collision_fill(1,23,12,1,1,1)
collision_fill(2,0,6,19,18,0)
for sc,x,y in [(1,2,6),(1,23,6),(1,3,18),(1,24,19),(2,1,6),(2,10,6),(2,3,19),(2,11,19)]:collision_fill(sc,x+1,y+3,2,2,1)
collision_fill(1,1,13,7,1,1)
solids[0][13*32+22]=1;solids[1][16*32+9]=1

# Floors: long pale planks, staggered joints and sparse grain, not brick grids.
a=canvases[0]
zone(0,16,48,224,144,1);rect(a,16,48,224,144,1)
for yy in range(64,192,16):
 line(a,24,yy,231,yy,2)
 for xx in range(32+((yy//16)%2)*32,232,64):
  line(a,xx,yy,xx,yy+15,2)
  line(a,xx+9,yy+6,xx+22,yy+6,2)
  line(a,xx+13,yy+7,xx+19,yy+7,1)
# Plaster back wall, skirting, side beams, exit threshold.
zone(0,16,48,224,16,0);rect(a,16,48,224,16,1)
for x in (16,232):rect(a,x,48,8,144,3);rect(a,x+2,50,3,139,2)
rect(a,24,61,208,3,3);rect(a,16,184,224,8,3);rect(a,112,184,32,8,1)
for x in range(112,144,8):line(a,x,185,x,191,2)
# Bed: white pillow, blue blanket folds and wooden feet.
zone(0,32,64,32,32,3)
rect(a,32,64,32,32,1);rect(a,32,64,32,4,3)
rect(a,34,68,28,8,3);rect(a,37,69,22,5,2)
rect(a,34,77,28,16,1);rect(a,36,79,24,2,2)
for xx in (38,48,58):line(a,xx,82,xx-2,90,2)
rect(a,33,93,5,3,0);rect(a,58,93,5,3,0)
# Window, frame and visible blue sky with a tiny cloud.
zone(0,112,64,32,32,3);rect(a,112,64,32,32,0)
rect(a,114,66,28,26,2);rect(a,116,68,24,21,1)
rect(a,119,73,8,3,3);rect(a,122,71,3,2,3)
rect(a,126,67,3,24,3);rect(a,115,79,26,2,3);rect(a,112,92,32,4,3)
# Rug is woven, with a medallion and corners, not a full checker texture.
zone(0,80,96,96,64,2);rect(a,80,96,96,64,1)
rect(a,83,99,90,58,3);rect(a,85,101,86,54,2)
rect(a,89,105,78,46,1);rect(a,91,107,74,42,2)
polygon(a,[(128,111),(151,128),(128,145),(105,128)],3)
polygon(a,[(128,116),(145,128),(128,140),(111,128)],1)
polygon(a,[(128,120),(139,128),(128,136),(117,128)],2)
for xx in range(83,174,8):rect(a,xx,96,2,3,3);rect(a,xx,157,2,3,3)
# Wicker basket stays at the approved interaction/collision position.
zone(0,32,112,32,32,1)
rect(a,40,121,24,13,3);rect(a,42,123,20,9,2)
for yy in (124,128):line(a,42,yy,61,yy,3)
for xx in range(44,62,5):line(a,xx,123,xx,132,1)
line(a,44,120,47,117,3);line(a,47,117,56,117,3);line(a,56,117,60,120,3)
# Buff-stone hearth and warm fire, without a red room palette.
zone(0,192,48,32,48,1);rect(a,192,56,32,32,2)
rect(a,194,58,28,27,1)
for yy in (62,70,78):line(a,194,yy,221,yy,2)
for xx,yy in [(201,58),(213,64),(202,72)]:line(a,xx,yy,xx,yy+6,2)
rect(a,200,66,16,20,0);polygon(a,[(202,83),(204,75),(207,78),(210,69),(214,82)],2)
polygon(a,[(205,83),(208,77),(211,83)],1);rect(a,190,86,36,3,3)

# Outdoor terrain: irregular grass clusters and sandy paths aligned to attributes.
for sc in (1,2):
 a=canvases[sc];zone(sc,0,48,256,144,2);rect(a,0,48,256,144,1)
 for yy in range(48,192,16):
  for xx in range(0,256,16):
   pattern=((xx//16)*7^(yy//16)*11)%8
   if pattern==0:
    line(a,xx+3,yy+7,xx+5,yy+4,3);line(a,xx+5,yy+4,xx+7,yy+7,3)
   elif pattern==1:
    rect(a,xx+10,yy+11,2,1,2);rect(a,xx+12,yy+9,1,2,2)
   elif pattern==2:
    line(a,xx+4,yy+12,xx+7,yy+12,3);rect(a,xx+10,yy+4,2,1,2)
   elif pattern==3:
    line(a,xx+8,yy+9,xx+10,yy+6,3);line(a,xx+10,yy+6,xx+12,yy+9,3);rect(a,xx+2,yy+3,2,1,2)
   elif pattern==4:
    rect(a,xx+4,yy+5,3,1,3);rect(a,xx+6,yy+6,3,1,3);rect(a,xx+11,yy+12,2,1,2)
   elif pattern==5:
    line(a,xx+3,yy+11,xx+5,yy+8,3);line(a,xx+5,yy+8,xx+7,yy+11,3);rect(a,xx+11,yy+3,2,1,2)
   elif pattern==6:
    rect(a,xx+5,yy+6,2,1,2);rect(a,xx+6,yy+4,1,2,2);line(a,xx+10,yy+13,xx+13,yy+13,3)
   else:
    line(a,xx+9,yy+5,xx+11,yy+3,3);rect(a,xx+3,yy+11,2,1,2)
 # Shared path patch: color 3 is grass in its palette, matching grass color 1.
 for by in range(3,12):
  for bx in range(16):
   is_path=((sc==1 and bx in (6,7,8) and by<=8) or (by in (6,7,8) and (sc==2 or bx>=6)))
   if not is_path or (sc==2 and bx>=9):continue
   x=bx*16;y=by*16;zone(sc,x,y,16,16,1);rect(a,x,y,16,16,1)
   if by==6 and not(sc==1 and bx in (6,7,8)):
    polygon(a,[(x,y),(x+16,y),(x+16,y+3),(x+10,y+2),(x+4,y+5),(x,y+4)],3)
   if by==8:polygon(a,[(x,y+13),(x+6,y+11),(x+11,y+14),(x+16,y+12),(x+16,y+16),(x,y+16)],3)
   if sc==1 and bx==6 and by<6:
    polygon(a,[(x,y),(x+4,y),(x+2,y+6),(x+5,y+10),(x+3,y+16),(x,y+16)],3)
   rect(a,x+8,y+6,2,1,2);rect(a,x+5,y+12,1,1,2)

# Detailed tree clusters: hand-composed highlight masses, a shaded crown and root mound.
def tree(sc,x,y):
 a=canvases[sc]
 zone(sc,x,y,32,40,2)
 points=[(12,0),(21,1),(23,4),(28,5),(30,10),(28,14),(31,18),(30,24),(26,28),(20,30),(12,29),(7,31),(2,27),(0,21),(2,16),(0,11),(4,6),(9,5)]
 polygon(a,[(x+xx,y+yy) for xx,yy in points],3)
 for ox,oy,w,h in [(6,6,14,10),(14,7,12,10),(4,14,15,10),(13,16,14,10),(6,22,13,7)]:oval(a,x+ox,y+oy,w,h,1)
 for ox,oy,w,h in [(7,5,10,5),(15,8,8,4),(4,13,9,4),(12,16,8,4),(7,22,6,3)]:oval(a,x+ox,y+oy,w,h,2)
 for ox,oy in [(5,11),(17,14),(24,20),(9,20),(13,25)]:line(a,x+ox,y+oy,x+ox+3,y+oy-1,3)
 # Bottom 16-pixel region uses soil/wood palette: soil under the roots is intentional.
 zone(sc,x+8,y+32,16,8,1)
 rect(a,x+12,y+28,7,11,2);line(a,x+14,y+29,x+14,y+37,0)
 line(a,x+12,y+37,x+8,y+39,2);line(a,x+18,y+37,x+23,y+39,2)
for sc,x,y in [(1,16,48),(1,184,48),(1,24,144),(1,192,152),(2,8,48),(2,80,48),(2,24,152),(2,88,152)]:tree(sc,x,y)

# Cottage on the path: tiled roof, light facade and a visible door on the same route.
a=canvases[1]
zone(1,80,32,96,32,3)
polygon(a,[(78,64),(98,37),(151,37),(176,64)],3)
polygon(a,[(84,61),(101,40),(149,40),(168,61)],1)
for yy in (45,51,57):
 line(a,94-(yy-45)//2,yy,156+(yy-45)//2,yy,2)
 for xx in range(101+(yy%2)*4,157,12):line(a,xx,yy-4,xx-2,yy,3)
zone(1,80,64,96,32,0);rect(a,80,64,96,32,1)
rect(a,80,64,96,4,3);rect(a,81,68,4,28,3);rect(a,171,68,4,28,3)
rect(a,86,91,83,5,3)
for x in (89,147):
 rect(a,x,72,16,15,3);rect(a,x+2,74,12,11,2);rect(a,x+7,74,2,11,3);rect(a,x+2,78,12,2,3)
rect(a,109,68,28,28,3);rect(a,112,71,22,25,0)
rect(a,114,73,18,23,2);line(a,122,74,122,95,3);rect(a,128,84,2,2,1)
# Sign and low wooden fence reuse the path palette.
zone(1,176,80,16,32,1);rect(a,177,88,14,9,2);rect(a,179,90,10,5,1)
line(a,180,92,188,92,0);line(a,186,90,188,92,0);line(a,186,94,188,92,0);rect(a,183,97,3,7,2)
for xx in (8,24,40,56):
 zone(1,xx,96,16,16,1);rect(a,xx+3,98,3,12,2);line(a,xx,103,xx+15,103,2)

# River: sand shelves, a clear cliff lip at the collision boundary, bright water.
a=canvases[2]
zone(2,144,48,16,144,1);rect(a,144,48,16,144,1)
for yy in range(48,192):
 a[yy][144]=3 if yy%7<3 else 1
 a[yy][151]=2;a[yy][152]=0;a[yy][153]=2
 for xx in (155,159):
  if yy%8 not in (0,1):a[yy][xx]=2
zone(2,160,48,64,144,3);rect(a,160,48,64,144,1)
for yy in range(48,192,16):
 for xx in range(160,224,16):
  # Four staggered ripple shapes, no complete horizontal tile boundary.
  variant=((xx//16)+(yy//16)*3)%4
  ox=[2,7,3,5][variant];oy=[4,8,10,5][variant]
  line(a,xx+ox,yy+oy,xx+min(14,ox+5),yy+oy,2)
  line(a,xx+ox+1,yy+oy+1,xx+min(13,ox+4),yy+oy+1,3)
  if variant==0:rect(a,xx+11,yy+12,2,1,2)
# Far-bank reeds are on the inaccessible shore.
zone(2,224,48,16,144,1);rect(a,224,48,16,144,1)
for yy in range(48,192,16):
 rect(a,224,yy,3,16,2);line(a,226,yy+12,229,yy+3,3);line(a,230,yy+12,232,yy+6,3)
zone(2,240,48,16,144,2);rect(a,240,48,16,144,1)
for yy in (64,112,160):line(a,245,yy+12,243,yy+4,3);line(a,246,yy+12,249,yy+5,3)
# Half-submerged stones and small white eddies, in water's own subpalette.
for x,y in [(200,80),(208,152)]:
 polygon(a,[(x,y+8),(x+3,y+2),(x+10,y),(x+15,y+6),(x+13,y+12),(x+3,y+13)],3)
 polygon(a,[(x+2,y+7),(x+5,y+3),(x+10,y+2),(x+13,y+6),(x+10,y+8)],2)
 line(a,x-2,y+14,x+14,y+14,2)
# Flowers: small clusters with deliberately placed leaves, not noise over all terrain.
for sc in (1,2):
 a=canvases[sc]
 for x,y in [(64,73),(75,157),(52,137),(132,68)]:
  if sc==1 and 80<=x<176 and y<96:continue
  rect(a,x,y,2,2,2);rect(a,x-1,y+2,4,1,2);line(a,x+1,y+3,x+1,y+6,3)

# A few warm flower clusters use the sand palette's grass entry as their base.
for sc,x,y in [(1,64,64),(1,176,144),(2,48,80),(2,128,144)]:
 a=canvases[sc];zone(sc,x,y,16,16,1);rect(a,x,y,16,16,3)
 for ox,oy in [(4,5),(10,9),(7,2)]:
  rect(a,x+ox-1,y+oy,3,1,1);rect(a,x+ox,y+oy-1,1,3,1)
  rect(a,x+ox,y+oy,1,1,2);line(a,x+ox,y+oy+2,x+ox,y+oy+4,0)
# Small back-wall shelf: a domestic detail, not a new quest object.
a=canvases[0];zone(0,80,48,32,16,1);rect(a,80,48,32,16,1)
rect(a,81,49,30,2,3);rect(a,81,61,30,3,3)
for x,h in [(84,8),(89,10),(94,7),(100,9),(105,8)]:
 rect(a,x,61-h,3,h,2);line(a,x+1,62-h,x+1,59,3)

# Original directional 16x24 sprites. Head and torso use different sprite palettes.
def encode_sprite(index,rows):
 assert len(rows)==24 and all(len(r)==16 for r in rows),(index,len(rows))
 for ty in range(3):
  for tx in range(2):chrtiles[256+index+ty*2+tx]=tile([r[tx*8:tx*8+8] for r in rows[ty*8:ty*8+8]])
front=[
'0000011111100000','0000113333110000','0001133333310000','0001333333331000',
'0001322222231000','0001221221221000','0000122222210000','0000012222100000',
'0000013333100000','0000122222210000','0001322222231000','0001322222231000',
'0001322122231000','0001322122231000','0000122222210000','0000111111110000',
'0000122222210000','0000121112210000','0000111001110000','0000111001110000',
'0000110000110000','0000110000110000','0001110000111000','0001110000111000']
back=[
'0000011111100000','0000113333110000','0001133333310000','0001333333331000',
'0001333333331000','0001133333310000','0000113333110000','0000011111100000',
'0000011111100000','0000122222210000','0001122222211000','0001322222231000',
'0001322222231000','0001322222231000','0000122222210000','0000111111110000',
'0000122222210000','0000121112210000','0000111001110000','0000111001110000',
'0000110000110000','0000110000110000','0001110000111000','0001110000111000']
side=[
'0000011111000000','0000113331100000','0001133333110000','0001333333310000',
'0001332222210000','0001122212211000','0000112222210000','0000012221100000',
'0000013331000000','0000122221100000','0000122222110000','0000122333210000',
'0000122333210000','0000122233100000','0000122221100000','0000111111100000',
'0000122222100000','0000121122100000','0000110011100000','0000110011100000',
'0000110001100000','0000110001100000','0001110001110000','0001110001110000']
legs_front=[
 ['0000122222210000','0000121112210000','0000111001100000','0001110001100000','0001110000110000','0011100000110000','0011100000111000','0000000000111000'],
 ['0000122222210000','0000121112210000','0000110011100000','0000110001110000','0001100001110000','0001100000111000','0011100000111000','0011100000000000']]
legs_side=[
 ['0000122222100000','0000121122100000','0000110011100000','0001110001100000','0011100000110000','0111000000111000','0111000000011100','0000000000011100'],
 ['0000122222100000','0000121122100000','0000110011100000','0000110001110000','0001100000111000','0011100000011100','0011100000011100','0011100000000000']]
for direction,body in enumerate((front,back,side)):
 encode_sprite(direction*18,body)
 for frame in range(2):
  art=body[:16]+(legs_side[frame] if direction==2 else legs_front[frame])
  # Opposite arm swing is visible in the side silhouette too.
  if direction==2 and frame==0:art[11]='0000122333331000';art[12]='0000122333310000'
  if direction==2 and frame==1:art[11]='0001322222110000';art[12]='0001322222110000'
  encode_sprite(direction*18+(frame+1)*6,art)
fisher=side.copy();fisher[10]='0000122222110000';fisher[11]='0000122233331100';fisher[12]='0000122233331100';encode_sprite(54,fisher)
mother=[
'0000011111100000','0000111111110000','0001111111111000','0001122222211000',
'0001222222221000','0001221221221000','0000122222210000','0000012222100000',
'0000013333100000','0000133333310000','0001332222331000','0001332222331000',
'0001332222331000','0001332222331000','0000132222310000','0000132222310000',
'0001332222331000','0001332222331000','0001333333331000','0001333333331000',
'0001111111111000','0000011001100000','0000111001110000','0000111001110000']
orc=[
'0000011111100000','0000113333110000','0011133333311100','0111222222221110',
'0112222222222110','0012212222122100','0001222222221000','0000112222110000',
'0000111111110000','0001333333331000','0012333223332100','0012333223332100',
'0012333333332100','0012333333332100','0001333333331000','0001111111111000',
'0001333333331000','0001331113331000','0001111001111000','0001111001111000',
'0001110000111000','0001110000111000','0011110000111100','0011110000111100']
encode_sprite(60,mother);blink=mother.copy();blink[5]='0001222222221000';encode_sprite(66,blink)
encode_sprite(72,orc);blink=orc.copy();blink[5]='0012222222222100';encode_sprite(78,blink)
sprites={84:['00000000','00000000','00300000','03330000','00300000','00000003','00000033','00000003'],85:['00000000','00000000','00000300','00003330','00000300','30000000','33000000','30000000'],86:['00000000','00000000','00030000','00333000','00030000','00000000','00000000','00000000'],87:['00000000']*8,88:['10000000','01000000','00100000','00010000','00001000','00000100','00000010','00000001'],89:['10000000','01000000','00100000','00010000','00001000','00000100','00000010','00000001']}
for idx,bitmap in sprites.items():chrtiles[256+idx]=tile(bitmap)

# Compile each room into one legal NES tile table and attribute table.
reserved={ord(ch) for ch in font}|{0,32}
free=[i for i in range(1,256) if i not in reserved]
font_tiles=chrtiles[:256]
room_patterns=[];maps=[];counts=[]
for sc in range(3):
 patterns=font_tiles.copy();lookup={raw:i for i,raw in enumerate(patterns) if i in reserved};next_index=0;nt=bytearray(1024)
 for ty in range(30):
  for tx in range(32):
   raw=tile([canvases[sc][ty*8+yy][tx*8:tx*8+8] for yy in range(8)])
   if raw not in lookup:
    assert next_index<len(free),f'Room {sc} exceeds tile budget: {next_index}'
    idx=free[next_index];next_index+=1;patterns[idx]=raw;lookup[raw]=idx
   nt[ty*32+tx]=lookup[raw]
 for i,c in enumerate(['CABANA DO RIO','CAMINHO DO RIACHO','RIACHO TRANQUILO'][sc]):nt[2*32+3+i]=ord(c)
 for ay in range(8):
  for ax in range(8):
   v=0
   for qy in range(2):
    for qx in range(2):
     by=ay*2+qy;bx=ax*2+qx
     pal=attributes[sc][by][bx] if by<15 else 0
     if by<2 or by>=12:pal=0
     v|=pal<<(qy*4+qx*2)
   nt[960+ay*8+ax]=v
 raw=b''.join(patterns)
 assert len(raw)==4096
 room_patterns.append(raw);maps.append(nt);counts.append(next_index)
 (out/f'room{sc}.nam').write_bytes(nt);(out/f'solid{sc}.bin').write_bytes(solids[sc]);(out/f'background{sc}.chr').write_bytes(raw)

# PackBits: 0 terminates, 1..127 repeat next byte, 129..255 copy literal bytes.
def pack(data):
 result=bytearray();i=0
 while i<len(data):
  run=1
  while i+run<len(data) and data[i+run]==data[i] and run<127:run+=1
  if run>=3:result.extend((run,data[i]));i+=run;continue
  start=i;i+=run
  while i<len(data) and i-start<127:
   run=1
   while i+run<len(data) and data[i+run]==data[i] and run<3:run+=1
   if run>=3:break
   i+=min(run,127-(i-start))
  literal=data[start:i];result.append(0x80|len(literal));result.extend(literal)
 result.append(0);return bytes(result)
for sc,raw in enumerate(room_patterns):(out/f'background{sc}.pkb').write_bytes(pack(raw))
raw=b''.join(chrtiles[256:]);assert len(raw)==4096
(out/'sprites.chr').write_bytes(raw);(out/'sprites.pkb').write_bytes(pack(raw))
(out/'art-stats.txt').write_text('\n'.join(f'Room {i}: {n} custom tiles + {len(reserved)} reserved font/blank slots; packed {len(pack(room_patterns[i]))} bytes' for i,n in enumerate(counts))+'\nSprite pattern table: 4096 bytes; packed '+str(len(pack(raw)))+' bytes\n')
print((out/'art-stats.txt').read_text())
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
hud=[' ']*32
for x,t in [(2,'PEIXES 0/6'),(14,'CESTO 000'),(25,'J:0/2')]:hud[x:x+len(t)]=t
(out/'hud.inc').write_text('hud_label: .byte "'+''.join(hud)+'"\n')
