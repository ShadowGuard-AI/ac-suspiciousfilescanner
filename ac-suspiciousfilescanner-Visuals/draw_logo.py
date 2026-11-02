#!/usr/bin/env python3
"""ac-suspiciousfilescanner logo: one moon jelly from slightly below, Asset name spaced wide beneath."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(29)
HERE = __file__.rsplit('/', 1)[0]
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE + '/logo.png'
W, H = 900, 560
PALE = (243, 238, 224); INK = (16, 84, 96)
img = Image.new('RGB', (W, H), PALE)
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)
cx, cy, R = 450, 208, 158
rw, rh = R, R * 0.82
# bell dome: reef turquoise, deeper at the crown, lighter at the rim
ld.pieslice([cx - rw, cy - rh, cx + rw, cy + rh], 180, 360, fill=(52, 168, 178, 235))
ld.pieslice([cx - rw * 0.78, cy - rh * 0.8, cx + rw * 0.78, cy + rh * 0.78], 180, 360, fill=(96, 200, 202, 160))
ld.pieslice([cx - rw * 0.5, cy - rh * 0.62, cx + rw * 0.5, cy + rh * 0.55], 180, 360, fill=(140, 222, 216, 130))
# coral deepening at the centre where the inner organs show through
petal = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(petal)
for k in range(4):
    a = math.pi * (0.25 + 0.5 * k)
    gx, gy = cx + math.cos(a) * rw * 0.34, cy - rh * 0.3 + math.sin(a) * rh * 0.22
    pd.ellipse([gx - rw * 0.16, gy - rh * 0.14, gx + rw * 0.16, gy + rh * 0.14], fill=(240, 122, 134, 200))
petal = petal.filter(ImageFilter.GaussianBlur(4))
layer = Image.alpha_composite(layer, petal)
ld = ImageDraw.Draw(layer)
# bell opening seen from slightly below: a shallow rim ellipse under the dome,
# filled so dome and rim read as one bell, with the single sand band on the rim curve
ld.pieslice([cx - rw, cy - rh * 0.38, cx + rw, cy + rh * 0.38], 0, 180, fill=(52, 168, 178, 235))
ld.pieslice([cx - rw * 0.8, cy - rh * 0.3, cx + rw * 0.8, cy + rh * 0.3], 0, 180, fill=(96, 200, 202, 140))
ld.arc([cx - rw, cy - rh * 0.38, cx + rw, cy + rh * 0.38], 12, 168, fill=(226, 202, 150, 255), width=11)
ld.arc([cx - rw, cy - rh * 0.38, cx + rw, cy + rh * 0.38], 8, 172, fill=(224, 246, 242, 200), width=2)
base = cy + rh * 0.34
# four oral arms drifting down in a loose cluster
for k in range(4):
    ax = cx + (k - 1.5) * rw * 0.17
    pts = []
    for s in range(15):
        t = s / 14
        pts.append((ax + math.sin(t * 6 + k * 1.9) * rw * 0.11 * (0.3 + t), base + t * R * (0.68 + 0.1 * (k % 2))))
    ld.line(pts, fill=(238, 172, 178, 175), width=8)
    ld.line(pts, fill=(250, 212, 208, 130), width=4)
# fringe of fine tentacles falling unevenly around the arms
for i in range(46):
    t = i / 45
    ax = cx - rw * 0.94 + t * rw * 1.88
    ay = base + math.sin(t * math.pi) * rh * 0.08
    ln = R * random.uniform(0.38, 0.82)
    pts = [(ax + math.sin(s * 0.6 + i * 1.3) * 3.2, ay + s * ln / 7) for s in range(8)]
    ld.line(pts, fill=(120, 196, 198, 165), width=1)
layer = layer.filter(ImageFilter.GaussianBlur(0.6))
img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
d = ImageDraw.Draw(img)
# name in Asset, letterspaced like marks at intervals along a sounding line, fitted to the frame
t = 'ac-suspiciousfilescanner'
size, track = 34, 5
while size > 16:
    f = ImageFont.truetype(HERE + '/fonts/Asset.ttf', size)
    widths = [d.textlength(ch, font=f) for ch in t]
    if sum(widths) + track * (len(t) - 1) <= W - 70:
        break
    size -= 2
total = sum(widths) + track * (len(t) - 1)
x = (W - total) / 2
for ch, wch in zip(t, widths):
    d.text((x, 486), ch, font=f, fill=INK)
    x += wch + track
img.save(OUT)
img.resize((64, 40)).save(HERE + '/scratch/logo64-ship.png')
print('saved', OUT)
