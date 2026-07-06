#!/usr/bin/env python3
"""PATHFINDER ARENA — one looping SVG cycling BFS → DFS → Dijkstra → A* over the
GitHub contribution heatmap, then a scoreboard. Commit days are walls; the scout
runs from the year's first day to today. `--invert` flips physics: commit days
are the path, idle days the void (gaps bridged minimally, shown as a causeway).
Pure SVG+SMIL on one master period T, so the whole scene loops in a README <img>.
Usage: gen_arena.py [--invert]   (reads gh_data.json next to this script)"""
import json, os, sys, datetime, heapq
from collections import deque

BASE = os.path.dirname(os.path.abspath(__file__))
INVERT = "--invert" in sys.argv
OUT = "arena_inverted.svg" if INVERT else "arena.svg"

# ---- layout / palette ----------------------------------------------------------
W, H = 1350, 264
X0, Y0, CELL, GAP = 50, 64, 20, 4
PITCH = CELL + GAP
INK, MUTED, BORDER, CARD, GHOST = "#e6edf3", "#8b949e", "#21262d", "#0d1117", "#161b22"
GREENS = ["#0e4429", "#006d32", "#26a641", "#39d353"]
BLUE, GOLD, GREEN = "#58a6ff", "#ffd33d", "#3fb950"
HEAD, RECENT, SETTLE = "#e6f6ff", "#79c0ff", "#1d4f94"   # scan comet: head → settled
BRIDGE = "#2d333b"
WALL_FLASH = "#39424e" if INVERT else "#7ee787"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# ---- grid ------------------------------------------------------------------------
d = json.load(open(f"{BASE}/gh_data.json"))["data"]["user"]
weeks = d["contributionsCollection"]["contributionCalendar"]["weeks"]
TOTAL = d["contributionsCollection"]["contributionCalendar"]["totalContributions"]
pos = {}
for c, w in enumerate(weeks):
    for day in w["contributionDays"]:
        pos[(c, day["weekday"])] = day["contributionCount"]
start = (0, weeks[0]["contributionDays"][0]["weekday"])
goal = (len(weeks) - 1, weeks[-1]["contributionDays"][-1]["weekday"])   # today
NBR = ((1, 0), (0, 1), (0, -1), (-1, 0))


def is_wall(n):
    return (n == 0) if INVERT else (n >= 1)


# carve the minimum blocks so a route exists (Dijkstra; walls ~1000, edge rows discouraged)
dd, par, hq = {start: 0}, {}, [(0, start)]
while hq:
    cd, p = heapq.heappop(hq)
    if cd > dd.get(p, 9e9): continue
    for dx, dy in NBR:
        q = (p[0] + dx, p[1] + dy)
        if q not in pos: continue
        w_ = 1000 if is_wall(pos[q]) and q not in (start, goal) else 1 + (5 if q[1] in (0, 6) else 0)
        if cd + w_ < dd.get(q, 9e9):
            dd[q] = cd + w_; par[q] = p
            heapq.heappush(hq, (cd + w_, q))
p, carved = goal, set()
while p != start:
    if is_wall(pos[p]) and p not in (start, goal):
        pos[p] = 2 if INVERT else 0; carved.add(p)
    p = par[p]

walls = {p for p, n in pos.items() if is_wall(n) and p not in (start, goal)}
free = lambda p: p in pos and p not in walls
hman = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])


# ---- searchers: each returns (visit order, parent map) -----------------------------
def bfs():
    parent, seen, order, q = {}, {start}, [], deque([start])
    while q:
        p = q.popleft(); order.append(p)
        if p == goal: break
        for dx, dy in NBR:
            n = (p[0] + dx, p[1] + dy)
            if free(n) and n not in seen:
                seen.add(n); parent[n] = p; q.append(n)
    return order, parent


def dfs():
    parent, seen, order, stack = {}, set(), [], [(start, None)]
    while stack:
        p, from_ = stack.pop()
        if p in seen: continue
        seen.add(p); order.append(p)
        if from_: parent[p] = from_
        if p == goal: break
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):     # DOWN pops first: serpentine
            n = (p[0] + dx, p[1] + dy)
            if free(n) and n not in seen:
                stack.append((n, p))
    return order, parent


def best_first(f):
    """Dijkstra (f=g) / A* (f=g+h) on the unit grid; ties toward deeper g."""
    parent, g, order, tick = {}, {start: 0}, [], 0
    seen, hq = set(), [(f(0, start), 0, 0, start)]
    while hq:
        _, _, _, p = heapq.heappop(hq)
        if p in seen: continue
        seen.add(p); order.append(p)
        if p == goal: break
        for dx, dy in NBR:
            n = (p[0] + dx, p[1] + dy)
            if free(n) and g[p] + 1 < g.get(n, 9e9):
                g[n] = g[p] + 1; parent[n] = p; tick += 1
                heapq.heappush(hq, (f(g[n], n), -g[n], tick, n))
    return order, parent


ALGOS = [("BFS", bfs), ("DFS", dfs),
         ("DIJKSTRA", lambda: best_first(lambda g, p: g)),
         ("A*", lambda: best_first(lambda g, p: g + hman(p)))]
runs = []
for name, fn in ALGOS:
    order, parent = fn()
    assert order[-1] == goal, f"{name} found no route"
    path, p = [], goal
    while p != start:
        path.append(p); p = parent[p]
    path.append(start); path.reverse()
    runs.append(dict(name=name, visited=order, path=path, steps=len(path) - 1))
    print(f"{name:9s} scanned {len(order):3d} · steps {len(path) - 1}")

# ---- master timeline: 4 phases + scoreboard ----------------------------------------
INTRO, PHASE, SCAN_D, RES_D = 1.2, 8.0, 4.0, 4.2
P0 = [INTRO + i * PHASE for i in range(4)]
PEND = [t + PHASE - 0.25 for t in P0]
TRES = INTRO + 4 * PHASE
T = TRES + RES_D + 0.2


def kf(pairs):
    """(seconds, value) pairs -> SMIL values/keyTimes spanning [0, T]."""
    pts = ([(0.0, pairs[0][1])] if pairs[0][0] > 0 else []) + list(pairs)
    if pts[-1][0] < T: pts.append((T, pts[-1][1]))
    last, ks, vs = -1.0, [], []
    for sec, v in pts:
        k = min(max(sec / T, 0.0), 1.0)
        if k <= last: k = min(last + 1e-4, 1.0)
        last = k
        ks.append(f"{k:.4f}"); vs.append(str(v))
    return ";".join(vs), ";".join(ks)


def anim(attr, pairs):
    v, k = kf(pairs)
    return f'<animate attributeName="{attr}" values="{v}" keyTimes="{k}" dur="{T:.2f}s" repeatCount="indefinite"/>'


def windows(spans, lo="0", hi="1"):
    """opacity keyframes: on during each (a, b) span, off elsewhere."""
    E, pairs, cur = 0.02, [(0.0, lo)], 0.0
    for a, b in spans:
        pairs += [(max(a - E, cur + 1e-3), lo), (a, hi), (b, hi), (b + E, lo)]
        cur = b + E
    return pairs


def cxy(p):
    return X0 + p[0] * PITCH + CELL / 2, Y0 + p[1] * PITCH + CELL / 2


rng = 913
def jit():
    global rng
    rng = (rng * 1103515245 + 12345) % (2 ** 31)
    return (rng % 40) / 1000.0


visits = {}                                    # cell -> [(t_visit, phase)]
for i, run in enumerate(runs):
    dt = SCAN_D / len(run["visited"])
    for j, p in enumerate(run["visited"]):
        visits.setdefault(p, []).append((P0[i] + 0.5 + j * dt + jit(), i))

# ---- scene --------------------------------------------------------------------------
S = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
  aria-label="Pathfinder arena: BFS, DFS, Dijkstra and A-star race across {TOTAL} contributions">
<defs>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="pathglow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
  <feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".5"/></pattern>
</defs>
<rect width="{W}" height="{H}" rx="10" fill="{CARD}" stroke="{BORDER}"/>
<text x="{X0}" y="36" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{INK}">PATHFINDER ARENA</text>''']

# HUD: phase name (center), live scan counter then result (right)
for i, run in enumerate(runs):
    S.append(f'<text x="{W / 2}" y="36" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{BLUE}" opacity="0">'
             f'{i + 1}/4 <tspan fill="{INK}" font-weight="700">{run["name"]}</tspan>'
             f'{anim("opacity", windows([(P0[i] + 0.1, PEND[i])]))}</text>')
    n = len(run["visited"])
    frames = [(P0[i] + 0.5 + j * (SCAN_D / n), j + 1) for j in range(0, n, max(1, n // 22))]
    for k_, (ts, val) in enumerate(frames):
        te = frames[k_ + 1][0] if k_ + 1 < len(frames) else P0[i] + 0.5 + SCAN_D
        S.append(f'<text x="{W - 36}" y="36" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}" opacity="0">'
                 f'SCAN <tspan fill="{BLUE}">{val:04d}</tspan>{anim("opacity", windows([(ts, te)]))}</text>')
    S.append(f'<text x="{W - 36}" y="36" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}" opacity="0">'
             f'SCAN {n} · STEPS <tspan fill="{GOLD}">{run["steps"]}</tspan>'
             f'{anim("opacity", windows([(P0[i] + 0.5 + SCAN_D + 0.1, PEND[i])]))}</text>')
S.append(f'<text x="{W / 2}" y="36" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{GOLD}" opacity="0">'
         f'RESULTS · SAME GRID, FOUR MINDS{anim("opacity", windows([(TRES + 0.2, T - 0.25)]))}</text>')

# weekday / month labels
for lbl, row in [("MON", 1), ("WED", 3), ("FRI", 5)]:
    S.append(f'<text x="{X0 - 8}" y="{Y0 + row * PITCH + 13}" text-anchor="end" font-family="{MONO}" font-size="8" fill="{MUTED}" opacity=".7">{lbl}</text>')
seen_m = None
for c, w in enumerate(weeks):
    m = datetime.date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b").upper()
    if m != seen_m:
        if seen_m is not None:
            S.append(f'<text x="{X0 + c * PITCH}" y="{Y0 + 7 * PITCH + 12}" font-family="{MONO}" font-size="8" fill="{MUTED}" opacity=".7">{m}</text>')
        seen_m = m


# terrain (true heatmap colors; walls flash when the scan touches them)
def cell_color(p, n):
    if p in carved and INVERT: return BRIDGE
    if n == 0: return GHOST
    return GREENS[3 if n >= 10 else 2 if n >= 5 else 1 if n >= 2 else 0]


contact = {}                                   # wall -> {phase: first touch time}
for p, vlist in visits.items():
    for dx, dy in NBR:
        q = (p[0] + dx, p[1] + dy)
        if q in walls:
            for tv, ph in vlist:
                cl = contact.setdefault(q, {})
                cl[ph] = min(cl.get(ph, 9e9), tv)
for (c, r), n in sorted(pos.items()):
    x, y = X0 + c * PITCH, Y0 + r * PITCH
    col = cell_color((c, r), n)
    fl = ""
    if (c, r) in contact:
        pairs = []
        for ph in sorted(contact[(c, r)]):
            tc = contact[(c, r)][ph]
            pairs += [(tc, col), (tc + 0.06, WALL_FLASH), (tc + 0.5, col)]
        fl = anim("fill", pairs)
    S.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{col}">{fl}</rect>')

# exploration comet: white head → bright blue → one settled blue, reset each phase
S.append("<g>")
for p, vlist in sorted(visits.items()):
    if p in (start, goal): continue
    x, y = X0 + p[0] * PITCH, Y0 + p[1] * PITCH
    spans, fill_pairs = [], []
    for tv, ph in vlist:
        dt = SCAN_D / len(runs[ph]["visited"])
        spans.append((tv, PEND[ph]))
        pe = PEND[ph] - 0.02
        for age, col in ((0, HEAD), (1.5, RECENT), (4, SETTLE)):
            fill_pairs.append((min(tv + age * dt, pe), col))
    S.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{HEAD}" opacity="0">'
             f'{anim("opacity", windows(spans, hi=".85"))}{anim("fill", fill_pairs)}</rect>')
S.append("</g>")

# start / goal markers
for p, col, lbl in [(start, GREEN, "DAY 1"), (goal, GOLD, "TODAY")]:
    cx, cy = cxy(p)
    ly = Y0 - 8 if p[1] <= 3 else Y0 + 7 * PITCH + 24
    S.append(f'''<rect x="{cx - 9:.0f}" y="{cy - 9:.0f}" width="18" height="18" rx="4" fill="{col}"/>
<circle cx="{cx:.0f}" cy="{cy:.0f}" r="10" fill="none" stroke="{col}" stroke-width="1.5">
  <animate attributeName="r" values="11;20;11" dur="1.8s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".9;0;.9" dur="1.8s" repeatCount="indefinite"/>
</circle>
<text x="{cx:.0f}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="9" letter-spacing="1" fill="{col}">{lbl}</text>''')

# per-phase route (full cell width) + runner + arrival ring
for i, run in enumerate(runs):
    tp, pd = P0[i] + 0.5 + SCAN_D + 0.3, 1.2
    tr, rd = tp + pd + 0.2, 1.1
    pts = " ".join(f"{cxy(q)[0]:.1f},{cxy(q)[1]:.1f}" for q in run["path"])
    S.append(f'''<polyline points="{pts}" fill="none" stroke="{GOLD}" stroke-width="{CELL}" stroke-linejoin="round" stroke-linecap="round"
  filter="url(#pathglow)" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0">
  {anim("stroke-dashoffset", [(tp, 1), (tp + pd, 0), (PEND[i], 0), (PEND[i] + 0.02, 1)])}
  {anim("opacity", windows([(tp, PEND[i])], hi=".95"))}</polyline>''')
    mp = f'M{pts.split()[0]} ' + " ".join("L" + s for s in pts.split()[1:])
    for lag, r_, op in ((0.0, 5, "1"), (0.09, 3, ".5")):
        v, k = kf([(tr + lag, 0), (tr + rd + lag, 1)])
        S.append(f'''<circle r="{r_}" fill="#fff" filter="url(#glow)" opacity="0">
  {anim("opacity", windows([(tr + lag, tr + rd + lag)], hi=op))}
  <animateMotion path="{mp}" keyPoints="{v}" keyTimes="{k}" calcMode="linear" dur="{T:.2f}s" repeatCount="indefinite"/>
</circle>''')
    gx, gy = cxy(goal)
    S.append(f'<circle cx="{gx:.0f}" cy="{gy:.0f}" r="4" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0">'
             f'{anim("opacity", windows([(tr + rd, tr + rd + 0.6)]))}{anim("r", [(tr + rd, 4), (tr + rd + 0.6, 20)])}</circle>')

# scoreboard
best_steps = min(r["steps"] for r in runs)
best_scan = min(len(r["visited"]) for r in runs)
S.append(f'<rect x="8" y="46" width="{W - 16}" height="{Y0 + 7 * PITCH - 30}" rx="8" fill="#010409" opacity="0">'
         f'{anim("opacity", [(0, 0), (TRES - 0.2, 0), (TRES, 0.78), (T - 0.3, 0.78), (T - 0.1, 0)])}</rect>')
cols = [(W / 2 - 140, "start"), (W / 2 + 90, "end"), (W / 2 + 210, "end")]
sb = [f'<g font-family="{MONO}" font-size="12" letter-spacing="1" opacity="0">{anim("opacity", windows([(TRES + 0.25, T - 0.3)]))}']
for ri, row in enumerate([None] + runs):
    yy = 90 + ri * 26
    vals = ["", "SCANNED", "STEPS"] if row is None else [row["name"], str(len(row["visited"])), str(row["steps"])]
    for ci, val in enumerate(vals):
        if not val: continue
        colr = MUTED if row is None else INK
        if row and ci == 1 and len(row["visited"]) == best_scan: colr = BLUE
        if row and ci == 2 and row["steps"] == best_steps: colr = GOLD
        wgt = ' font-weight="700"' if row and (ci == 0 or colr in (GOLD, BLUE)) else ""
        sb.append(f'<text x="{cols[ci][0]:.0f}" y="{yy}" text-anchor="{cols[ci][1]}"{wgt} fill="{colr}">{val}</text>')
sb.append(f'<text x="{W / 2}" y="{90 + 5 * 26 + 6}" text-anchor="middle" font-size="10" letter-spacing="2" fill="{MUTED}">'
          f'<tspan fill="{GOLD}">■</tspan> FEWEST STEPS   <tspan fill="{BLUE}">■</tspan> FEWEST CELLS SCANNED</text></g>')
S.append("".join(sb))

S.append(f'<rect width="{W}" height="{H}" rx="10" fill="url(#scan)" opacity=".12"/>')
S.append("</svg>")

svg = "\n".join(S)
open(f"{BASE}/{OUT}", "w").write(svg)
print(f"{OUT} → {len(svg) / 1024:.0f} KB · loop {T:.1f}s · carved {len(carved)}")
