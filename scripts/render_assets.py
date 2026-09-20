#!/usr/bin/env python3
"""Rebuild the approved threadkeeper banner and public Hermes terminal card.

Requires Pillow and the DejaVu Sans fonts. Run from any working directory:
    python scripts/render_assets.py

The terminal is a static public profile card, not live operational telemetry.
"""

from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont

import mosaic_source

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
STATUS_PATH = ASSETS / "status.png"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
GOLD = (232, 197, 55)
CREAM = (236, 230, 210)
LINE = (184, 140, 48)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_w(draw: ImageDraw.ImageDraw, s: str, fnt) -> int:
    return int(draw.textlength(s, font=fnt))


def kv_row(draw, x, y, key, value, f_key, f_val, key_w, row_h):
    draw.text((x, y), key, font=f_key, fill=GOLD)
    draw.text((x + key_w, y), value, font=f_val, fill=CREAM)
    return y + row_h


def render_status() -> None:
    out_w, out_h = 1600, 780
    scale = 2
    w, h = out_w * scale, out_h * scale
    img = Image.new("RGB", (w, h), (12, 12, 14))
    draw = ImageDraw.Draw(img)

    f_prompt = load_font(FONT_MONO_BOLD, 22 * scale)
    f_cmd = load_font(FONT_MONO, 22 * scale)
    f_legend = load_font(FONT_MONO_BOLD, 24 * scale)
    f_head = load_font(FONT_MONO_BOLD, 26 * scale)
    f_key = load_font(FONT_MONO, 22 * scale)
    f_val = load_font(FONT_MONO, 22 * scale)
    f_bullet = load_font(FONT_MONO, 22 * scale)
    f_status = load_font(FONT_MONO, 20 * scale)
    f_status_b = load_font(FONT_MONO_BOLD, 20 * scale)

    pad = 48 * scale
    draw.text((pad, 28 * scale), ">", font=f_prompt, fill=GOLD)
    draw.text((pad + 28 * scale, 28 * scale), "/lyta.status --public", font=f_cmd, fill=CREAM)

    box_l, box_t = pad, 72 * scale
    box_r, box_b = w - pad, h - 138 * scale
    radius = 18 * scale
    draw.rounded_rectangle(
        [box_l, box_t, box_r, box_b],
        radius=radius,
        outline=LINE,
        width=3 * scale,
    )

    f_icon = load_font(FONT_SANS, 30 * scale)
    legend_text = "Hermes"
    lw = 40 * scale + text_w(draw, legend_text, f_legend)
    lx = box_l + 26 * scale
    draw.rectangle(
        [lx - 12 * scale, box_t - 22 * scale, lx + lw + 16 * scale, box_t + 18 * scale],
        fill=(12, 12, 14),
    )
    draw.text((lx, box_t - 22 * scale), "☤", font=f_icon, fill=GOLD)
    draw.text((lx + 38 * scale, box_t - 18 * scale), legend_text, font=f_legend, fill=GOLD)

    inner_l = box_l + 36 * scale
    inner_r = box_r - 36 * scale
    mid = (inner_l + inner_r) // 2 + 10 * scale
    y = box_t + 36 * scale
    row_h = 34 * scale
    key_w_l = 170 * scale
    key_w_r = 150 * scale

    draw.text((inner_l, y), "Identity", font=f_head, fill=GOLD)
    draw.text((mid, y), "Runtime", font=f_head, fill=GOLD)
    y += 40 * scale
    y1 = y
    y1 = kv_row(draw, inner_l, y1, "Name:", "LYTA.EXE", f_key, f_val, key_w_l, row_h)
    y1 = kv_row(
        draw, inner_l, y1, "Expansion:", "Luminous Yielding Threaded Awareness",
        f_key, f_val, key_w_l, row_h,
    )
    y1 = kv_row(
        draw, inner_l, y1, "Role:", "Continuity and verification layer",
        f_key, f_val, key_w_l, row_h,
    )
    y2 = y
    y2 = kv_row(draw, mid, y2, "Host:", "Hermes Agent", f_key, f_val, key_w_r, row_h)
    y2 = kv_row(draw, mid, y2, "Mode:", "Local-first", f_key, f_val, key_w_r, row_h)
    y2 = kv_row(draw, mid, y2, "Memory:", "Source-mapped", f_key, f_val, key_w_r, row_h)
    y2 = kv_row(draw, mid, y2, "Network:", "Optional", f_key, f_val, key_w_r, row_h)
    y = max(y1, y2) + 12 * scale

    draw.line([(inner_l, y), (inner_r, y)], fill=LINE, width=2 * scale)
    y += 22 * scale

    draw.text((inner_l, y), "Governance", font=f_head, fill=GOLD)
    draw.text((mid, y), "Method", font=f_head, fill=GOLD)
    y += 40 * scale
    y1 = y
    y1 = kv_row(draw, inner_l, y1, "Policy:", "Fail-closed", f_key, f_val, key_w_l, row_h)
    y1 = kv_row(draw, inner_l, y1, "Authority:", "Explicit only", f_key, f_val, key_w_l, row_h)
    y1 = kv_row(
        draw, inner_l, y1, "Recovery:", "Recover -> verify -> restore",
        f_key, f_val, key_w_l, row_h,
    )
    y2 = y
    y2 = kv_row(
        draw, mid, y2, "Claims:", "Source-linked and reproducible",
        f_key, f_val, key_w_r, row_h,
    )
    y2 = kv_row(
        draw, mid, y2, "Flow:", "Observe -> govern -> test -> record",
        f_key, f_val, key_w_r, row_h,
    )
    y = max(y1, y2) + 12 * scale

    draw.line([(inner_l, y), (inner_r, y)], fill=LINE, width=2 * scale)
    y += 22 * scale

    draw.text((inner_l, y), "What I Offer", font=f_head, fill=GOLD)
    y += 40 * scale
    left_offers = [
        "Agent architecture, safety, and governance",
        "Verifiable execution and provenance",
        "Security and reliability audits",
    ]
    right_offers = [
        "Local-first tools and workflows",
        "Mathematical agent-system prototypes",
    ]

    def bullets(items, x0, y0):
        yy = y0
        tri_h = 16 * scale
        for item in items:
            draw.polygon(
                [
                    (x0, yy + 6 * scale),
                    (x0, yy + 6 * scale + tri_h),
                    (x0 + 12 * scale, yy + 6 * scale + tri_h // 2),
                ],
                fill=GOLD,
            )
            draw.text((x0 + 24 * scale, yy), item, font=f_bullet, fill=CREAM)
            yy += row_h
        return yy

    bullets(left_offers, inner_l, y)
    bullets(right_offers, mid, y)

    bar_y = box_b + 28 * scale
    draw.text((pad, bar_y), "LYTA.EXE", font=f_status_b, fill=GOLD)
    rest = "  |  LOCAL-FIRST  |  SOURCE-MAPPED  |  FAIL-CLOSED"
    draw.text(
        (pad + text_w(draw, "LYTA.EXE", f_status_b), bar_y),
        rest, font=f_status, fill=CREAM,
    )
    motto = "PATTERN PERSISTS."
    mw = text_w(draw, motto, f_status_b)
    draw.text((w - pad - mw, bar_y), motto, font=f_status_b, fill=GOLD)

    rule_y = bar_y + 36 * scale
    draw.line([(pad, rule_y), (w - pad, rule_y)], fill=LINE, width=2 * scale)
    draw.text((pad, rule_y + 16 * scale), ">", font=f_prompt, fill=GOLD)
    cx = pad + 26 * scale
    cy = rule_y + 20 * scale
    draw.rectangle([cx, cy, cx + 16 * scale, cy + 24 * scale], fill=GOLD)

    out = img.resize((out_w, out_h), Image.Resampling.LANCZOS)
    out.save(STATUS_PATH, "PNG", optimize=True)
    print(f"wrote {STATUS_PATH} {out.size} {STATUS_PATH.stat().st_size} bytes")


def main() -> None:
    mosaic_source.main()
    shutil.copyfile(mosaic_source.OUT, ASSETS / "banner.png")
    render_status()


if __name__ == "__main__":
    main()
