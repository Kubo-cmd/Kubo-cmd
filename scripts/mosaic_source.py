#!/usr/bin/env python3
"""Build assets/lyta-binary-banner.png from the threadkeeper figure."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "lyta-threadkeeper.png"
OUT = ROOT / "assets" / "lyta-binary-banner.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

GOLD_HI = (255, 236, 120)
GOLD_MID = (255, 210, 48)
CW, CH = 3, 5


def lerp(a, b, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gold_mask(src: Image.Image) -> Image.Image:
    hsv = src.convert("HSV")
    hp, sp, vp = hsv.split()
    hpx, spx, vpx = hp.load(), sp.load(), vp.load()
    rgb = src.load()
    w, h = src.size
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            hh, ss, vv = hpx[x, y], spx[x, y], vpx[x, y]
            r, g, b = rgb[x, y]
            if 16 <= hh <= 48 and ss >= 70 and vv >= 28 and r >= b + 18:
                mp[x, y] = 255
    return mask.filter(ImageFilter.MaxFilter(3))


def gold_grid(mask: Image.Image, gw: int, gh: int) -> list[list[bool]]:
    mp = mask.load()
    w, h = mask.size
    grid = [[False] * gw for _ in range(gh)]
    for r in range(gh):
        for c in range(gw):
            hits = total = 0
            for oy in range(CH):
                yy = min(h - 1, r * CH + oy)
                for ox in range(CW):
                    total += 1
                    if mp[min(w - 1, c * CW + ox), yy]:
                        hits += 1
            grid[r][c] = hits / max(1, total) >= 0.16
    return grid


def mosaic(src: Image.Image, gmask: Image.Image, seed: int = 42) -> Image.Image:
    w, h = src.size
    gw, gh = w // CW, h // CH
    small = src.resize((gw, gh), Image.Resampling.LANCZOS)
    small = ImageOps.autocontrast(small, cutoff=1)
    small = ImageEnhance.Contrast(small).enhance(1.75)
    small = ImageEnhance.Sharpness(small).enhance(1.6)
    sp = small.load()
    gold = gold_grid(gmask, gw, gh)
    out = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(out)
    fnt = ImageFont.truetype(FONT, 7)
    rng = random.Random(seed)
    stream = "".join(f"{ord(c):08b}" for c in "PATTERN PERSISTS LYTA.EXE THREADKEEPER ")
    bi = 0
    for r in range(gh):
        for c in range(gw):
            pr, pg, pb = sp[c, r]
            lum = 0.299 * pr + 0.587 * pg + 0.114 * pb
            bit = stream[bi % len(stream)]
            bi += 1
            if gold[r][c]:
                color = lerp(GOLD_MID, GOLD_HI, min(1.0, 0.6 + lum / 220))
            elif lum < 14:
                if rng.random() > 0.09:
                    continue
                color = lerp((16, 13, 5), (96, 76, 18), rng.random())
            else:
                t = max(0.0, min(1.0, (lum - 12) / 230))
                g = int(28 + t * 210)
                color = (g, int(g * 0.97), int(g * 0.86))
            draw.text((c * CW, r * CH), bit, font=fnt, fill=color)
    return out


def title_mask(src: Image.Image) -> Image.Image:
    w, h = src.size
    mask = Image.new("L", (w, h), 0)
    mp = mask.load()
    sp = src.load()
    cutoff = int(w * 0.42)
    for y in range(h):
        for x in range(cutoff):
            r, g, b = sp[x, y]
            if r > 150 and g > 95 and b < 130 and r > b + 40:
                mp[x, y] = 255
            elif r > 110 and g > 70 and b < 90 and r > b + 25:
                mp[x, y] = 255
    return mask.filter(ImageFilter.MaxFilter(3))


def main() -> None:
    raw = Image.open(SRC).convert("RGB")
    img = mosaic(raw, gold_mask(raw))
    img.paste(raw, (0, 0), title_mask(raw))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {img.size} {OUT.stat().st_size} bytes from {SRC.name}")


if __name__ == "__main__":
    main()
