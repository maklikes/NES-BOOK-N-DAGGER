"""Read user-authored Pixelorama projects; preserve exact native RGBA pixels."""
from pathlib import Path
import ast
import hashlib
import json
import re
import zipfile
from PIL import Image

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
OUT = BASE / 'build'
OUT.mkdir(exist_ok=True)
PREVIEW = BASE / 'imported'
PREVIEW.mkdir(exist_ok=True)
HERO = [(0, 0, 0, 0), (15, 15, 15, 255), (0, 88, 248, 255), (252, 188, 116, 255)]
GROUND = [(0, 0, 0, 0), (0, 88, 0, 255), (0, 168, 0, 255), (88, 216, 84, 255)]


def load_project(name, palette, expected_frames):
    path = BASE / 'source' / name
    result = []
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read('data.json'))
        assert (data['size_x'], data['size_y']) == (16, 16), name
        assert len(data['layers']) == 1 and data['layers'][0]['visible'], name
        assert data['layers'][0]['opacity'] == 1, name
        assert not data['layers'][0]['effects'], name
        assert len(data['frames']) == expected_frames, name
        for index, frame in enumerate(data['frames'], 1):
            assert len(frame['cels']) == 1 and frame['duration'] == 1, name
            cel = frame['cels'][0]
            assert cel['opacity'] == 1 and cel['z_index'] == 0, name
            width, height = map(int, re.findall(r'-?\d+', cel['image_size'])[-2:])
            x, y = map(int, re.findall(r'-?\d+', cel['offset']))
            assert 0 <= x <= 16-width and 0 <= y <= 16-height, (name, index)
            raw = archive.read(f'image_data/frames/{index}/layer_1')
            assert len(raw) == width*height*4
            image = Image.new('RGBA', (16, 16))
            image.paste(Image.frombytes('RGBA', (width, height), raw), (x, y))
            assert set(image.getdata()) <= set(palette), (name, index, set(image.getdata()))
            result.append(image)
    return result, data['fps'], hashlib.sha256(path.read_bytes()).hexdigest()


def encode(image, palette):
    chunks = []
    for ty in range(2):
        for tx in range(2):
            pixels = [[palette.index(image.getpixel((tx*8+x, ty*8+y))) for x in range(8)] for y in range(8)]
            raw = bytes(sum((v & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            raw += bytes(sum(((v >> 1) & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            chunks.append(raw)
    # Decode the exported bitplanes, independently of the image assembly.
    decoded = Image.new('RGBA', (16, 16))
    for i, raw in enumerate(chunks):
        for y in range(8):
            for x in range(8):
                v = ((raw[y] >> (7-x)) & 1) | (((raw[y+8] >> (7-x)) & 1) << 1)
                decoded.putpixel(((i % 2)*8+x, (i // 2)*8+y), palette[v])
    assert decoded.tobytes() == image.tobytes()
    return chunks


hero, fps, hero_hash = load_project('teste_personagem_v1.pxo', HERO, 4)
floor, _, floor_hash = load_project('teste-piso.pxo', GROUND, 1)
bush, _, bush_hash = load_project('teste-arbusto.pxo', GROUND, 1)
assert fps == 6
assert all(p[3] == 255 for image in floor+bush for p in image.getdata())
assert hero[0].tobytes() == hero[2].tobytes()
chrdata = [bytes(16) for _ in range(512)]
for i, image in enumerate(hero):
    image.save(PREVIEW / f'personagem-{i+1}.png')
    for j, raw in enumerate(encode(image, HERO)):
        chrdata[256+i*4+j] = raw
for name, images, offset in [('piso', floor, 128), ('arbusto', bush, 132)]:
    images[0].save(PREVIEW / f'{name}.png')
    for j, raw in enumerate(encode(images[0], GROUND)):
        chrdata[offset+j] = raw

# Reuse only the existing project font, without executing its generator.
font = {}
for node in ast.parse((REPO / 'game/first-river/assets.py').read_text()).body:
    if isinstance(node, ast.Assign):
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == 'font':
            font = ast.literal_eval(node.value)
        elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == 'font':
            font[ast.literal_eval(target.slice)] = ast.literal_eval(node.value)
for char, rows in font.items():
    assert ord(char) < 128
    chrdata[ord(char)] = bytes(sum(int(c) << (7-x) for x, c in enumerate(row)) for row in rows) + bytes(9)
    assert len(chrdata[ord(char)]) == 16

# Metatile grid: bushes around the playfield and three small interior groups.
collision = bytearray(16*15)
for y in range(2, 14):
    for x in range(16):
        if x in (0, 15) or y in (2, 13):
            collision[y*16+x] = 1
for x, y in [(5, 5), (6, 5), (7, 5), (10, 7), (10, 8), (10, 9), (4, 10)]:
    collision[y*16+x] = 1
screen = bytearray(1024)
for my in range(2, 14):
    for mx in range(16):
        tile = 132 if collision[my*16+mx] else 128
        for ty in range(2):
            for tx in range(2):
                screen[(my*2+ty)*32+mx*2+tx] = tile+ty*2+tx
for ay in range(8):
    for ax in range(8):
        value = 0
        for qy in range(2):
            for qx in range(2):
                tile_y = ay*4+qy*2
                if tile_y < 4 or tile_y >= 28:
                    value |= 1 << (qy*4+qx*2)
        screen[960+ay*8+ax] = value
for x, y, text in [(3, 2, 'MEU PRIMEIRO CENARIO'), (1, 28, 'B:LENTO SEL:INICIO START:PAUSA')]:
    for i, char in enumerate(text):
        assert char in font or char == ' '
        screen[y*32+x+i] = ord(char)
(OUT / 'graphics.chr').write_bytes(b''.join(chrdata))
(OUT / 'screen.nam').write_bytes(screen)
(OUT / 'collision.bin').write_bytes(collision)
(BASE / 'imported' / 'validation.json').write_text(json.dumps({
    'source_sha256': {'personagem': hero_hash, 'piso': floor_hash, 'arbusto': bush_hash},
    'canvas': [16, 16], 'frames': 4, 'fps': fps, 'ntsc_ticks_per_frame': 10,
    'hero_rgba': HERO, 'ground_rgba': GROUND,
    'sprite_palette_ppu': [15, 15, 18, 55], 'ground_palette_ppu': [15, 10, 26, 42],
    'chr_roundtrip_exact': True, 'overlays': False,
    'sprites_per_actor': 4, 'sprites_per_scanline': 2,
    'bush_cells': [[x, y] for y in range(2, 14) for x in range(16) if collision[y*16+x]],
}, indent=2))
print('PXO import exact: 4 actor frames + floor + bush; 6 FPS; valid NES palettes.')
