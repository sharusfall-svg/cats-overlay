#!/usr/bin/env python3
"""src/box.png (закрытая + открытая коробка на зелёном) → ../overlay/sprites/box.webp: 3 кадра 300x240 — закрытая, открытая, передняя стенка открытой."""
import os, numpy as np
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from mksheet import key
CW, CH, SC, FRONT_Y = 300, 240, 0.3, 388      # FRONT_Y — верх переднего клапана в исходнике
im = key('src/box.png'); half = im.shape[1] // 2
im[:, half - 40:half] = 0                      # кусочек клапана соседней коробки
front = im.copy(); front[:FRONT_Y] = 0; front[:, :half + 78] = 0; front[:, half + 793:] = 0
sheet = Image.new('RGBA', (3 * CW, CH))
for i, a in enumerate([im[:, :half], im[:, half:], front[:, half:]]):
    ref = Image.fromarray(im[:, :half] if i == 0 else im[:, half:])
    bb = ref.getchannel('A').point(lambda v: 255 if v > 90 else 0).getbbox()
    fr = Image.fromarray(a).crop(bb); fr = fr.resize((round(fr.width * SC), round(fr.height * SC)), Image.LANCZOS)
    sheet.alpha_composite(fr, (i * CW + (CW - fr.width) // 2, CH - 4 - fr.height))
sheet.save('../overlay/sprites/box.webp', quality=92, method=6); print(sheet.size)
