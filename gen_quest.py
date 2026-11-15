#!/usr/bin/env python3
"""BUG QUEST — two pixel-art platformer strips for the top and bottom of the README.
Stage 1 (top): the dev runs in, fixes two bugs, and runs off the right edge.
Stage 2 (bottom): the dev runs in from the left, spawns agents in the sky that destroy
both performance issues at once, and ships.
Both SVGs share one loop of T seconds, so the hero leaves the top strip as he enters
the bottom one, provided the browser loads both images at about the same time.
Pure SVG + CSS keyframes with the font embedded, so it animates in a README <img>.
Usage: gen_quest.py   (writes assets/quest-top.svg and assets/quest-bottom.svg)"""
import base64, os

BASE = os.path.dirname(os.path.abspath(__file__))
T = 20.0                                  # one full loop: stage 1 is 0-9s, stage 2 is 9-20s
W, H, PX, GROUND = 1200, 240, 4, 190      # PX = size of one sprite pixel; GROUND = y of the floor

# sweetie-16, same palette as the character sheet
NIGHT, PURPLE, RED, ORANGE, YELLOW, LIME, GREEN = "#1a1c2c", "#5d275d", "#b13e53", "#ef7d57", "#ffcd75", "#a7f070", "#38b764"
NAVY, BLUE, SKYBLUE, CYAN, WHITE, DIM, SLATE, SLOT = "#29366f", "#3b5dc9", "#41a6f6", "#73eff7", "#f4f4f4", "#94b0c2", "#566c86", "#333c57"

HERO_TOP = ["....HHHH....", "...HHHHHH...", "...HSSSSH...", "...SGDSGD...", "...SSSSSS...", "....SSSS....",
            "...RRRRRR...", "..RRRRRRRR..", "..RRRRCCRR..", "..SRRRRRRS..", "...RRRRRR...", "...BBBBBB..."]
HERO_A = HERO_TOP + ["...BB..BB...", "...BB..BB...", "...KK..KKK.."]      # stride
HERO_B = HERO_TOP + ["....BBBB....", "....BBBB....", "....KKKK...."]      # legs together
HERO_C = {"H": NIGHT, "S": "#e8b796", "G": WHITE, "D": NIGHT, "R": RED, "C": CYAN, "B": BLUE, "K": WHITE}
BUG_A = ["..N......N..", "...RRRRRR...", ".RRRRRRRRRR.", "RRWDRRRRRRRR", "RRRRRRRRRRRR", ".RRRRRRRRRR.", "..N..N..N..."]
BUG_B = BUG_A[:-1] + ["...N..N..N.."]
BUG_C = {"N": NIGHT, "R": RED, "W": WHITE, "D": NIGHT}
SNAIL = ["......OOOO....", ".....OOOOOO...", "....OOPPOOOO..", ".Y..OPOOPOOO..", "YWY.OOPPOOOO..", "YDY.OOOOOOOO..",
         "YYYYYYYYYYYYY.", ".YYYYYYYYYYYYY"]
SNAIL_C = {"O": ORANGE, "P": PURPLE, "Y": YELLOW, "W": WHITE, "D": NIGHT}
LEAK = ["....BB....", "...BBBB...", "..BBBBBB..", ".BBWBBWBB.", ".BBDBBDBB.", "BBBBBBBBBB", "BBBBBBBBBB", ".BBBBBBBB."]
LEAK_C = {"B": SKYBLUE, "W": WHITE, "D": NIGHT}
TOOL = [".X.X.", "XXXXX", ".X.X.", "XXXXX", ".X.X."]
AGENT = [".....A.....", ".....A.....", "..WWWWWWW..", ".WWCWWWCWW.", ".WWWWWWWWW.", "LLWWDDDWWLL", "..WWWWWWW.."]
AGENT_C = {"A": YELLOW, "W": WHITE, "C": CYAN, "D": NIGHT, "L": DIM}

def sprite(rows, colours, x=0, y=0, px=PX):
    out = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            e = i
            while e < len(row) and row[e] == row[i]:
                e += 1
            if row[i] in colours:
                out.append(f'<rect x="{x + i * px}" y="{y + j * px}" width="{(e - i) * px}" height="{px}" fill="{colours[row[i]]}"/>')
            i = e
    return "".join(out)

def kf(name, pts):
    """Keyframes on the master loop from (seconds, css) points."""
    return f"@keyframes {name}{{" + "".join(f"{t / T * 100:.2f}%{{{css}}}" for t, css in pts) + "}"

def shown(name, spans):
    """Keyframes that make something visible only inside the given (start, end) spans."""
    pts, e = [(0, "opacity:0")], 0.02
    for a, b in spans:
        pts += [(max(0, a - e), "opacity:0"), (a, "opacity:1"), (b, "opacity:1"), (min(T, b + e), "opacity:0")]
    return kf(name, pts + [(T, "opacity:0")])

def on(cls, name, timing="linear"):
    return f".{cls}{{animation:{name} {T}s {timing} infinite}}"

def tx(x, extra=""):
    return f"transform:translateX({x}px){extra}"

def label(x, y, s, size=9, fill=WHITE, cls="", anchor="middle"):
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{s}</text>'

def frames(a, b, colours, x, y):
    """Two-frame walk cycle."""
    return f'<g class="fa">{sprite(a, colours, x, y)}</g><g class="fb">{sprite(b, colours, x, y)}</g>'

FONT = base64.b64encode(open(f"{BASE}/assets/fonts/press-start-2p.woff2", "rb").read()).decode()
BASE_CSS = (f"@font-face{{font-family:D;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
            "text{font-family:D,monospace}"
            "@keyframes fa{0%{opacity:1}50%{opacity:0}}@keyframes fb{0%{opacity:0}50%{opacity:1}}"
            ".fa{animation:fa .3s step-end infinite}.fb{animation:fb .3s step-end infinite}"
            "@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
            ".bob{animation:bob .8s step-end infinite}"
            "@keyframes spin{to{transform:rotate(360deg)}}"
            ".spin{animation:spin .35s linear infinite;transform-box:fill-box;transform-origin:center}"
            "@keyframes twinkle{0%{opacity:1}50%{opacity:.25}}"
            ".squash{transform-box:fill-box;transform-origin:bottom}"
            ".mid{transform-box:fill-box;transform-origin:center}"
            "@keyframes pulse{0%{transform:scale(.8)}50%{transform:scale(1.25)}}"
            ".pulse{animation:pulse .3s step-end infinite;transform-box:fill-box;transform-origin:center}")
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}.hx{transform:translateX(560px)}}"

def backdrop(seed):
    out = [f'<rect x="5" y="5" width="{W - 10}" height="{H - 10}" fill="{NAVY}"/>']
    for i in range(26):                                             # stars
        x, y = 30 + (i * 173 + seed * 61) % (W - 60), 40 + (i * 37 + seed * 17) % 90
        out.append(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{WHITE}" style="animation:twinkle {1.4 + i % 5 * .5}s step-end infinite"/>')
    x, i = 5, seed
    while x < W - 5:                                                # the neighbourhood
        w, h = 60 + (i * 37) % 70, 30 + (i * 53) % 70
        out.append(f'<rect x="{x}" y="{GROUND - h}" width="{w}" height="{h}" fill="{NIGHT if i % 2 else SLOT}"/>')
        for wy in range(GROUND - h + 10, GROUND - 14, 20):
            for wx in range(x + 10, x + w - 12, 20):
                if (wx + wy * 3 + i) % 3 == 0:
                    out.append(f'<rect x="{wx}" y="{wy}" width="8" height="8" fill="{YELLOW}"/>')
        x, i = x + w, i + 1
    out.append(f'<rect x="5" y="{GROUND}" width="{W - 10}" height="8" fill="{GREEN}"/>'
               f'<rect x="5" y="{GROUND + 8}" width="{W - 10}" height="{H - GROUND - 13}" fill="{PURPLE}"/>')
    for i in range(40):                                             # dirt speckles
        out.append(f'<rect x="{20 + (i * 97 + seed * 13) % (W - 40)}" y="{GROUND + 14 + (i * 7) % 20}" width="8" height="4" fill="{NIGHT}" opacity=".45"/>')
    return "".join(out)

def hero():
    """Hero drawn with his feet on the floor at x=0; .hx moves him along, .hy makes him jump."""
    return f'<g class="hx"><g class="hy">{frames(HERO_A, HERO_B, HERO_C, 0, GROUND - 15 * PX)}%s</g></g>'

def enemy(cls, body, x, w, tag):
    """An enemy standing at x with a name tag; cls carries its defeat animation."""
    return f'<g class="{cls} squash"><g class="bob">{body}{label(x + w / 2, GROUND - 52, tag, 8, DIM)}</g></g>'

def popup(cls, x, s, fill=LIME):
    return label(x, GROUND - 60, s, 10, fill, cls)

def rise(name, t):
    return kf(name, [(0, "opacity:0;transform:translateY(0)"), (t - .02, "opacity:0;transform:translateY(0)"), (t, "opacity:1;transform:translateY(0)"),
                     (t + 1.0, "opacity:1;transform:translateY(-34px)"), (t + 1.3, "opacity:0;transform:translateY(-40px)"),
                     (T, "opacity:0;transform:translateY(0)")])

def defeat(name, t, how):
    """Enemy is there until t, then squashes or pops, and comes back just before the loop restarts."""
    gone = {"squash": "transform:scaleY(.15)", "pop": "transform:scale(1.5)", "shrink": "transform:scale(.1)"}[how]
    return kf(name, [(0, "opacity:1;transform:none"), (t, "opacity:1;transform:none"), (t + .2, f"opacity:1;{gone}"), (t + .4, f"opacity:0;{gone}"),
                     (T - .6, "opacity:0;transform:none"), (T - .2, "opacity:1;transform:none"), (T, "opacity:1;transform:none")])

def svg(css, body, alt):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{alt}" shape-rendering="crispEdges">'
            f'<style>{BASE_CSS}{css}{REDUCED}</style>'
            f'<clipPath id="in"><rect x="5" y="5" width="{W - 10}" height="{H - 10}"/></clipPath>'
            f'<g clip-path="url(#in)">{body}</g>'
            f'<rect x="2.5" y="2.5" width="{W - 5}" height="{H - 5}" fill="none" stroke="{WHITE}" stroke-width="5"/></svg>\n')

def counter(prefix, spans, x=W - 30):
    """HUD value that changes over the loop: spans is [(text, [(start, end), ...]), ...]."""
    css = "".join(shown(f"{prefix}{i}", s) + on(f"{prefix}{i}", f"{prefix}{i}") for i, (_, s) in enumerate(spans))
    return css, "".join(label(x, 36, t, 11, WHITE, f"{prefix}{i}", "end") for i, (t, _) in enumerate(spans))

# ---- stage 1: bugs -------------------------------------------------------------------
B1, B2 = 470, 780                                                   # where the two bugs stand
css = "".join([
    kf("hx", [(0, tx(-60)), (2.4, tx(330)), (3.2, tx(330)), (5.3, tx(700)), (5.95, tx(B2)), (6.2, tx(B2)), (8.8, tx(1240)), (T, tx(1240))]), on("hx", "hx"),
    kf("hy", [(0, "transform:translateY(0)"), (5.3, "transform:translateY(0);animation-timing-function:cubic-bezier(.2,.8,.4,1)"),
              (5.65, "transform:translateY(-76px);animation-timing-function:cubic-bezier(.6,0,.9,.4)"),
              (5.95, "transform:translateY(-22px)"), (6.2, "transform:translateY(0)"), (T, "transform:translateY(0)")]), on("hy", "hy"),
    kf("tool", [(0, "opacity:0;" + tx(378)[:-0]), (2.48, "opacity:0;transform:translateX(378px)"), (2.5, "opacity:1;transform:translateX(378px)"),
                (3.0, f"opacity:1;transform:translateX({B1}px)"), (3.02, f"opacity:0;transform:translateX({B1}px)"), (T, "opacity:0;transform:translateX(378px)")]), on("tool", "tool"),
    defeat("b1", 3.0, "pop"), on("b1", "b1"), defeat("b2", 5.95, "squash"), on("b2", "b2"),
    rise("p1", 3.0), on("p1", "p1", "ease-out"), rise("p2", 5.95), on("p2", "p2", "ease-out"),
    shown("s1", [(2.4, 3.3)]), on("s1", "s1"), shown("s2", [(5.3, 6.4)]), on("s2", "s2"),
])
c_css, c_svg = counter("c", [("FIXED 0/2", [(0, 3.0), (T - .4, T)]), ("FIXED 1/2", [(3.0, 5.95)]), ("FIXED 2/2", [(5.95, T - .4)])])
says = label(24, GROUND - 74, "DEBUGGER!", 9, YELLOW, "s1") + label(24, GROUND - 74, "TESTS!", 9, YELLOW, "s2")
body = "".join([
    backdrop(3), label(30, 36, "STAGE 1  BUGS", 11, YELLOW, anchor="start"), c_svg,
    enemy("b1", frames(BUG_A, BUG_B, BUG_C, B1, GROUND - 7 * PX), B1, 48, "BUG"),
    enemy("b2", frames(BUG_A, BUG_B, BUG_C, B2, GROUND - 7 * PX), B2, 48, "BUG"),
    popup("p1", B1 + 24, "+1 FIXED"), popup("p2", B2 + 24, "+1 FIXED"),
    f'<g class="tool"><g class="spin">{sprite(TOOL, {"X": YELLOW}, 0, GROUND - 40)}</g></g>',
    hero() % says,
])
open(f"{BASE}/assets/quest-top.svg", "w").write(svg(css + c_css, body, "Stage 1: a pixel-art developer runs in, fixes two bugs with a debugger and tests, and runs off to the right."))

# ---- stage 2: performance ------------------------------------------------------------
S1, L1, RACK = 470, 800, 1080                                        # snail, leak, server rack
STOP, CAST, FIRE, BOOM = 240, 10.6, 13.4, 13.9                       # where the hero stands; when he casts, agents fire, issues die
AGENTS = [(380, 70), (530, 46), (720, 46), (870, 70)]                # sky positions; first two take the snail, last two the leak
css = [
    kf("hx", [(0, "opacity:0;" + tx(-60)), (8.9, "opacity:0;" + tx(-60)), (9.0, "opacity:1;" + tx(-60)), (CAST, "opacity:1;" + tx(STOP)), (14.6, "opacity:1;" + tx(STOP)),
              (17.0, "opacity:1;" + tx(990)), (19.4, "opacity:1;" + tx(990)), (19.8, "opacity:0;" + tx(990)), (T, "opacity:0;" + tx(990))]), on("hx", "hx"),
    kf("hy", [(0, "transform:translateY(0)"), (17.4, "transform:translateY(0)"), (17.7, "transform:translateY(-40px)"), (18.0, "transform:translateY(0)"),
              (18.3, "transform:translateY(-40px)"), (18.6, "transform:translateY(0)"), (T, "transform:translateY(0)")]), on("hy", "hy", "ease-out"),
    shown("aura", [(CAST, 11.8)]), on("aura", "aura"),
    shown("s1", [(CAST, BOOM)]), on("s1", "s1"),
    shown("online", [(12.4, 14.3)]), on("online", "online"),
    shown("beam", [(FIRE, FIRE + .12), (FIRE + .2, FIRE + .32), (FIRE + .38, BOOM)]), on("beam", "beam"),
    kf("flash", [(0, "opacity:0"), (11.55, "opacity:0"), (11.6, "opacity:.55"), (11.85, "opacity:0"), (BOOM - .03, "opacity:0"), (BOOM, "opacity:.75"), (BOOM + .3, "opacity:0"), (T, "opacity:0")]), on("flash", "flash"),
    kf("shake", [(0, "transform:none"), (BOOM, "transform:none"), (BOOM + .06, "transform:translate(7px,-4px)"), (BOOM + .12, "transform:translate(-7px,4px)"),
                 (BOOM + .18, "transform:translate(5px,3px)"), (BOOM + .24, "transform:translate(-3px,-2px)"), (BOOM + .32, "transform:none"), (T, "transform:none")]), on("shake", "shake", "step-end"),
    defeat("e1", BOOM, "pop"), on("e1", "e1"), defeat("e2", BOOM, "pop"), on("e2", "e2"),
    rise("p1", BOOM), on("p1", "p1", "ease-out"), rise("p2", BOOM), on("p2", "p2", "ease-out"),
    shown("ok", [(17.2, 19.4)]), on("ok", "ok"), shown("bad", [(0, 17.2), (19.4, T)]), on("bad", "bad"),
]
sky = []
for i, (ax, ay) in enumerate(AGENTS):
    ts = 11.6 + i * .18                                              # staggered spawn
    css += [kf(f"a{i}", [(0, "opacity:0;transform:scale(0)"), (ts, "opacity:0;transform:scale(0)"), (ts + .15, "opacity:1;transform:scale(1.35)"), (ts + .3, "opacity:1;transform:scale(1)"),
                         (14.3, "opacity:1;transform:scale(1)"), (14.6, "opacity:0;transform:translateY(-50px)"), (T, "opacity:0;transform:scale(0)")]), on(f"a{i}", f"a{i}"),
            kf(f"w{i}", [(0, "opacity:0;transform:scale(.2)"), (ts - .02, "opacity:0;transform:scale(.2)"), (ts, "opacity:1;transform:scale(.2)"), (ts + .35, "opacity:0;transform:scale(2.2)"), (T, "opacity:0;transform:scale(.2)")]), on(f"w{i}", f"w{i}", "ease-out")]
    tx_, ty_ = (S1 + 28, GROUND - 16) if i < 2 else (L1 + 20, GROUND - 16)
    sky.append(f'<line class="beam" x1="{ax + 22}" y1="{ay + 30}" x2="{tx_}" y2="{ty_}" stroke="{CYAN}" stroke-width="4"/>'
               f'<rect class="w{i} mid" x="{ax - 6}" y="{ay - 12}" width="56" height="56" fill="none" stroke="{WHITE}" stroke-width="6"/>'
               f'<g class="a{i} mid"><g class="bob">{sprite(AGENT, AGENT_C, ax, ay)}'
               f'<rect class="fa" x="{ax + 12}" y="{ay + 28}" width="4" height="8" fill="{ORANGE}"/><rect class="fa" x="{ax + 28}" y="{ay + 28}" width="4" height="8" fill="{ORANGE}"/>'
               f'<rect class="fb" x="{ax + 12}" y="{ay + 28}" width="4" height="4" fill="{YELLOW}"/><rect class="fb" x="{ax + 28}" y="{ay + 28}" width="4" height="4" fill="{YELLOW}"/></g></g>')
boom = ""
for j, (bx, col, delay) in enumerate([(S1 + 28, YELLOW, 0), (S1 + 28, ORANGE, .12), (L1 + 20, YELLOW, 0), (L1 + 20, ORANGE, .12)]):
    t = BOOM + delay
    css += [kf(f"x{j}", [(0, "opacity:0;transform:scale(.2)"), (t - .02, "opacity:0;transform:scale(.2)"), (t, "opacity:1;transform:scale(.3)"), (t + .45, "opacity:0;transform:scale(2.4)"), (T, "opacity:0;transform:scale(.2)")]), on(f"x{j}", f"x{j}", "ease-out")]
    boom += f'<rect class="x{j} mid" x="{bx - 24}" y="{GROUND - 44}" width="48" height="48" fill="none" stroke="{col}" stroke-width="8"/>'
c_css, c_svg = counter("c", [("ISSUES 2", [(0, BOOM), (T - .4, T)]), ("ISSUES 0", [(BOOM, T - .4)])])
says = (label(24, GROUND - 74, "SPAWN AGENTS!", 9, YELLOW, "s1")
        + f'<g class="aura"><rect class="pulse" x="-10" y="{GROUND - 70}" width="68" height="76" fill="none" stroke="{LIME}" stroke-width="4"/></g>')
rack = "".join([f'<rect x="{RACK}" y="{GROUND - 88}" width="64" height="88" fill="{SLOT}"/><rect x="{RACK + 4}" y="{GROUND - 84}" width="56" height="80" fill="{NIGHT}"/>']
               + [f'<rect x="{RACK + 10}" y="{GROUND - 76 + i * 18}" width="32" height="8" fill="{SLATE}"/>'
                  f'<rect class="bad" x="{RACK + 46}" y="{GROUND - 76 + i * 18}" width="8" height="8" fill="{RED}"/>'
                  f'<rect class="ok" x="{RACK + 46}" y="{GROUND - 76 + i * 18}" width="8" height="8" fill="{LIME}"/>' for i in range(4)]
               + [label(RACK + 32, GROUND - 100, "PROD", 8, DIM), label(RACK + 32, GROUND - 118, "SHIPPED!", 11, LIME, "ok")])
body = "".join([
    '<g class="shake">', backdrop(8), rack,
    enemy("e1", sprite(SNAIL, SNAIL_C, S1, GROUND - 8 * PX), S1, 56, "LATENCY"),
    enemy("e2", sprite(LEAK, LEAK_C, L1, GROUND - 8 * PX), L1, 40, "MEM LEAK"),
    "".join(sky), boom,
    popup("p1", S1 + 28, "-200 MS"), popup("p2", L1 + 20, "LEAK PLUGGED"),
    hero() % says, '</g>',
    label(30, 36, "STAGE 2  PERFORMANCE", 11, YELLOW, anchor="start"), c_svg,
    label(W / 2, 36, "AGENTS ONLINE x4", 11, CYAN, "online"),
    f'<rect class="flash" x="5" y="5" width="{W - 10}" height="{H - 10}" fill="{WHITE}"/>',
])
open(f"{BASE}/assets/quest-bottom.svg", "w").write(svg("".join(css) + c_css, body, "Stage 2: the developer runs in from the left and spawns four agents in the sky; they destroy a latency snail and a memory leak at once, and he ships to prod."))
print("wrote assets/quest-top.svg and assets/quest-bottom.svg")
