#!/usr/bin/env python3
"""ac-suspiciousfilescanner intro banner: moon jelly bloom in lit water, wordless.
Foreground jelly close at lower left, a dozen more on a diagonal, bright surface above."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
random.seed(117)
HERE = __file__.rsplit('/', 1)[0]
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE + '/intro-banner.png'
W, H = 1200, 520
TURQ = (64, 178, 186); DEEP = (18, 74, 116); CORAL = (240, 128, 138); SAND = (232, 214, 168)

img = Image.new('RGB', (W, H), (30, 110, 150))
d = ImageDraw.Draw(img, 'RGBA')
# water body: bright ceiling at top, deepening blue at the sides and bottom
for y in range(H):
    t = y / H
    for x in range(0, W, 8):
        edge = abs(x - W / 2) / (W / 2)
        r = int(120 - 62 * t - 34 * edge * t)
        g = int(196 - 74 * t - 20 * edge)
        b = int(214 - 52 * t - 6 * edge)
        d.rectangle([x, y, x + 8, y + 1], fill=(max(8, r), max(40, g), max(90, b)))
# surface light coins, broken sun at the very top
for _ in range(130):
    x = random.uniform(0, W); y = random.uniform(0, 64); rx = random.uniform(8, 30)
    d.ellipse([x - rx, y - rx * 0.28, x + rx, y + rx * 0.28], fill=(255, 246, 214, random.randint(40, 110)))
# soft shafts slanting down from the surface
for sx in (180, 470, 760, 1010):
    d.polygon([(sx, 0), (sx + 90, 0), (sx + 210, H), (sx + 60, H)], fill=(255, 250, 220, 16))
img = img.filter(ImageFilter.GaussianBlur(1.2))
d = ImageDraw.Draw(img, 'RGBA')
# drifting specks in the shafts
for _ in range(420):
    x = random.uniform(0, W); y = random.uniform(20, H - 10)
    d.ellipse([x, y, x + random.uniform(1, 2.6), y + random.uniform(1, 2.6)], fill=(255, 244, 205, random.randint(60, 150)))
# one slow column of tiny bubbles at the far right, near no animal
for i in range(16):
    y = 470 - i * 27; x = 1142 + math.sin(i * 0.9) * 7
    r = 2 + (i % 4)
    d.ellipse([x - r, y - r, x + r, y + r], outline=(235, 250, 252, 170), width=1)
    d.point((x - 1, y - 1), fill=(255, 255, 255, 200))

def jelly(cx, cy, R, phase, glow=False, detail=True):
    """One moon jelly. phase 0 = bell open, 1 = bell contracted mid pulse."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    squash = 1 - 0.26 * phase
    rw, rh = R, R * 0.78 * squash
    if glow:
        glow_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.ellipse([cx - rw * 1.45, cy - rh * 1.5, cx + rw * 1.45, cy + rh * 1.8], fill=(140, 235, 230, 90))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(46))
        layer = Image.alpha_composite(glow_layer, layer)
        ld = ImageDraw.Draw(layer)
    # bell dome, turquoise, translucent rim
    ld.pieslice([cx - rw, cy - rh, cx + rw, cy + rh], 180, 360, fill=(96, 205, 208, 168))
    ld.pieslice([cx - rw * 0.8, cy - rh * 0.82, cx + rw * 0.8, cy + rh * 0.8], 180, 360, fill=(140, 224, 220, 120))
    # coral structures showing through the dome: four soft petal masses, blurred, never outlined
    if detail:
        petal = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(petal)
        for k in range(4):
            a = math.pi * (0.25 + 0.5 * k)
            gx, gy = cx + math.cos(a) * rw * 0.36, cy - rh * 0.3 + math.sin(a) * rh * 0.22
            pd.ellipse([gx - rw * 0.15, gy - rh * 0.13, gx + rw * 0.15, gy + rh * 0.13], fill=(243, 128, 140, 170))
        petal = petal.filter(ImageFilter.GaussianBlur(max(1.5, R * 0.02)))
        layer = Image.alpha_composite(layer, petal)
        ld = ImageDraw.Draw(layer)
    # rim curling inward
    ld.arc([cx - rw, cy - rh * 0.24, cx + rw, cy + rh * 0.55], 8, 172, fill=(210, 244, 240, 210), width=max(2, int(R * 0.045)))
    base = cy + rh * 0.18
    # four oral arms, loose ribbons hanging from the centre
    for k in range(4):
        ax = cx + (k - 1.5) * rw * 0.2
        pts = []
        for s in range(15):
            t = s / 14
            pts.append((ax + math.sin(t * 6.2 + k * 1.7) * rw * 0.13 * (0.3 + t), base + t * R * (1.25 + 0.16 * (k % 2))))
        ld.line(pts, fill=(240, 182, 186, 130), width=max(2, int(R * 0.055)))
        ld.line(pts, fill=(252, 220, 214, 90), width=max(1, int(R * 0.026)))
    # fringe of fine tentacles, uneven lengths, all around the rim
    n = max(11, int(R / 2.4))
    for i in range(n):
        t = i / max(1, n - 1)
        ax = cx - rw * 0.92 + t * rw * 1.84
        ay = base + math.sin(t * math.pi) * rh * 0.1
        ln = R * random.uniform(0.95, 1.95)
        pts = [(ax + math.sin(s * 0.55 + i) * R * 0.035, ay + s * ln / 7) for s in range(8)]
        ld.line(pts, fill=(216, 246, 244, 120), width=1)
    layer = layer.filter(ImageFilter.GaussianBlur(0.7))
    img.paste(Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB'), (0, 0))
    return ImageDraw.Draw(img, 'RGBA')

# midground company on a gentle diagonal, each at its own pulse point
company = [(560, 150, 44, 0.15), (648, 178, 38, 0.7), (724, 205, 33, 0.35), (792, 232, 28, 0.9),
           (852, 256, 24, 0.1), (904, 276, 20, 0.55), (948, 294, 17, 0.8), (986, 310, 14, 0.25),
           (470, 205, 30, 0.6), (1018, 322, 12, 0.45), (1052, 334, 10, 0.05), (420, 258, 21, 0.85)]
for (x, y, r, p) in company:
    d = jelly(x + random.uniform(-6, 6), y + random.uniform(-5, 5), r, p, detail=(r > 22))
# foreground jelly, bell filling the lower left quadrant, arms trailing out of frame
d = jelly(212, 300, 205, 0.3, glow=True, detail=True)
img = img.filter(ImageFilter.GaussianBlur(0.4))
img.save(OUT)
print('saved', OUT)
