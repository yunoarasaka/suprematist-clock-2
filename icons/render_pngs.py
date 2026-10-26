#!/usr/bin/env python3
"""Render suprematist-clock.png icons from the same geometry as the SVG."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SIZES = (256, 128, 64, 48)

BLACK = (5, 5, 5, 255)
INK = (12, 12, 12, 255)
PAPER = (235, 228, 212, 255)
WHITE = (245, 242, 234, 255)
RED = (192, 21, 42, 255)
YELLOW = (224, 184, 58, 255)
BLUE = (21, 36, 94, 255)


def sx(v: float, s: int) -> float:
    return v * s / 512.0


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), BLACK)
    d = ImageDraw.Draw(img)
    S = lambda v: sx(v, size)  # noqa: E731

    # Blue tower
    d.rectangle([S(28), S(318), S(28 + 88), S(318 + 148)], fill=BLUE)

    # Yellow beam (approx rotated bar as axis-aligned for small sizes)
    d.rectangle([S(360), S(52), S(360 + 118), S(52 + 22)], fill=YELLOW)

    # White ring
    r = S(42)
    cx, cy = S(430), S(400)
    sw = max(2, int(S(10)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(245, 242, 234, 217), width=sw)

    # Face
    cx, cy, r = S(256), S(256), S(168)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PAPER)

    # Black square
    d.rectangle([S(78), S(72), S(78 + 118), S(72 + 118)], fill=INK)

    # Accents
    d.rectangle([S(308), S(102), S(308 + 42), S(102 + 42)], fill=RED)
    d.rectangle([S(86), S(310), S(86 + 64), S(310 + 14)], fill=BLUE)
    ar = S(10)
    ax, ay = S(148), S(158)
    d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=YELLOW)

    # Major marks
    mark_w = max(1, int(S(5)))
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        inner, outer = S(138), S(156)
        x1 = cx + math.sin(rad) * inner
        y1 = cy - math.cos(rad) * inner
        x2 = cx + math.sin(rad) * outer
        y2 = cy - math.cos(rad) * outer
        d.line([(x1, y1), (x2, y2)], fill=INK, width=mark_w)

    def hand_rect(angle_deg: float, width: float, length: float, color, y_from_center: float):
        """Draw a bar hand rotated around center (clock angles: 0 = up)."""
        # Build polygon of a vertical rect then rotate
        half_w = S(width) / 2
        top = cy - S(y_from_center)
        bottom = top + S(length)
        pts = [
            (cx - half_w, top),
            (cx + half_w, top),
            (cx + half_w, bottom),
            (cx - half_w, bottom),
        ]
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rot = []
        for x, y in pts:
            dx, dy = x - cx, y - cy
            rot.append((cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a))
        d.polygon(rot, fill=color)

    # ~10:10 pose — hour -60°, minute +60°, second +150° (CSS rotate clockwise from 12)
    hand_rect(-60, 16, 126, INK, 118)
    hand_rect(60, 12, 172, BLUE, 164)
    # Second hand line + tail
    rad = math.radians(150)
    tip = (cx + math.sin(rad) * S(178), cy - math.cos(rad) * S(178))
    tail = (cx - math.sin(rad) * S(24), cy + math.cos(rad) * S(24))
    d.line([tail, tip], fill=RED, width=max(2, int(S(3))))
    hand_rect(150, 8, 36, RED, -12)

    # Hub
    for r, color in ((S(14), INK), (S(8), RED), (S(4), YELLOW)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    return img


def main() -> None:
    for size in SIZES:
        path = OUT / f"suprematist-clock-{size}.png"
        draw_icon(size).save(path, "PNG")
        print(f"wrote {path}")
    # Canonical 256 without size suffix for simple Icon= paths
    (OUT / "suprematist-clock.png").write_bytes(
        (OUT / "suprematist-clock-256.png").read_bytes()
    )
    print(f"wrote {OUT / 'suprematist-clock.png'}")


if __name__ == "__main__":
    main()
