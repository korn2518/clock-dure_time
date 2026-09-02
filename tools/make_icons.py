#!/usr/bin/env python3
"""두레 HUD 아이콘 생성기 — 네온 HUD 알람시계."""
import os
import cairosvg

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
os.makedirs(OUT, exist_ok=True)

NEON = "#34e5ff"
NEON2 = "#7ef0ff"
DEEP = "#0a1018"


def clock(cx, cy, r, glow=True):
    """시계 본체 그룹 (반지름 r 기준 상대 배치)."""
    k = r / 150.0
    # 눈 / 입 위치
    eye_y = cy + 0.30 * r
    eye_dx = 0.36 * r
    eye_r = 0.115 * r
    parts = []

    # --- 벨 두 개 ---
    bell_dx = 0.80 * r
    bell_dy = -0.80 * r
    for sx in (-1, 1):
        parts.append(
            f'<path d="M {cx + sx*bell_dx - sx*0.34*r:.1f} {cy + bell_dy + 0.30*r:.1f} '
            f'a {0.36*r:.1f} {0.36*r:.1f} 0 1 {1 if sx>0 else 0} {sx*0.60*r:.1f} {-0.16*r:.1f} Z" '
            f'fill="url(#bell)" stroke="{NEON}" stroke-width="{9*k:.1f}" stroke-linejoin="round"/>'
        )
    # 벨 사이 손잡이
    parts.append(
        f'<rect x="{cx - 0.16*r:.1f}" y="{cy - 1.20*r:.1f}" width="{0.32*r:.1f}" height="{0.20*r:.1f}" '
        f'rx="{0.10*r:.1f}" fill="{NEON}" opacity=".9"/>'
    )

    # --- 다리 ---
    for sx in (-1, 1):
        parts.append(
            f'<path d="M {cx + sx*0.60*r:.1f} {cy + 0.82*r:.1f} L {cx + sx*0.86*r:.1f} {cy + 1.12*r:.1f}" '
            f'stroke="{NEON}" stroke-width="{20*k:.1f}" stroke-linecap="round" opacity=".85"/>'
        )

    # --- 본체 ---
    g = ' filter="url(#glow)"' if glow else ""
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="url(#dial)" stroke="{NEON}" stroke-width="{16*k:.1f}"{g}/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.83:.1f}" fill="none" stroke="{NEON}" stroke-width="{3*k:.1f}" opacity=".35"/>')

    # --- 눈금 (12개) ---
    import math
    for i in range(12):
        a = math.radians(i * 30 - 90)
        big = (i % 3 == 0)
        r1 = r * 0.72
        x = cx + math.cos(a) * r1
        y = cy + math.sin(a) * r1
        rr = (0.055 if big else 0.032) * r
        op = ".95" if big else ".45"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{NEON2}" opacity="{op}"/>')

    # --- 시침 · 분침 (위쪽으로만) ---
    parts.append(
        f'<path d="M {cx} {cy} L {cx - 0.30*r:.1f} {cy - 0.42*r:.1f}" stroke="#ffffff" '
        f'stroke-width="{20*k:.1f}" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="M {cx} {cy} L {cx + 0.34*r:.1f} {cy - 0.52*r:.1f}" stroke="{NEON2}" '
        f'stroke-width="{15*k:.1f}" stroke-linecap="round"/>'
    )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{0.075*r:.1f}" fill="#ffffff"/>')

    # --- 귀여운 얼굴 ---
    for sx in (-1, 1):
        parts.append(f'<ellipse cx="{cx + sx*eye_dx:.1f}" cy="{eye_y:.1f}" rx="{eye_r:.1f}" ry="{eye_r*1.15:.1f}" fill="#ffffff"/>')
        parts.append(f'<circle cx="{cx + sx*eye_dx + 0.03*r:.1f}" cy="{eye_y - 0.03*r:.1f}" r="{eye_r*0.34:.1f}" fill="{DEEP}"/>')
    parts.append(
        f'<path d="M {cx - 0.17*r:.1f} {eye_y + 0.20*r:.1f} Q {cx} {eye_y + 0.40*r:.1f} {cx + 0.17*r:.1f} {eye_y + 0.20*r:.1f}" '
        f'fill="none" stroke="#ffffff" stroke-width="{12*k:.1f}" stroke-linecap="round" opacity=".92"/>'
    )
    # 볼터치
    for sx in (-1, 1):
        parts.append(f'<ellipse cx="{cx + sx*0.60*r:.1f}" cy="{eye_y + 0.10*r:.1f}" rx="{0.12*r:.1f}" ry="{0.075*r:.1f}" fill="#ff7ac6" opacity=".38"/>')

    return "\n".join(parts)


DEFS = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#101a2b"/><stop offset="1" stop-color="#070c14"/>
  </linearGradient>
  <radialGradient id="halo" cx="50%" cy="46%" r="58%">
    <stop offset="0" stop-color="{NEON}" stop-opacity=".34"/>
    <stop offset="1" stop-color="{NEON}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="dial" cx="50%" cy="34%" r="72%">
    <stop offset="0" stop-color="#16273c"/><stop offset="1" stop-color="#0a121d"/>
  </radialGradient>
  <linearGradient id="bell" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1c3348"/><stop offset="1" stop-color="#0d1826"/>
  </linearGradient>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="10" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
"""


def svg(maskable=False, rounded=True, transparent=False):
    if maskable:
        cx, cy, r = 256, 262, 104          # 세이프존(중앙 80%) 안쪽
        bgshape = '<rect width="512" height="512" fill="url(#bg)"/>'
    else:
        cx, cy, r = 256, 280, 146
        if transparent:
            bgshape = ""
        elif rounded:
            bgshape = '<rect width="512" height="512" rx="116" ry="116" fill="url(#bg)"/>'
        else:
            bgshape = '<rect width="512" height="512" fill="url(#bg)"/>'
    halo = '' if transparent else f'<circle cx="{cx}" cy="{cy}" r="{r*1.9:.0f}" fill="url(#halo)"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
{DEFS}
{bgshape}
{halo}
{clock(cx, cy, r)}
</svg>"""


def write(name, data):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(data)
    print("svg  ", name)


def png(src_svg, name, size):
    p = os.path.join(OUT, name)
    cairosvg.svg2png(bytestring=src_svg.encode(), write_to=p,
                     output_width=size, output_height=size)
    print("png  ", name, os.path.getsize(p), "bytes")


main = svg()
mask = svg(maskable=True)
flat = svg(rounded=False)

write("icon.svg", main)
write("icon-maskable.svg", mask)

png(main, "icon-192.png", 192)
png(main, "icon-512.png", 512)
png(mask, "icon-maskable-192.png", 192)
png(mask, "icon-maskable-512.png", 512)
png(flat, "apple-touch-icon.png", 180)
png(main, "favicon-32.png", 32)
png(main, "favicon-16.png", 16)
png(main, "og-image.png", 512)
print("done")
