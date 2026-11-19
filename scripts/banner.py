#!/usr/bin/env python3
"""Render assets/banner.gif for the profile README.

The light bulb critter from yoshimoriryu/nudge-lamp types `git push`, then
walks under each pipeline stage and lights it up until production goes green.
The sprite follows CritterRenderer.swift in that repo pixel for pixel.

Usage: python3 scripts/banner.py        (needs Pillow)
"""
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

SCALE = 4            # screen pixels per sprite pixel
W, H = 208, 56       # canvas in sprite pixels
FRAME_MS = 60
OUT = Path(__file__).resolve().parent.parent / "assets" / "banner.gif"


def rgb(h):
    return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


def mix(a, b, t):
    """Blend colour a toward b by fraction t."""
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


BG = (41, 41, 46)
PANEL = rgb(0x303137)
TRACK = rgb(0x3A3D44)
GROUND = rgb(0x45484F)
INK = rgb(0x1F2328)
METAL_LIGHT = rgb(0xC5CAD3)
METAL_DARK = rgb(0x8C929C)
CONTACT = rgb(0x5B6069)
FOOT = rgb(0x4A4F57)
WHITE = (255, 255, 255)
YELLOW = rgb(0xFFD60A)
GREEN = rgb(0x4ADE80)
MINT = rgb(0xA7F3C4)
AMBER = rgb(0xFCD34D)
PENDING_LINE = rgb(0x4A4F57)
PENDING_TEXT = rgb(0x8C929C)

GLASS = {
    "off": (rgb(0xC9CED6), rgb(0x8E949E)),
    "green": (rgb(0x4ADE80), rgb(0x15803D)),
    "mint": (rgb(0xA7F3C4), rgb(0x15803D)),
    "amber": (rgb(0xFCD34D), rgb(0xB45309)),
}

# 3x5 pixel font, only the glyphs the banner needs.
FONT = {
    ">": ["#..", ".#.", "..#", ".#.", "#.."],
    " ": ["...", "...", "...", "...", "..."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "G": [".##", "#..", "#.#", "#.#", ".##"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "N": ["#.#", "###", "###", "#.#", "#.#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "P": ["##.", "#.#", "##.", "#..", "#.."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
}


@dataclass
class Pose:
    dx: int = 0
    dy: int = 0
    eyes: tuple = ("open", 0, 0)   # ("open", dx, dy) | ("happy",)
    left_arm: str = "side"         # side | down | up | forward
    right_arm: str = "side"
    left_foot_up: bool = False
    right_foot_up: bool = False
    bulb: str = "green"
    glow: int = 0
    sparkle: object = None         # None | False (small) | True (big)


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), BG)
        self.d = ImageDraw.Draw(self.img)

    def px(self, x, y, w=1, h=1, c=WHITE):
        if w > 0 and h > 0:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)

    def text(self, s, x, y, c):
        for i, ch in enumerate(s):
            for row, line in enumerate(FONT[ch]):
                for col, bit in enumerate(line):
                    if bit == "#":
                        self.px(x + i * 4 + col, y + row, 1, 1, c)


def text_width(s):
    return len(s) * 4 - 1


# Critter ---------------------------------------------------------------------

LIFT = 3
SPRITE_ROWS = 14 + LIFT


def draw_critter(cv, p, sx, sy):
    """Draw the bulb with its sprite canvas (23 x 17) at sx, sy."""
    px = cv.px
    ox = sx + 4 + p.dx
    oy = sy + LIFT + max(p.dy, -LIFT)
    fill, rim = GLASS[p.bulb]

    if p.glow:
        light = mix(BG, fill, 0.55 if p.glow > 1 else 0.3)
        for x, y, w, h in [(3, -1, 4, 1), (1, 0, 2, 1), (7, 0, 2, 1), (0, 1, 1, 1),
                           (9, 1, 1, 1), (-1, 2, 1, 5), (10, 2, 1, 5), (0, 7, 1, 1),
                           (9, 7, 1, 1), (1, 8, 1, 1), (8, 8, 1, 1)]:
            px(ox + x, oy + y, w, h, light)

    px(ox + 3, oy, 4, 1, rim)
    px(ox + 1, oy + 1, 8, 1, rim)
    px(ox, oy + 2, 10, 5, rim)
    px(ox + 1, oy + 7, 8, 1, rim)
    px(ox + 2, oy + 8, 6, 1, rim)
    px(ox + 3, oy + 1, 4, 1, fill)
    px(ox + 1, oy + 2, 8, 5, fill)
    px(ox + 2, oy + 7, 6, 1, fill)
    px(ox + 3, oy + 8, 4, 1, fill)
    px(ox + 2, oy + 2, 1, 2, mix(fill, WHITE, 0.85))

    px(ox + 2, oy + 9, 6, 1, METAL_LIGHT)
    px(ox + 2, oy + 10, 6, 1, METAL_DARK)
    px(ox + 2, oy + 11, 6, 1, METAL_LIGHT)
    px(ox + 3, oy + 12, 4, 1, CONTACT)

    px(ox + 1, oy + (12 if p.left_foot_up else 13), 2, 1, FOOT)
    px(ox + 7, oy + (12 if p.right_foot_up else 13), 2, 1, FOOT)

    def arm(x, kind):
        rows = {"side": (4, 2), "down": (6, 2), "forward": (7, 2), "up": (1, 3)}[kind]
        px(x, oy + rows[0], 1, rows[1], METAL_DARK)

    arm(ox - 1, p.left_arm)
    arm(ox + 10, p.right_arm)

    lx, rx, ey = ox + 2, ox + 6, oy + 4
    if p.eyes[0] == "open":
        _, edx, edy = p.eyes
        px(lx + edx, ey + edy, 2, 2, INK)
        px(rx + edx, ey + edy, 2, 2, INK)
    elif p.eyes[0] == "happy":
        for x in (lx - 1, rx):
            px(x, ey + 1, 1, 1, INK)
            px(x + 1, ey, 1, 1, INK)
            px(x + 2, ey + 1, 1, 1, INK)

    if p.sparkle is not None:
        px(sx + 19, sy + 4, 3, 1, YELLOW)
        px(sx + 20, sy + 3, 1, 3, YELLOW)
        if p.sparkle:
            px(sx + 18, sy + 4, 5, 1, YELLOW)
            px(sx + 20, sy + 2, 1, 5, YELLOW)


def walk_pose(t):
    phase = (t // 2) % 4
    return Pose(
        dy=-1 if phase % 2 == 0 else 0,
        eyes=("open", 1, 0),
        left_arm="down" if phase == 2 else "side",
        right_arm="down" if phase == 0 else "side",
        left_foot_up=phase == 0,
        right_foot_up=phase == 2,
        glow=1,
    )


def work_pose(t):
    """Arms pump upward while the bulb beams power into the stage above."""
    phase = t % 4
    return Pose(
        eyes=("open", 0, -1),
        left_arm="up" if phase < 2 else "side",
        right_arm="side" if phase < 2 else "up",
        bulb="green" if (t // 2) % 2 == 0 else "mint",
        glow=2,
    )


def cheer_pose(t):
    cycle = t % 12
    return Pose(
        dy=[0, -1, -2, -1, 0][cycle] if cycle < 5 else 0,
        eyes=("happy",),
        left_arm="up",
        right_arm="up",
        left_foot_up=cycle in (1, 2, 3),
        right_foot_up=cycle in (1, 2, 3),
        bulb="amber",
        glow=2,
        sparkle=(t // 3) % 2 == 0,
    )


# Scene -----------------------------------------------------------------------

STAGES = ["BUILD", "TEST", "SCAN", "DEPLOY", "PROD"]
BOX_W, BOX_H, GAP, BOX_Y = 30, 14, 10, 17
BOX_X = [9 + i * (BOX_W + GAP) for i in range(len(STAGES))]
GROUND_Y = 52
CRITTER_Y = GROUND_Y - SPRITE_ROWS
COMMAND = "> GIT PUSH"
DONE_TEXT = "ALL GREEN"
BAR_W = 24


def stop_x(i):
    """Critter x that puts the glass right under stage i."""
    return BOX_X[i] + 6


@dataclass
class State:
    typed: int = 0
    cursor: bool = True
    status: list = None        # per stage: "wait" | "run" | "done"
    progress: list = None      # per stage: bar pixels filled
    wire: list = None          # per gap: pixels of the connector lit
    pods: int = 0
    pod_flash: int = -1
    done_typed: int = 0
    critter_x: float = -24
    pose: Pose = None
    beam: int = -1             # stage the bulb is powering, or -1
    t: int = 0

    def __post_init__(self):
        self.status = ["wait"] * len(STAGES)
        self.progress = [0] * len(STAGES)
        self.wire = [0] * (len(STAGES) - 1)


def draw_box(cv, i, st):
    x, y = BOX_X[i], BOX_Y
    status = st.status[i]
    line = {"wait": PENDING_LINE, "run": AMBER, "done": GREEN}[status]
    label = {"wait": PENDING_TEXT, "run": AMBER, "done": GREEN}[status]
    cv.px(x + 1, y + 1, BOX_W - 2, BOX_H - 2, PANEL)
    # Border with clipped corners for the 8-bit look.
    cv.px(x + 1, y, BOX_W - 2, 1, line)
    cv.px(x + 1, y + BOX_H - 1, BOX_W - 2, 1, line)
    cv.px(x, y + 1, 1, BOX_H - 2, line)
    cv.px(x + BOX_W - 1, y + 1, 1, BOX_H - 2, line)
    name = STAGES[i]
    cv.text(name, x + (BOX_W - text_width(name)) // 2, y + 3, label)

    if name == "PROD":
        for k in range(3):
            pxx = x + 3 + k * 9
            if k < st.pods:
                c = WHITE if k == st.pod_flash else GREEN
                cv.px(pxx, y + 9, 6, 3, c)
                cv.px(pxx, y + 9, 1, 1, mix(c, WHITE, 0.7))
            else:
                cv.px(pxx, y + 9, 6, 3, TRACK)
        return

    cv.px(x + 3, y + 9, BAR_W, 2, TRACK)
    fill = GREEN if status == "done" else AMBER
    cv.px(x + 3, y + 9, st.progress[i], 2, fill)


def draw_wire(cv, i, st):
    x0 = BOX_X[i] + BOX_W
    y = BOX_Y + BOX_H // 2
    lit = st.wire[i]
    for k in range(GAP):
        if k < lit:
            cv.px(x0 + k, y, 1, 1, GREEN)
        elif k % 2 == 0:
            cv.px(x0 + k, y, 1, 1, PENDING_LINE)
    if 0 < lit < GAP:
        cv.px(x0 + lit - 1, y - 1, 2, 3, WHITE)   # the packet travelling along


def render(st):
    cv = Canvas()

    # Terminal line, top left.
    cv.text(COMMAND[:1], 9, 5, GREEN)
    cv.text(COMMAND[1:st.typed] if st.typed > 1 else "", 13, 5, METAL_LIGHT)
    if st.cursor:
        cv.px(9 + st.typed * 4, 5, 3, 5, METAL_LIGHT)

    # Result line, top right.
    if st.done_typed:
        tx = W - 9 - text_width(DONE_TEXT)
        cv.text(DONE_TEXT[:st.done_typed], tx, 5, GREEN)

    for i in range(len(STAGES) - 1):
        draw_wire(cv, i, st)
    for i in range(len(STAGES)):
        draw_box(cv, i, st)

    # Ground, dashed like a scanline.
    for x in range(0, W, 3):
        cv.px(x, GROUND_Y, 2, 1, GROUND)

    # Power beam from the bulb up into the running stage.
    if st.beam >= 0:
        bx = BOX_X[st.beam] + 14
        top, bottom = BOX_Y + BOX_H, CRITTER_Y + LIFT - 2
        for y in range(top, bottom + 1):
            if (y + st.t) % 3 == 0:
                cv.px(bx, y, 2, 1, MINT)

    if st.pose is not None:
        draw_critter(cv, st.pose, round(st.critter_x), CRITTER_Y)
    return cv.img


def timeline():
    st = State()
    frames = []

    def snap(n=1):
        for _ in range(n):
            frames.append(render(st))
            st.t += 1

    # 1. Type the command, cursor blinking.
    for k in range(4):
        st.cursor = k % 2 == 0
        snap(2)
    for k in range(1, len(COMMAND) + 1):
        st.typed = k
        st.cursor = True
        snap()
    for k in range(4):
        st.cursor = k % 2 == 1
        snap(2)
    st.cursor = False

    def walk_to(target, wire=None):
        while st.critter_x < target:
            st.critter_x = min(target, st.critter_x + 2)
            st.pose = walk_pose(st.t)
            if wire is not None and st.wire[wire] < GAP:
                st.wire[wire] += 1
            snap()
        if wire is not None:
            st.wire[wire] = GAP

    # 2. Walk in, then power each stage in turn.
    walk_to(stop_x(0))
    for i in range(4):
        st.status[i] = "run"
        st.beam = i
        while st.progress[i] < BAR_W:
            st.progress[i] = min(BAR_W, st.progress[i] + 2)
            st.pose = work_pose(st.t)
            snap()
        st.status[i] = "done"
        st.beam = -1
        walk_to(stop_x(i + 1), wire=i)

    # 3. Production: pods come up one by one.
    st.status[4] = "run"
    st.beam = 4
    for k in range(3):
        for f in range(5):
            st.pose = work_pose(st.t)
            if f == 2:
                st.pods = k + 1
                st.pod_flash = k
            elif f == 3:
                st.pod_flash = -1
            snap()
    st.status[4] = "done"
    st.beam = -1

    # 4. Celebrate while the result types out.
    for k in range(30):
        st.pose = cheer_pose(k)
        if st.done_typed < len(DONE_TEXT):
            st.done_typed += 1
        snap()

    # 5. Stroll off stage, hold the green board, then loop.
    while st.critter_x < W + 2:
        st.critter_x += 2
        st.pose = walk_pose(st.t)
        snap()
    st.pose = None
    snap(14)
    return frames


def main():
    frames = timeline()
    colours = set()
    for f in frames:
        colours.update(c for _, c in f.getcolors(W * H))
    colours = sorted(colours)
    assert len(colours) <= 256, len(colours)

    pal = Image.new("P", (1, 1))
    flat = [v for c in colours for v in c]
    pal.putpalette(flat + [0] * (768 - len(flat)))

    out = []
    for f in frames:
        q = f.quantize(palette=pal, dither=Image.Dither.NONE)
        out.append(q.resize((W * SCALE, H * SCALE), Image.Resampling.NEAREST))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out[0].save(OUT, save_all=True, append_images=out[1:], duration=FRAME_MS,
                loop=0, optimize=False, disposal=1)
    print(f"{OUT}: {len(out)} frames, {len(colours)} colours, "
          f"{OUT.stat().st_size // 1024} KB, {len(out) * FRAME_MS / 1000:.1f} s")


if __name__ == "__main__":
    main()
