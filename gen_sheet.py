#!/usr/bin/env python3
"""CHARACTER SHEET — the pixel-art profile card, rebuilt from GitHub data.
Stats are languages by bytes of code across non-fork repos; items are the
11 most recently pushed repos plus one empty slot. Fonts are embedded so the
SVG renders inside a README <img>. Layout mirrors the Pencil design in profile.pen.
Usage: gen_sheet.py   (reads repos.json next to this script, writes sheet.svg)"""
import base64, json, os, textwrap
from collections import Counter
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))

# ---- things to edit by hand --------------------------------------------------------
NAME, CLASS = "RANDHEER RAMESH K", "CLASS: YOUR FRIENDLY NEIGHBOURHOOD CODER"
RECIPE = ("Take 2 cups of Rust and a pinch of Zig. Fold into the network until the latency "
          "is too small to see. Add a handful of sandboxed agents and let them tell on the "
          "infrastructure, to keep it honest. Serve at 3 a.m.")
QUEST = "Ship clankr, so AI agents can be left running without a babysitter."
LINKS = [("GITHUB", "randheer-rk"), ("LINKEDIN", "in/randheerrrk"), ("X", "@randheerrrk")]
SKIP_REPOS = {"randheer-rk", "Randheerrrk", "ranskytech-contributions"}
SKIP_LANGS = {"HTML", "CSS", "Jupyter Notebook"}      # markup and notebook exports, not code
# repo -> (name on the sheet, one-liner). Anything not listed uses its GitHub description.
OVERRIDES = {
    "clankr": ("clankr", "An engine for AI agents you can leave running."),
    "gate": ("gate", "Lets the costly model plan and a cheap one type."),
    "mekey": ("mekey", "An Android keyboard with mechanical keycaps."),
    "loop": ("loop", "An Android music player, artwork first."),
    "randheer-portfolio": ("portfolio", "My own corner of the web."),
    "leetrooms": ("leetrooms", "LeetCode races with friends. No forged scores."),
    "blank": ("blank", "A peer-to-peer coding interview room."),
    "torchit": ("torchit", "Learn PyTorch by doing."),
    "tugboat": ("tugboat", "A Docker and Kubernetes learning lab."),
    "slidesjs": ("slidesjs", "Slide decks written as React components."),
    "borrowed": ("borrowed", "Learn Rust by doing."),
    "oxigraf": ("oxigraf", "LangGraph, but in Rust."),
}
JOKE_STATS = [("COFFEE", 10, "#f4f4f4"), ("SLEEP", 1, "#b13e53")]

# ---- palette (sweetie-16) / type ---------------------------------------------------
NIGHT, SLOT, EDGE, WHITE, DIM = "#1a1c2c", "#333c57", "#566c86", "#f4f4f4", "#94b0c2"
YELLOW, GREEN, CYAN, RED, BLUE = "#ffcd75", "#a7f070", "#73eff7", "#b13e53", "#3b5dc9"
BAR_COLOURS = [CYAN, "#ef7d57", BLUE, YELLOW, "#38b764", "#41a6f6"]
W, H, PAD, GAP = 1200, 960, 28, 22

# ---- data --------------------------------------------------------------------------
repos = json.load(open(f"{BASE}/repos.json"))["data"]["user"]["repositories"]["nodes"]
repos = [r for r in repos if r["name"] not in SKIP_REPOS]          # already newest-push first
langs = Counter()
for r in repos:
    for e in r["languages"]["edges"]:
        if e["node"]["name"] not in SKIP_LANGS:
            langs[e["node"]["name"]] += e["size"]
top = langs.most_common(6)
stats = [(n.upper(), max(1, round(10 * b / top[0][1])), BAR_COLOURS[i]) for i, (n, b) in enumerate(top)]
stats += JOKE_STATS
items = []
for r in repos[:11]:
    name, desc = OVERRIDES.get(r["name"], (r["name"], r["description"] or ""))
    items.append((name, (r["primaryLanguage"] or {}).get("name", "").upper(),
                  "LOCKED" if r["isPrivate"] else "OPEN", desc))
items.append(("? ? ?", "", "EMPTY", "Something is brewing."))

# ---- drawing helpers ---------------------------------------------------------------
out = []
def rect(x, y, w, h, fill, stroke=None, sw=0):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    i = sw / 2                                                     # keep the stroke inside
    out.append(f'<rect x="{x + i:.1f}" y="{y + i:.1f}" width="{w - sw:.1f}" height="{h - sw:.1f}" fill="{fill}"{s}/>')
def text(x, y, s, size, fill, cls="d", anchor="start"):
    out.append(f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')
def para(x, y, s, size, fill, chars, lead, max_lines=99):
    lines = textwrap.wrap(s, chars)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:chars - 1].rstrip(" .,") + "…"
    for i, l in enumerate(lines):
        text(x, y + i * lead, l, size, fill, "b")
    return y + len(lines) * lead
def panel(x, y, w, h):
    rect(x, y, w, h, NIGHT, WHITE, 5)
def sprite(x, y, rows, colours, px):
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            e = i
            while e < len(row) and row[e] == row[i]:
                e += 1
            if row[i] in colours:
                out.append(f'<rect x="{x + i * px}" y="{y + j * px}" width="{(e - i) * px}" height="{px}" fill="{colours[row[i]]}"/>')
            i = e

AVATAR = ["...HHHHHH...", "..HHHHHHHH..", "..HSSSSSSH..", "..SGGSSGGS..", "..SGDSSGDS..", "..SSSSSSSS..",
          "..SSSDDSSS..", "...SSSSSS...", ".OOOOOOOOOO.", "OOOOOWWOOOOO", "OOOOOOOOOOOO", "OOOOOOOOOOOO"]
HEART = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]

# ---- player panel ------------------------------------------------------------------
LX, LW = PAD, 300
panel(LX, PAD, LW, H - 2 * PAD)
ax = LX + (LW - 216) / 2
rect(ax, 56, 216, 216, BLUE)
sprite(ax + 12, 68, AVATAR, {"H": NIGHT, "S": "#e8b796", "G": WHITE, "D": NIGHT, "O": RED, "W": CYAN}, 16)
text(LX + LW / 2, 304, "LV 99 NIGHT OWL", 12, GREEN, anchor="middle")
text(LX + 72, 338, "HP", 12, WHITE)
for i in range(5):
    sprite(LX + 106 + i * 36, 322, HEART, {"X": RED if i < 4 else SLOT}, 4)
rect(LX + 22, 366, LW - 44, 4, SLOT)
text(LX + 22, 402, "FIND ME", 13, GREEN)
y = 428
for k, v in LINKS:
    text(LX + 22, y, k, 10, DIM)
    text(LX + 22, y + 24, v, 22, WHITE, "b")
    y += 52
rect(LX + 22, y - 6, LW - 44, 4, SLOT)
text(LX + 22, y + 30, "MAIN QUEST", 13, GREEN)
para(LX + 22, y + 60, QUEST, 20, WHITE, 24, 26)

# ---- identity ----------------------------------------------------------------------
RX = LX + LW + GAP
RW = W - PAD - RX
panel(RX, PAD, RW, 104)
text(RX + 22, PAD + 56, NAME, 34, YELLOW)
text(RX + 22, PAD + 84, CLASS, 14, CYAN)

# ---- stats -------------------------------------------------------------------------
MY, MH, SW = PAD + 104 + GAP, 306, 380
panel(RX, MY, SW, MH)
text(RX + 22, MY + 36, "STATS", 13, GREEN)
for i, (k, v, col) in enumerate(stats):
    y = MY + 62 + i * 25
    text(RX + 22, y, k[:12], 11, WHITE)
    for p in range(10):
        rect(RX + SW - 22 - (10 - p) * 16 + 3, y - 12, 13, 13, col if p < v else SLOT)
text(RX + 22, MY + MH - 26, "Languages by bytes of code in my repos.", 15, DIM, "b")

# ---- recipe ------------------------------------------------------------------------
CX, CW = RX + SW + GAP, RW - SW - GAP
panel(CX, MY, CW, MH)
text(CX + 22, MY + 38, "RECIPE: SYSTEMS & AI", 13, GREEN)
text(CX + 22, MY + 58, "ENGINEER", 13, GREEN)
para(CX + 22, MY + 94, RECIPE, 20, WHITE, 36, 27)

# ---- items -------------------------------------------------------------------------
IY = MY + MH + GAP
panel(RX, IY, RW, H - PAD - IY)
text(RX + 20, IY + 36, "ITEMS", 13, GREEN)
text(RX + RW - 20, IY + 34, "11 LATEST REPOS | OPEN = PUBLIC | LOCKED = NOT YET", 9, DIM, anchor="end")
SLOT_W = (RW - 40 - 36) / 4
for i, (name, lang, state, desc) in enumerate(items):
    x = RX + 20 + (i % 4) * (SLOT_W + 12)
    y = IY + 48 + (i // 4) * 132
    rect(x, y, SLOT_W, 120, SLOT, GREEN if state == "OPEN" else EDGE, 3)
    room = SLOT_W - 24 - len(state) * 8 - 8                       # px left of the state tag
    size = min(12, max(8, room // max(1, len(name))))
    if len(name) * size > room:
        name = name[:int(room // size) - 1] + "…"
    text(x + 12, y + 26, name, size, YELLOW)
    text(x + SLOT_W - 12, y + 24, state, 8, GREEN if state == "OPEN" else DIM, anchor="end")
    if lang:
        text(x + 12, y + 42, lang, 8, CYAN)
    para(x + 12, y + 64, desc, 16, WHITE, 19, 20, 3)

def font(path):
    return base64.b64encode(open(f"{BASE}/assets/fonts/{path}", "rb").read()).decode()
css = (f"@font-face{{font-family:D;src:url(data:font/woff2;base64,{font('press-start-2p.woff2')}) format('woff2')}}"
       f"@font-face{{font-family:B;src:url(data:font/woff2;base64,{font('pixelify-sans.woff2')}) format('woff2')}}"
       ".d{font-family:D,monospace}.b{font-family:B,sans-serif}")
alt = f"Character sheet for {NAME.title()}. {CLASS.title()}. Items: {', '.join(i[0] for i in items[:-1])}."
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'role="img" aria-label="{escape(alt)}" shape-rendering="crispEdges"><style>{css}</style>\n' + "\n".join(out) + "\n</svg>\n")
open(f"{BASE}/sheet.svg", "w").write(svg)
print(f"wrote sheet.svg ({len(svg)} bytes): {len(items) - 1} items, stats {[(k, v) for k, v, _ in stats]}")
