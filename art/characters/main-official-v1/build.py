"""Exportação determinística da especificação oficial; nenhuma edição artística."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from spec import COLORS, FRONT, PROFILE, BACK, PALETTE_SYMBOLS, PALETTE_INDICES

ROOT = Path(__file__).resolve().parent
poses = {'frente': FRONT, 'perfil': PROFILE, 'costas': BACK}
records = {}
report = []
for name, rows in poses.items():
    assert len(rows) == 24 and all(len(row) == 16 for row in rows), name
    assert rows[23] == '.' * 16
    assert 'K' in rows[0] and 'K' in rows[22]
    assert set(rows[7]) <= {'.', 'K'} and set(rows[15]) <= {'.', 'K'}
    image = Image.new('RGBA', (16, 24))
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            image.putpixel((x, y), COLORS[char])
    image.save(ROOT / f'{name}.png')
    tiles = []
    entries = []
    for ty in range(3):
        palette = PALETTE_SYMBOLS[ty]
        for tx in range(2):
            pixels = []
            for yy in range(8):
                row = rows[ty * 8 + yy][tx * 8:tx * 8 + 8]
                assert set(row) <= set(palette), (name, ty, tx, row)
                pixels.append([palette.index(c) for c in row])
            raw = bytes(sum((v & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            raw += bytes(sum(((v >> 1) & 1) << (7-x) for x, v in enumerate(row)) for row in pixels)
            entries.append({'x': tx * 8, 'y': ty * 8, 'tile': len(tiles), 'palette': ty})
            tiles.append(raw)
    data = b''.join(tiles)
    assert len(data) == 96 and len(entries) == 6
    (ROOT / f'{name}.chr').write_bytes(data)
    # Decode exported bitplanes through each tile's subpalette independently.
    decoded = Image.new('RGBA', (16, 24))
    for e in entries:
        raw = data[e['tile']*16:(e['tile']+1)*16]
        for y in range(8):
            for x in range(8):
                index = ((raw[y] >> (7-x)) & 1) | (((raw[y+8] >> (7-x)) & 1) << 1)
                decoded.putpixel((e['x']+x, e['y']+y), COLORS[PALETTE_SYMBOLS[e['palette']][index]])
    assert decoded.tobytes() == image.tobytes(), name
    assert max(sum(e['y'] <= y < e['y']+8 for e in entries) for y in range(24)) == 2
    records[name] = {'pixels': rows, 'metasprite': entries}
    report.append(f'{name}: exact 16x24; 6 sprites; 96 CHR bytes; 2 sprites/scanline; no overlays; exact decoded RGBA; Y0/Y7/Y15/Y22/Y23 verified')

(ROOT / 'sprites.json').write_text(json.dumps({'size': [16,24], 'colors_rgba': COLORS,
    'palette_indices': PALETTE_INDICES, 'poses': records}, indent=2))
# Four entries per sprite subpalette. Transparent entries are placeholders;
# when loading into PPU palette RAM, respect its mirrored backdrop addresses.
hardware = bytes(0x0F if v is None else v for pal in PALETTE_INDICES for v in pal)
(ROOT / 'sprite-subpalettes.pal').write_bytes(hardware)
(ROOT / 'validacao.txt').write_text('\n'.join(report) + '\nStatic export only; no ROM or animation modified.\n')

board = Image.new('RGB', (1050,735), '#f6f0e2')
d = ImageDraw.Draw(board)
def label(x,y,text,size=18,bold=False):
    path = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    d.text((x,y),text,font=ImageFont.truetype(path,size),fill='#30251b')
label(30,20,'AVENTUREIRO — ESPECIFICAÇÃO OFICIAL',28,True)
label(30,65,'Matrizes exatas do usuário • 16 × 24 px • 6 sprites por vista • sem overlays',18)
for x,name,title in [(90,'frente','FRENTE'),(420,'perfil','PERFIL DIREITO'),(750,'costas','COSTAS')]:
    label(x,115,title,20,True)
    im = Image.open(ROOT / f'{name}.png').convert('RGBA')
    big = im.resize((192,288), Image.Resampling.NEAREST)
    board.paste(big,(x,155),big)
    for y,color in [(474,'#398f32'),(580,'#eed8ac')]:
        d.rectangle((x,y,x+191,y+99), fill=color)
        board.paste(im,(x+30,y+38),im)
        scaled = im.resize((64,96),Image.Resampling.NEAREST)
        board.paste(scaled,(x+110,y+2),scaled)
label(30,451,'Acima: 12×. Abaixo: 1× e 4× sobre dois fundos. Abra em tamanho original.',16)
label(30,704,'RGBA fornecido pelo usuário • índices PPU preservados nos arquivos técnicos',17)
board.save(ROOT / 'prancha-oficial.png')
print('\n'.join(report))
