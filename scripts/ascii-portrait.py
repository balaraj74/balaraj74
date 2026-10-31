"""Renders an animated ASCII portrait with a neofetch-style panel.

Usage: python3 scripts/ascii-portrait.py <photo> assets/ascii-profile.svg
"""
import random
import sys
from xml.sax.saxutils import escape

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps

SOURCE, OUTPUT = sys.argv[1], sys.argv[2]

COLS, ROWS = 84, 53
CELL_W, CELL_H = 3.9, 8.1
RAMP = " .'`^,:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
WIDTH, HEIGHT = 900, 472
LEFT, TOP = 26, 22

INFO = [
    ("title", "balaraj@bengaluru"),
    ("rule", "-" * 34),
    ("Role", "AI/ML Engineer"),
    ("Focus", "Multi-agent systems, edge AI"),
    ("Backend", "Python, FastAPI, Node.js"),
    ("AI", "Vertex AI, LangGraph, llama.cpp"),
    ("Cloud", "GCP, Docker, Firebase"),
    ("Work", "Novabion, AatonovaZ"),
    ("Education", "PES University, CSE (AI & ML)"),
    ("Honours", "2x national hackathon winner"),
    ("OSS", "Ubuntu, pandas, NumPy"),
    ("Status", "Open to AI/ML roles"),
    ("Web", "balaraj.me"),
]

def cut_out(photo):
    """Separates the subject from a plain background, since the source has no transparency."""
    rgb = np.asarray(photo.convert("RGB"))[:, :, ::-1].copy()
    h, w = rgb.shape[:2]
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    mask[int(h * 0.04):, int(w * 0.20):int(w * 0.80)] = cv2.GC_PR_FGD
    mask[int(h * 0.20):int(h * 0.68), int(w * 0.32):int(w * 0.68)] = cv2.GC_FGD
    mask[int(h * 0.82):, int(w * 0.12):int(w * 0.92)] = cv2.GC_FGD
    mask[:int(h * 0.02), :] = cv2.GC_BGD
    mask[:int(h * 0.60), :int(w * 0.10)] = cv2.GC_BGD
    mask[:int(h * 0.60), int(w * 0.90):] = cv2.GC_BGD
    cv2.grabCut(rgb, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    subject = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)).astype(np.uint8) * 255
    subject = cv2.morphologyEx(subject, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return Image.merge("RGBA", (*photo.convert("RGB").split(), Image.fromarray(subject)))


image = cut_out(Image.open(SOURCE))
w, h = image.size
crop = image.crop((int(w * 0.12), 0, int(w * 0.88), h))
alpha = np.asarray(crop.getchannel("A").resize((COLS, ROWS), Image.LANCZOS), dtype=np.float32) / 255

gray = crop.convert("L")
mask = crop.getchannel("A")
tone = np.asarray(gray.resize((COLS, ROWS), Image.LANCZOS), dtype=np.uint8)
tone = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(3, 3)).apply(tone).astype(np.float32) / 255

# Edges keep the hairline, glasses and jaw readable where the tones alone go flat.
small = gray.resize((COLS * 3, ROWS * 3), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
edges = ImageOps.autocontrast(small.filter(ImageFilter.FIND_EDGES), cutoff=(0, 2))
edges = np.asarray(edges.resize((COLS, ROWS), Image.LANCZOS), dtype=np.float32) / 255

levels = np.clip(np.power(tone, 1.05) * 1.02 + edges * 0.22, 0, 1)
levels = np.where(alpha > 0.5, np.maximum(levels, 0.07), 0)

rows = []
for y in range(ROWS):
    runs, current, shade = [], "", None
    for x in range(COLS):
        value = levels[y, x]
        char = RAMP[min(int(value * len(RAMP)), len(RAMP) - 1)]
        tone = "w" if value > 0.84 else "a" if value > 0.6 else "b" if value > 0.3 else "c"
        if char == " ":
            tone = shade or tone
        if tone != shade and current:
            runs.append((shade, current))
            current = ""
        shade = tone
        current += char
    runs.append((shade, current))
    rows.append(runs)

BANDS = {3: (9, 15), 2: (19, 24), 1: (29, 33), 4: (38, 46)}
SCRAMBLED = [12, 13, 22, 23, 35, 36]
random.seed(7)


def row_y(y):
    return TOP + y * CELL_H + 8


def row_text(y, css, body, delay=None):
    timing = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
    return (
        f'<text class="{css}" x="{LEFT}" y="{row_y(y):.1f}" textLength="{COLS * CELL_W:.1f}" '
        f'lengthAdjust="spacing"{timing}>{body}</text>'
    )


def plain(y):
    return "".join(text for _, text in rows[y])


def band_of(y):
    return next((band for band, (start, end) in BANDS.items() if start <= y < end), 0)


groups = {band: [] for band in (0, 1, 2, 3, 4)}
ghosts = []
scramble = []
for y, runs in enumerate(rows):
    if not plain(y).strip():
        continue
    spans = "".join(f'<tspan class="{tone}">{escape(text)}</tspan>' for tone, text in runs)
    groups[band_of(y)].append(row_text(y, "row", spans, 0.25 + y * 0.03))
    ghosts.append(row_text(y, "ghost", escape(plain(y))))

for index, y in enumerate(SCRAMBLED):
    noise = "".join(random.choice(RAMP[20:]) if char != " " else " " for char in plain(y))
    scramble.append(
        f'<g class="scramble s{index % 3}"><rect x="{LEFT}" y="{row_y(y) - 7:.1f}" width="{COLS * CELL_W:.0f}" height="{CELL_H + 0.6}" fill="#0c0a09"/>'
        + row_text(y, "noise", escape(noise))
        + "</g>"
    )

ghost_rows = "".join(ghosts)
art = (
    f'<g class="split cyan">{ghost_rows}</g><g class="split red">{ghost_rows}</g>'
    + '<g class="flicker">'
    + "".join(f'<g class="band b{band}">{"".join(items)}</g>' for band, items in groups.items())
    + "".join(scramble)
    + "</g>"
)

info_x = LEFT + COLS * CELL_W + 26
info = []
y = 72
for index, (label, value) in enumerate(INFO):
    delay = 1.9 + index * 0.13
    if label == "title":
        body = f'<tspan class="key">{escape(value)}</tspan>'
    elif label == "rule":
        body = f'<tspan class="dim">{value}</tspan>'
    else:
        body = f'<tspan class="key">{label}</tspan><tspan class="sep">: </tspan><tspan class="val">{escape(value)}</tspan>'
    info.append(f'<text class="info" x="{info_x:.0f}" y="{y}" style="animation-delay:{delay:.2f}s">{body}</text>')
    y += 24

palette = ["#3e1206", "#732a10", "#b23a0b", "#f76616", "#f9853c", "#fbad74", "#fbbf24", "#faf7f2"]
swatch_delay = 1.9 + len(INFO) * 0.13
swatches = "".join(
    f'<rect class="info" x="{info_x + i * 26:.0f}" y="{y - 4}" width="26" height="14" fill="{c}" style="animation-delay:{swatch_delay:.2f}s"/>'
    for i, c in enumerate(palette)
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="ASCII portrait of Balaraj R beside a terminal system panel listing role, focus, stack, work and education.">
<defs>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f76616" stop-opacity="0"/><stop offset="0.7" stop-color="#f76616" stop-opacity="0.05"/><stop offset="1" stop-color="#fbbf24" stop-opacity="0.16"/></linearGradient>
<clipPath id="art"><rect x="{LEFT}" y="{TOP}" width="{COLS * CELL_W:.0f}" height="{ROWS * CELL_H}"/></clipPath>
</defs>
<style>
text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", "Courier New", monospace; white-space: pre; }}
.row {{ font-size: 7px; opacity: 0; animation: rise 0.25s ease-out forwards; }}
.w {{ fill: #fff3e0; }} .a {{ fill: #fbad45; }} .b {{ fill: #f76616; }} .c {{ fill: #8e300e; }}
.info {{ font-size: 15px; opacity: 0; animation: rise 0.2s ease-out forwards; }}
.key {{ fill: #f76616; font-weight: 700; }} .sep {{ fill: #78716c; }} .val {{ fill: #e7e5e4; }} .dim {{ fill: #44403c; }}
.ghost {{ font-size: 7px; }}
.noise {{ font-size: 7px; fill: #fbad45; }}
.split {{ opacity: 0; mix-blend-mode: screen; animation: split 6s steps(1) 3.4s infinite; }}
.cyan text {{ fill: #22d3ee; }} .red text {{ fill: #f43f5e; }}
.red {{ animation-name: split-b; }}
.flicker {{ animation: flicker 6s steps(1) 3.4s infinite; }}
.band {{ animation: tear 6s steps(1) 3.4s infinite; }}
.b0 {{ animation: none; }} .b2 {{ animation-name: tear-b; }} .b3 {{ animation-name: tear-c; }} .b4 {{ animation-name: tear-d; }}
.scramble {{ opacity: 0; animation: scramble 6s steps(1) 3.4s infinite; }}
.s1 {{ animation-delay: 3.46s; }} .s2 {{ animation-delay: 3.52s; }}
.beam {{ animation: beam 5.5s linear 2.4s infinite; opacity: 0; }}
@keyframes rise {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes tear {{ 0%, 9%, 100% {{ transform: translateX(0); }} 1% {{ transform: translateX(16px); }} 3% {{ transform: translateX(-11px); }} 5% {{ transform: translateX(5px); }} 7% {{ transform: translateX(-3px); }} }}
@keyframes tear-b {{ 0%, 9%, 100% {{ transform: translateX(0); }} 1% {{ transform: translateX(-20px); }} 3% {{ transform: translateX(13px); }} 6% {{ transform: translateX(-6px); }} }}
@keyframes tear-c {{ 0%, 8%, 100% {{ transform: translateX(0); }} 2% {{ transform: translateX(10px); }} 4% {{ transform: translateX(-17px); }} 6% {{ transform: translateX(7px); }} }}
@keyframes tear-d {{ 0%, 9%, 100% {{ transform: translateX(0); }} 1% {{ transform: translateX(-9px); }} 4% {{ transform: translateX(22px); }} 7% {{ transform: translateX(-4px); }} }}
@keyframes split {{ 0%, 9%, 100% {{ opacity: 0; transform: translateX(0); }} 1% {{ opacity: 0.85; transform: translateX(-5px); }} 4% {{ opacity: 0.7; transform: translateX(-9px); }} 7% {{ opacity: 0.55; transform: translateX(-3px); }} }}
@keyframes split-b {{ 0%, 9%, 100% {{ opacity: 0; transform: translateX(0); }} 1% {{ opacity: 0.85; transform: translateX(5px); }} 4% {{ opacity: 0.7; transform: translateX(9px); }} 7% {{ opacity: 0.55; transform: translateX(3px); }} }}
@keyframes flicker {{ 0%, 10%, 100% {{ opacity: 1; }} 1% {{ opacity: 0.55; }} 2% {{ opacity: 1; }} 4% {{ opacity: 0.7; }} 5% {{ opacity: 1; }} 8% {{ opacity: 0.8; }} }}
@keyframes scramble {{ 0%, 9%, 100% {{ opacity: 0; }} 1% {{ opacity: 1; }} 3% {{ opacity: 0; }} 4% {{ opacity: 1; }} 7% {{ opacity: 0; }} }}
@keyframes beam {{ 0% {{ opacity: 1; transform: translateY(-90px); }} 100% {{ opacity: 1; transform: translateY({ROWS * CELL_H}px); }} }}
@media (prefers-reduced-motion: reduce) {{ .row, .info {{ opacity: 1; animation: none; }} .flicker, .band {{ animation: none; }} .beam, .split, .scramble {{ display: none; }} }}
</style>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="#0c0a09" stroke="#292524"/>
{art}
<g clip-path="url(#art)"><rect class="beam" x="{LEFT}" y="{TOP}" width="{COLS * CELL_W:.0f}" height="90" fill="url(#beam)"/></g>
{"".join(info)}
{swatches}
</svg>
"""
with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write(svg)
print(len(svg) // 1024, "KB")
