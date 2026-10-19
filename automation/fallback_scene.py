"""Original offline emergency artwork; no remote media or NASA dependency."""
import argparse
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def render(query, number, output):
    seed = int(hashlib.sha256(f'{query}|{number}'.encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    w, h = 800, 1280
    y, x = np.mgrid[:h, :w]
    base = np.empty((h, w, 3), dtype=np.uint8)
    haze = 11 * np.sin(x / (90 + number * 9) + y / 190) + rng.normal(0, 8, (h, w))
    for c, (lo, hi) in enumerate(((4, 20), (7, 28), (19, 49))):
        base[:, :, c] = np.clip(lo + (hi-lo) * y / h + haze, 0, 255)
    im = Image.fromarray(base, 'RGB')
    draw = ImageDraw.Draw(im)
    for i in range(850):
        sx, sy = int(rng.integers(0, w)), int(rng.integers(0, h))
        v = int(rng.integers(85, 245))
        radius = 1 if i % 12 else 2
        draw.ellipse((sx-radius, sy-radius, sx+radius, sy+radius), fill=(v, v, min(255, v+10)))
    query = query.lower()
    if any(k in query for k in ('sun', 'star', 'supernova')):
        color = np.array([240, 141, 50])
    elif 'mars' in query:
        color = np.array([171, 77, 48])
    elif 'neptune' in query:
        color = np.array([47, 102, 200])
    elif 'saturn' in query:
        color = np.array([190, 163, 107])
    elif 'jupiter' in query:
        color = np.array([191, 131, 77])
    else:
        color = np.array([45, 113, 180])
    cx = [390, 320, 510, 280, 410][(number-1)%5]
    cy = [650, 770, 620, 690, 720][(number-1)%5]
    r = [270, 235, 300, 220, 255][(number-1)%5]
    xx, yy = np.mgrid[-r:r+1, -r:r+1]
    norm = (xx.astype(float)**2 + yy.astype(float)**2) / (r*r)
    mask = norm <= 1
    depth = np.sqrt(np.clip(1-norm, 0, 1))
    lighting = np.clip(.24 + .83 * (depth*.8 - xx/r*.4 + yy/r*.14), .09, 1.2)
    bands = 1 + .09 * np.sin((xx + 2*yy)/26 + number) + .06 * rng.normal(0, 1, norm.shape)
    rgb = np.clip(color[None,None,:] * lighting[:,:,None] * bands[:,:,None], 0, 255).astype(np.uint8)
    patch = Image.fromarray(rgb, 'RGB')
    alpha = Image.fromarray((mask*255).astype(np.uint8), 'L')
    im.paste(patch, (cx-r, cy-r), alpha)
    draw = ImageDraw.Draw(im)
    if 'ring' in query or 'saturn' in query or number == 3:
        for delta in (18, 31, 44):
            draw.arc((cx-r-120-delta, cy-r//2-delta, cx+r+120+delta, cy+r//2+delta), 10, 175, fill=(218, 191, 131), width=5)
    for j in range(number % 3 + 1):
        mx = int((cx + 1.8*r + 48*j) % w)
        my = int((cy - 1.1*r + 76*j) % h)
        rr = 15 + 5*j
        draw.ellipse((mx-rr, my-rr, mx+rr, my+rr), fill=(138, 158, 182), outline=(218, 226, 233), width=2)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, 'PNG')
    if out.stat().st_size < 100000:
        raise RuntimeError('Emergency original scene is too small for validation')
    print('ORBIT_ORIGINAL_FALLBACK_OK', out, out.stat().st_size)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--query', required=True)
    p.add_argument('--number', type=int, required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    render(a.query, a.number, a.output)
