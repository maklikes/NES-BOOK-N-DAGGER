"""Exact export of user path pieces and a non-playable composition preview."""
from pathlib import Path
import collections
import hashlib
import json
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PALETTE = [(0, 0, 0, 0), (0, 168, 0, 255), (139, 68, 0, 255), (184, 112, 24, 255)]


def read_pxo(path):
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read('data.json'))
        assert (data['size_x'], data['size_y']) == (16, 16)
        assert len(data['frames']) == 1 and len(data['layers']) == 1
        assert data['layers'][0]['visible'] and data['layers'][0]['opacity'] == 1
        assert not data['layers'][0]['effects']
        cel = data['frames'][0]['cels'][0]
        assert cel['opacity'] == 1
        w, h = map(int, re.findall(r'-?\d+', cel['image_size'])[-2:])
        x, y = map(int, re.findall(r'-?\d+', cel['offset']))
        assert 0 <= x <= 16-w and 0 <= y <= 16-h
        raw = archive.read('image_data/frames/1/layer_1')
        assert len(raw) == w*h*4
        image = Image.new('RGBA', (16, 16))
        image.paste(Image.frombytes('RGBA', (w, h), raw), (x, y))
        return image


def encode(image):
    chunks = []
    for ty in range(2):
        for tx in range(2):
            pixels = [[PALETTE.index(image.getpixel((tx*8+x, ty*8+y))) for x in range(8)] for y in range(8)]
            raw = bytes(sum((v & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            raw += bytes(sum(((v >> 1) & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            chunks.append(raw)
    decoded = Image.new('RGBA', (16, 16))
    for tile, raw in enumerate(chunks):
        for y in range(8):
            for x in range(8):
                index = ((raw[y] >> (7-x)) & 1) | (((raw[y+8] >> (7-x)) & 1) << 1)
                decoded.putpixel(((tile % 2)*8+x, (tile // 2)*8+y), PALETTE[index])
    assert decoded.tobytes() == image.tobytes()
    return b''.join(chunks)


pieces = {}
report = {}
for name in ['borda-esquerda', 'centro', 'borda-direita']:
    path = ROOT / 'source' / f'teste-caminho-{name}.pxo'
    image = read_pxo(path)
    colors = collections.Counter(image.getdata())
    assert set(colors) <= set(PALETTE[1:]), (name, colors)
    image.save(ROOT / f'{name}.png')
    raw = encode(image)
    assert len(raw) == 64
    (ROOT / f'{name}.chr').write_bytes(raw)
    report[name] = {'canvas': [16,16], 'rgba_counts': {str(k): v for k,v in colors.items()},
                    'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'opaque': True, 'chr_bytes': len(raw), 'decoded_pixels_identical': True}
    pieces[name] = image

floor = read_pxo(REPO / 'game/tutorial-garden/source/teste-piso.pxo')
scene = Image.new('RGBA', (128,128))
for y in range(8):
    for x in range(8):
        piece = pieces[['borda-esquerda','centro','borda-direita'][x-3]] if 3 <= x <= 5 else floor
        scene.paste(piece, (x*16,y*16))
scene.save(ROOT / 'caminho-montado.png')
actor = Image.open(REPO / 'game/tutorial-garden/imported/personagem-1.png').convert('RGBA')
with_actor = scene.copy()
with_actor.alpha_composite(actor, (64,56))
with_actor.save(ROOT / 'caminho-com-personagem.png')

strip = Image.new('RGBA', (48,16))
for i,name in enumerate(['borda-esquerda','centro','borda-direita']):
    strip.paste(pieces[name], (16*i,0))
strip.save(ROOT / 'pecas.png')

board = Image.new('RGB',(1120,710),'#f6f0e2')
draw = ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def label(x,y,text,size=18):
    draw.text((x,y),text,font=ImageFont.truetype(font,size),fill='#30251b')
label(25,20,'SEU CAMINHO — PEÇAS E MONTAGEM',29)
label(25,65,'Pixels originais preservados; sem alteração de desenhos ou ROM.',18)
for x,name,title in [(30,'borda-esquerda','ESQUERDA'),(210,'centro','CENTRO'),(390,'borda-direita','DIREITA')]:
    label(x,120,title,17)
    board.paste(pieces[name].resize((128,128),Image.Resampling.NEAREST),(x,155))
label(570,120,'MONTAGEM 4× — personagem para escala',17)
board.paste(with_actor.resize((512,512),Image.Resampling.NEAREST),(570,155))
label(30,330,'Montagem em escala 1×:',18)
board.paste(with_actor,(210,370))
label(30,550,'Peças 16×16, ampliadas 8×.',17)
label(30,580,'Grama: uma subpaleta.',17)
label(30,610,'Caminho e bordas: outra subpaleta.',17)
label(25,680,'Prévia montada dos PNGs. Ainda não é captura de uma ROM.',16)
board.save(ROOT / 'prancha-caminho.png')
(ROOT / 'validation.json').write_text(json.dumps({'path_palette_ppu': [15,26,23,39],
    'path_palette_rgba': PALETTE, 'pieces':report, 'rom_modified':False},indent=2))
print('Three exact 16x16 pieces, fully opaque, 3 legal colors; CHR roundtrip identical.')
