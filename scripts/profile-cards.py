"""Renders the animated Recognition, Certification and Connect graphics into assets/."""
import json
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICONS = json.load(open(os.path.join(HERE, "icons.json")))

FONT = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'

BASE_CSS = f"""
text {{ font-family: {FONT}; }}
.card {{ opacity: 0; animation: rise 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
.frame {{ fill: #141110; stroke: #292524; }}
.glow {{ fill: none; stroke: #f76616; opacity: 0.2; animation: glow 4s ease-in-out infinite; }}
.bar {{ fill: #f76616; transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: grow 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
.icon {{ fill: none; stroke: #f76616; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
.tag {{ fill: #fbad74; font-size: 10.5px; font-weight: 700; letter-spacing: 1.4px; }}
.title {{ fill: #faf7f2; font-weight: 700; }}
.sub {{ fill: #a8a29e; }}
.shine {{ fill: url(#sheen); transform: translateX(-140%); animation: sweep 6s ease-in-out infinite; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes grow {{ to {{ transform: scaleX(1); }} }}
@keyframes glow {{ 0%, 100% {{ opacity: 0.2; }} 50% {{ opacity: 0.8; }} }}
@keyframes sweep {{ 0%, 62% {{ transform: translateX(-140%); }} 100% {{ transform: translateX(140%); }} }}
@media (prefers-reduced-motion: reduce) {{ .card {{ opacity: 1; animation: none; }} .bar {{ transform: none; animation: none; }} .glow, .shine {{ animation: none; }} .shine {{ display: none; }} }}
"""

DEFS = """<defs><linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0.25"><stop offset="0.3" stop-color="#fbad74" stop-opacity="0"/><stop offset="0.5" stop-color="#fbad74" stop-opacity="0.13"/><stop offset="0.7" stop-color="#fbad74" stop-opacity="0"/></linearGradient>"""


def icon(name, x, y, size):
    return f'<g class="icon" transform="translate({x} {y}) scale({size / 24})">{ICONS[name]}</g>'


def card(index, x, y, w, h, body, delay, step=0.14):
    start = delay + index * step
    clip = f"clip{index}"
    return f"""<clipPath id="{clip}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>
<g class="card" style="animation-delay:{start:.2f}s">
<rect class="frame" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>
<rect class="glow" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" style="animation-delay:{index * 0.5:.1f}s"/>
<g clip-path="url(#{clip})"><rect class="bar" x="{x}" y="{y}" width="{w}" height="3" style="animation-delay:{start + 0.2:.2f}s"/>
{body}
<rect class="shine" x="{x}" y="{y}" width="{w}" height="{h}" style="animation-delay:{1.2 + index * 0.4:.1f}s"/></g>
</g>"""


def write(name, width, height, label, cards):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(label)}">
{DEFS}</defs><style>{BASE_CSS}</style>
{"".join(cards)}
</svg>
"""
    path = os.path.join(ROOT, "assets", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(svg)


RECOGNITION = [
    ("trophy", "NATIONAL WINNER", "Google Gen AI", "Exchange", "2025"),
    ("medal", "1ST PLACE", "Inferentia 2.0", "State hackathon", "2025"),
    ("flame", "GRAND FINALE", "Meta PyTorch", "OpenEnv Hackathon", "2026"),
    ("rocket", "FINALIST", "Google Gen AI", "Academy APAC", "2026"),
]
W, GAP, H = 206, 12, 176
cards = []
for i, (ico, tag, line1, line2, year) in enumerate(RECOGNITION):
    x = 1 + i * (W + GAP)
    body = (
        icon(ico, x + 18, 22, 30)
        + f'<text class="sub" x="{x + W - 18}" y="42" text-anchor="end" font-size="12">{year}</text>'
        + f'<text class="tag" x="{x + 18}" y="86">{tag}</text>'
        + f'<text class="title" x="{x + 18}" y="118" font-size="16">{escape(line1)}</text>'
        + f'<text class="title" x="{x + 18}" y="140" font-size="16">{escape(line2)}</text>'
    )
    cards.append(card(i, x, 1, W, H, body, 0.1))
write("recognition.svg", 862, 178, "National Winner at Google Gen AI Exchange 2025, 1st Place at Inferentia 2.0 2025, Grand Finale at Meta PyTorch OpenEnv 2026, Finalist at Google Gen AI Academy APAC 2026.", cards)

CERTIFICATIONS = [
    ("award", "ORACLE", "OCI Generative AI Professional", "Oracle Cloud Infrastructure"),
    ("cloud", "GOOGLE CLOUD", "Gen AI Academy APAC 2026", "Cohorts 1, 2 and 3 completed"),
    ("badge-check", "GOOGLE SKILLS", "35+ Verified Skill Badges", "Gold League"),
    ("code", "HACKERRANK", "Frontend Developer (React)", "Plus JavaScript (Intermediate)"),
]
W, GAP, H = 424, 12, 96
cards = []
for i, (ico, tag, title, sub) in enumerate(CERTIFICATIONS):
    x, y = 1 + (i % 2) * (W + GAP), 1 + (i // 2) * (H + GAP)
    body = (
        icon(ico, x + 20, y + 30, 34)
        + f'<text class="tag" x="{x + 74}" y="{y + 28}">{tag}</text>'
        + f'<text class="title" x="{x + 74}" y="{y + 52}" font-size="16">{escape(title)}</text>'
        + f'<text class="sub" x="{x + 74}" y="{y + 74}" font-size="13">{escape(sub)}</text>'
    )
    cards.append(card(i, x, y, W, H, body, 0.1))
write("certifications.svg", 862, 206, "OCI Generative AI Professional, Google Gen AI Academy APAC 2026, 35+ Google Skills badges in Gold League, HackerRank Frontend Developer and JavaScript.", cards)

CONNECT = [
    ("globe", "Portfolio", "balaraj.me"),
    ("mail", "Email", "balu.balarajr@gmail.com"),
    ("linkedin", "LinkedIn", "in/balarajr"),
    ("github", "GitHub", "balaraj74"),
    ("twitter", "X", "@Balaraj__r"),
    ("brain", "Hugging Face", "balarajr"),
    ("database", "Kaggle", "balarajr"),
    ("code", "Google Dev", "g.dev/balarajr"),
    ("instagram", "Instagram", "balaraj.__r"),
]
for i, (ico, title, handle) in enumerate(CONNECT):
    W, H = 278, 76
    body = (
        icon(ico, 18, 22, 32)
        + f'<text class="title" x="66" y="35" font-size="15">{escape(title)}</text>'
        + f'<text class="sub" x="66" y="56" font-size="12.5">{escape(handle)}</text>'
        + icon("arrow-up-right", W - 36, 28, 20)
    )
    tile = card(0, 1, 1, W, H, body, 0.1 + i * 0.1, 0).replace("animation-delay:0.0s", f"animation-delay:{i * 0.5:.1f}s").replace("animation-delay:1.2s", f"animation-delay:{1.2 + i * 0.45:.1f}s")
    write(f"connect/{title.lower().replace(' ', '-')}.svg", W + 2, H + 2, f"{title}: {handle}", [tile])
