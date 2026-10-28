#!/usr/bin/env python3
"""Render rounded-squircle suprematist-clock icons matching the actual clock geometry."""
from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
BUILD_DIR = OUT.parent / "build"
SIZES = (512, 256, 128, 64, 48)

BLACK = (7, 7, 9, 255)
INK = (12, 12, 12, 255)
PAPER = (235, 228, 212, 255)
WHITE = (245, 242, 234, 255)
RED = (192, 21, 42, 255)
YELLOW = (224, 184, 58, 255)
BLUE = (21, 36, 94, 255)


def rotated_rect_pts(
    x: float,
    y: float,
    w: float,
    h: float,
    deg: float,
    piv_x: float,
    piv_y: float,
) -> list[tuple[float, float]]:
    rad = math.radians(deg)
    ca, sa = math.cos(rad), math.sin(rad)
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    out = []
    for px, py in corners:
        dx, dy = px - piv_x, py - piv_y
        out.append((piv_x + dx * ca - dy * sa, piv_y + dx * sa + dy * ca))
    return out


def rotated_poly_pts(
    pts: list[tuple[float, float]],
    deg: float,
    tx: float,
    ty: float,
) -> list[tuple[float, float]]:
    rad = math.radians(deg)
    ca, sa = math.cos(rad), math.sin(rad)
    return [(tx + x * ca - y * sa, ty + x * sa + y * ca) for x, y in pts]


def render_master(canvas_size: int = 2048) -> Image.Image:
    """Render master icon at 2048x2048 in 512x512 coordinate space, then clip to squircle."""
    S = lambda v: v * canvas_size / 512.0  # noqa: E731

    # Draw full scene onto opaque layer first
    scene = Image.new("RGBA", (canvas_size, canvas_size), BLACK)
    d = ImageDraw.Draw(scene)

    # ——— Background field planes (matching index.html .field) ———
    # White slab top-left
    d.rectangle([S(34), S(36), S(34 + 84), S(36 + 84)], fill=(235, 228, 212, 235))
    # Red banner top-right (rotated -6 deg)
    d.polygon(
        rotated_rect_pts(S(344), S(38), S(136), S(58), -6, S(412), S(67)),
        fill=RED,
    )
    # Yellow beam bottom-left (rotated 3.5 deg)
    d.polygon(
        rotated_rect_pts(S(42), S(438), S(210), S(12), 3.5, S(42), S(438)),
        fill=YELLOW,
    )
    # Blue tower bottom-right
    d.rectangle([S(404), S(336), S(404 + 68), S(336 + 136)], fill=BLUE)
    # White disk mid-left
    d.ellipse([S(48 - 28), S(264 - 28), S(48 + 28), S(264 + 28)], fill=(245, 242, 234, 230))
    # Red chip bottom-left
    d.rectangle([S(108), S(368), S(108 + 28), S(368 + 28)], fill=RED)

    # ——— Clock composition (offset +16, +16 so 240,240 dial center is at 256,256) ———
    OX, OY = 16.0, 16.0
    CX, CY = S(OX + 240), S(OY + 240)
    OUTER = S(168)

    # Asymmetric yellow bar behind top-right of face
    d.polygon(
        rotated_rect_pts(
            S(OX + 340),
            S(OY + 56),
            S(110),
            S(22),
            8,
            S(OX + 340),
            S(OY + 56),
        ),
        fill=YELLOW,
    )

    # White ring bottom-right
    rcx, rcy, rr = S(OX + 400), S(OY + 360), S(48)
    d.ellipse(
        [rcx - rr, rcy - rr, rcx + rr, rcy + rr],
        outline=(245, 242, 234, 218),
        width=max(2, int(S(10))),
    )

    # Clock face disk
    d.ellipse([CX - OUTER, CY - OUTER, CX + OUTER, CY + OUTER], fill=PAPER)

    # Malevich Black Square overlapping the face
    d.rectangle(
        [S(OX + 72), S(OY + 64), S(OX + 72 + 118), S(OY + 64 + 118)],
        fill=INK,
    )

    # Static face accents
    d.rectangle(
        [S(OX + 78), S(OY + 292), S(OX + 78 + 64), S(OY + 292 + 14)],
        fill=BLUE,
    )
    ay_x, ay_y, ay_r = S(OX + 136), S(OY + 148), S(10)
    d.ellipse([ay_x - ay_r, ay_y - ay_r, ay_x + ay_r, ay_y + ay_r], fill=YELLOW)

    # 60 dial marks (cardinal, major, minor — exact same math as js/clock.js)
    for i in range(60):
        angle = (i / 60.0) * math.pi * 2.0 - math.pi / 2.0
        major = i % 5 == 0
        cardinal = i % 15 == 0
        length = S(26 if cardinal else (18 if major else 8))
        inset = S(6 if cardinal else (8 if major else 12))
        x1 = CX + math.cos(angle) * (OUTER - inset)
        y1 = CY + math.sin(angle) * (OUTER - inset)
        x2 = CX + math.cos(angle) * (OUTER - inset - length)
        y2 = CY + math.sin(angle) * (OUTER - inset - length)
        w = int(S(7 if cardinal else (5 if major else 2.2)))
        color = INK if major else (12, 12, 12, 110)
        d.line([(x1, y1), (x2, y2)], fill=color, width=max(1, w))

    # Orbital hour indicator: blue vertical bar (x=212, y=12, w=56, h=100) rotated +34 deg (~1:05)
    d.polygon(
        rotated_rect_pts(
            S(OX + 212),
            S(OY + 12),
            S(56),
            S(100),
            34,
            CX,
            CY,
        ),
        fill=BLUE,
    )

    # Orbital minute indicator: red square (x=219, y=51, w=42, h=42) rotated +128 deg (~4:15)
    d.polygon(
        rotated_rect_pts(
            S(OX + 219),
            S(OY + 51),
            S(42),
            S(42),
            128,
            CX,
            CY,
        ),
        fill=RED,
    )

    # Flying second hand spear (pivot at 248, 234 in clock space, rotated 226 deg)
    piv_sx, piv_sy = S(OX + 248), S(OY + 234)
    sec_angle = 226.0
    # Main shaft: x=-2.5, y=-176, w=5, h=190
    d.polygon(
        rotated_rect_pts(
            piv_sx - S(2.5),
            piv_sy - S(176),
            S(5),
            S(190),
            sec_angle,
            piv_sx,
            piv_sy,
        ),
        fill=RED,
    )
    # Triangular tip: (0, -188), (-6.5, -170), (6.5, -170)
    d.polygon(
        rotated_poly_pts(
            [(0, -S(188)), (-S(6.5), -S(170)), (S(6.5), -S(170))],
            sec_angle,
            piv_sx,
            piv_sy,
        ),
        fill=RED,
    )
    # Tail: x=-5, y=8, w=10, h=36
    d.polygon(
        rotated_rect_pts(
            piv_sx - S(5),
            piv_sy + S(8),
            S(10),
            S(36),
            sec_angle,
            piv_sx,
            piv_sy,
        ),
        fill=RED,
    )

    # Three-layer Suprematist center hub
    for r_val, col in ((15, INK), (9, RED), (4.5, YELLOW)):
        r = S(r_val)
        d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=col)

    # ——— Apply rounded squircle mask (margin 16, corner radius 112 in 512 space) ———
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle(
        [S(16), S(16), S(496), S(496)],
        radius=S(112),
        fill=255,
    )

    out = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    out.paste(scene, (0, 0), mask=mask)

    # Subtle outer rim on the squircle so dark docks/themes show a clean silhouette
    rim = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rounded_rectangle(
        [S(17.5), S(17.5), S(494.5), S(494.5)],
        radius=S(110.5),
        outline=(245, 242, 234, 48),
        width=max(2, int(S(3))),
    )
    out = Image.alpha_composite(out, rim)
    return out


def main() -> None:
    master = render_master(2048)

    for size in SIZES:
        resized = master.resize((size, size), Image.Resampling.LANCZOS)
        path = OUT / f"suprematist-clock-{size}.png"
        resized.save(path, "PNG")
        print(f"wrote {path}")

    # Canonical suprematist-clock.png (256x256) & build/icon.png (512x512)
    shutil.copyfile(OUT / "suprematist-clock-256.png", OUT / "suprematist-clock.png")
    print(f"wrote {OUT / 'suprematist-clock.png'}")

    if BUILD_DIR.is_dir():
        shutil.copyfile(OUT / "suprematist-clock-512.png", BUILD_DIR / "icon.png")
        print(f"wrote {BUILD_DIR / 'icon.png'}")

    # Generate macOS .icns
    icon_512 = master.resize((512, 512), Image.Resampling.LANCZOS)
    icns_path = OUT / "suprematist-clock.icns"
    icon_512.save(icns_path, format="ICNS")
    print(f"wrote {icns_path}")
    if BUILD_DIR.is_dir():
        shutil.copyfile(icns_path, BUILD_DIR / "icon.icns")
        print(f"wrote {BUILD_DIR / 'icon.icns'}")


if __name__ == "__main__":
    main()
