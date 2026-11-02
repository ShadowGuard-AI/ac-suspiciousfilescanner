#!/usr/bin/env python3
"""ac-suspiciousfilescanner wordmark banner: bloom in ranks in morning water,
name in Asset along a pale drift line at the upper edge, one word group per depth mark."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(71)
HERE = __file__.rsplit('/', 1)[0]
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE + '/banner.png'
W, H = 1200, 420
img = Image.new('RGB', (W, H), (34, 116, 152))
d = ImageDraw.Draw(img, 'RGBA')
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(112 - 58 * t), int(188 - 66 * t), int(208 - 48 * t)))
for sx in (240, 620, 960):
    d.polygon([(sx, 30), (sx + 70, 30), (sx + 170, H), (sx + 40, H)], fill=(255, 250, 220, 14))
# darker patch of water at the lower right
patch = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(patch).ellipse([830, 250, 1240, 470], fill=(10, 52, 84, 120))
img = Image.alpha_composite(img.convert('RGBA'), patch.filter(ImageFilter.GaussianBlur(28))).convert('RGB')
d = ImageDraw.Draw(img, 'RGBA')
# surface coins overhead, below the drift line
for _ in range(90):
    x = random.uniform(0, W); y = random.uniform(56, 88); rx = random.uniform(7, 24)
    d.ellipse([x - rx, y - rx * 0.26, x + rx, y + rx * 0.26], fill=(255, 246, 214, random.randint(36, 95)))
for _ in range(300):
    x = random.uniform(0, W); y = random.uniform(60, H - 8)
    d.ellipse([x, y, x + 2, y + 2], fill=(255, 244, 205, random.randint(50, 130)))

def jelly(cx, cy, R, phase, coral_edge=False):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    squash = 1 - 0.3 * phase
    rw, rh = R, R * 0.78 * squash
    ld.pieslice([cx - rw, cy - rh, cx + rw, cy + rh], 180, 360, fill=(94, 203, 206, 165))
    ld.pieslice([cx - rw * 0.78, cy - rh * 0.8, cx + rw * 0.78, cy + rh * 0.8], 180, 360, fill=(140, 224, 218, 115))
    if R > 26:
        petal = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(petal)
        for k in range(4):
            a = math.pi * (0.25 + 0.5 * k)
            gx, gy = cx + math.cos(a) * rw * 0.34, cy - rh * 0.3 + math.sin(a) * rh * 0.2
            pd.ellipse([gx - rw * 0.15, gy - rh * 0.13, gx + rw * 0.15, gy + rh * 0.13], fill=(243, 128, 140, 160))
        layer = Image.alpha_composite(layer, petal.filter(ImageFilter.GaussianBlur(max(1.5, R * 0.02))))
        ld = ImageDraw.Draw(layer)
    if coral_edge:
        ld.arc([cx - rw, cy - rh, cx + rw, cy + rh], 180, 360, fill=(246, 138, 146, 230), width=max(2, int(R * 0.07)))
    ld.arc([cx - rw, cy - rh * 0.22, cx + rw, cy + rh * 0.5], 8, 172, fill=(212, 244, 240, 200), width=max(1, int(R * 0.04)))
    base = cy + rh * 0.16
    for k in range(4):
        ax = cx + (k - 1.5) * rw * 0.19
        pts = [(ax + math.sin(s / 12 * 6 + k * 1.7) * rw * 0.11 * (0.3 + s / 12), base + s / 12 * R * 1.1) for s in range(13)]
        ld.line(pts, fill=(240, 182, 186, 125), width=max(1, int(R * 0.05)))
    n = max(9, int(R / 2.6))
    for i in range(n):
        t = i / max(1, n - 1)
        ax = cx - rw * 0.92 + t * rw * 1.84
        ln = R * random.uniform(0.9, 1.8)
        pts = [(ax + math.sin(s * 0.55 + i) * R * 0.03, base + s * ln / 7) for s in range(8)]
        ld.line(pts, fill=(216, 246, 244, 110), width=1)
    img.paste(Image.alpha_composite(img.convert('RGBA'), layer.filter(ImageFilter.GaussianBlur(0.6))).convert('RGB'), (0, 0))
    return ImageDraw.Draw(img, 'RGBA')

# ranks of decreasing size toward a turquoise distance, each at its own pulse point
ranks = [(330, 150, 40, 0.2), (420, 168, 34, 0.75), (500, 184, 29, 0.4), (572, 198, 25, 0.95),
         (636, 210, 21, 0.1), (692, 220, 18, 0.6), (742, 228, 15, 0.3), (786, 236, 13, 0.85),
         (824, 242, 11, 0.5), (262, 196, 26, 0.65), (858, 248, 9, 0.15), (356, 214, 20, 0.9)]
for (x, y, r, p) in ranks:
    d = jelly(x, y, r, p)
# nearest animal, large at the left, bell contracted mid pulse
d = jelly(128, 178, 74, 1.0)
# one jelly crossing the darker patch at the lower right, bell edges coral pink
d = jelly(1012, 306, 46, 0.35, coral_edge=True)
img = img.filter(ImageFilter.GaussianBlur(0.4))
d = ImageDraw.Draw(img, 'RGBA')
# pale drift line along the upper edge, with depth ticks; each word group rests on the line at its mark
d.line([(26, 44), (W - 26, 44)], fill=(238, 228, 196, 235), width=3)
f = ImageFont.truetype(HERE + '/fonts/Asset.ttf', 25)
groups = ['ac', 'suspicious', 'file', 'scanner']
marks = [56, 330, 660, 920]
for gx, word in zip(marks, groups):
    d.line([(gx, 32), (gx, 56)], fill=(238, 228, 196, 235), width=3)
    d.text((gx + 12, 8), word, font=f, fill=(240, 234, 208))
img.save(OUT)
print('saved', OUT)
