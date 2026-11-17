#!/usr/bin/env python3
"""mksheet.py <coat> — из src/<coat>_walk.png (3x2 кадра шага) и src/<coat>_pose.png (4x2 позы) на зелёном фоне
собирает ../overlay/sprites/fluffy_<coat>.webp: 7x2 кадров по CELL px.
ряд 0: шаг 0..5, стоит;  ряд 1: сидит, жмурится, спит, умывается, тянется, лежит, мяукает."""
import os, sys, numpy as np
from PIL import Image
from scipy import ndimage
CELL, SCALE, BASE = 320, 0.68, 300          # клетка, масштаб от исходника, линия пола
def key(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spill = g - np.maximum(r, b)
    alpha = 1 - np.clip((spill - 6) / 205, 0, 1)            # пиксель = a*цвет + (1-a)*зелёный
    alpha = np.where(alpha < 0.12, 0, alpha)
    am = np.maximum(alpha, 0.12)[..., None]
    c = (a - (1 - alpha[..., None]) * np.array([0, 255, 0], np.float32)) / am   # вычесть фон
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    g = np.minimum(g, np.maximum(r, b))                     # остаток зелёного отлива
    rgb = np.dstack([r, g, b])
    inner = ndimage.binary_erosion(alpha > 0.97, iterations=5)                  # кромке — цвет ближайшей шерсти
    idx = ndimage.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    rgb = np.where((~inner)[..., None], rgb[idx[0], idx[1]], rgb)
    return np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
def frames(path, n):
    im = key(path)
    lab, k = ndimage.label(im[..., 3] > 90)
    objs = ndimage.find_objects(lab)
    big = sorted([(o, (lab[o] == i + 1).sum()) for i, o in enumerate(objs)], key=lambda t: -t[1])[:n]
    H = im.shape[0]
    big = sorted([o for o, _ in big], key=lambda o: (o[0].start + o[0].stop > H, o[1].start))
    out = []
    for o in big:
        y0, y1, x0, x1 = max(o[0].start - 14, 0), o[0].stop + 14, max(o[1].start - 14, 0), o[1].stop + 14
        out.append(Image.fromarray(im[y0:y1, x0:x1]))
    return out
def place(sheet, fr, col, row, align):
    fr = fr.resize((round(fr.width * SCALE), round(fr.height * SCALE)), Image.LANCZOS)
    bb = fr.getchannel('A').point(lambda v: 255 if v > 90 else 0).getbbox()
    fr = fr.crop(bb)
    x = CELL - 14 - fr.width if align == 'right' else (CELL - fr.width) // 2
    sheet.alpha_composite(fr, (col * CELL + x, row * CELL + BASE - fr.height))
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    coat = sys.argv[1]
    walk, pose = frames(f'src/{coat}_walk.png', 6), frames(f'src/{coat}_pose.png', 8)
    assert len(walk) == 6 and len(pose) == 8, (len(walk), len(pose))
    sheet = Image.new('RGBA', (7 * CELL, 2 * CELL))
    for i, f in enumerate(walk): place(sheet, f, i, 0, 'right')
    place(sheet, pose[3], 6, 0, 'right')
    for i, j in enumerate([0, 1, 2, 4, 5, 6, 7]): place(sheet, pose[j], i, 1, 'center')
    out = f'../overlay/sprites/fluffy_{coat}.webp'
    sheet.save(out, quality=92, method=6); print(out, sheet.size)
