"""Assemble unretouched FCEUX frames into a comparison outside the ROM."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
base=Path(__file__).resolve().parent;old_base=base.parent/'first-river'
out=Path('/workspace/artifacts/river-art')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def decode(p):
 d=p.read_bytes();assert len(d)==245771
 return Image.frombytes('RGBA',(256,240),d[11:],'raw','ARGB').convert('RGB')
for name,dst in [('cabin','cabana'),('path','caminho'),('fishing','riacho')]:decode(out/(name+'.gd')).save(base/(dst+'.png'))
canvas=Image.new('RGB',(1024,1540),'#152235');draw=ImageDraw.Draw(canvas)
draw.text((12,10),'v0.1 — versão funcional anterior',font=font,fill='white');draw.text((524,10),'v0.2 — estudo de arte',font=font,fill='white')
for i,(filename,label) in enumerate([('cabana','Cabana'),('caminho','Caminho'),('riacho','Riacho')]):
 y=40+i*500
 for x,p in [(0,old_base/(filename+'.png')),(512,base/(filename+'.png'))]:
  im=Image.open(p).convert('RGB').resize((512,480),Image.Resampling.NEAREST);canvas.paste(im,(x,y))
 draw.text((12,y+482),label,font=font,fill='white')
canvas.save(base/'comparacao-cenarios.png')
old=sorted((out/'motion-old').glob('*.gd'));new=sorted((out/'motion-new').glob('*.gd'))
assert len(old)==len(new)==68
frames=[]
for a,b in zip(old,new):
 panel=Image.new('RGB',(1024,332),'#152235');dr=ImageDraw.Draw(panel)
 dr.text((12,7),'v0.1 — frente em todas as direções',font=font,fill='white');dr.text((524,7),'v0.2 — frente / costas / perfil',font=font,fill='white')
 for x,p in [(0,a),(512,b)]:panel.paste(decode(p).crop((0,40,256,192)).resize((512,304),Image.Resampling.NEAREST),(x,28))
 frames.append(panel)
frames[0].save(base/'comparacao-movimento.gif',save_all=True,append_images=frames[1:],loop=0,duration=[120 if (i+1)%17==0 else 50 for i in range(68)],optimize=False)
print('Comparison files generated from actual framebuffer captures.')
