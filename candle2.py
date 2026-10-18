import math
import random
import tkinter as tk

# ------------------------------------------------------------
# ASCII CANDLE — animated character shading
# Run: python candle.py
# Close the window with Esc or the X button.
# Standard-library only; no caption, no terminal animation.
# ------------------------------------------------------------

COLS = 72
ROWS = 60
CELL_W = 9
CELL_H = 10
PAD_X = 14
PAD_Y = 14

WINDOW_W = COLS * CELL_W + 2 * PAD_X
WINDOW_H = ROWS * CELL_H + 2 * PAD_Y
BLACK = "#000000"

# Dark amber -> hot wax/flame highlights.
WAX_PALETTE = [
    "#100705", "#180906", "#220d07", "#2c1007",
    "#381407", "#471907", "#572008", "#69270a",
    "#7b2e0d", "#8e3710", "#a34214", "#b55019",
    "#c96320", "#d9782a", "#e78d37", "#f1a74c",
    "#f8c36d", "#ffdda0",
]
FLAME_PALETTE = [
    "#160704", "#280b04", "#401005", "#5c1806",
    "#782006", "#962908", "#b9360b", "#d84a0e",
    "#ef6412", "#ff8018", "#ff9c20", "#ffb632",
    "#ffd15c", "#ffe58a", "#fff2bc",
]
SPARK_PALETTE = ["#4c1908", "#762409", "#a8360c", "#d65a15", "#f9a33b"]

# Character ramps: low brightness uses light punctuation; high brightness
# uses denser glyphs. This gives the candle volume instead of a plain outline.
RAMP = "  ..,,:;irsXA253hMHGS#9B&@"
FLAME_RAMP = " .,:;irsxX2358#@$"

# Screen-space shape, row by row: narrow point, broad upper body, tapered base.
FLAME_WIDTHS = [0.20, 0.42, 0.78, 1.20, 1.70, 2.25, 2.72,
                3.05, 3.20, 3.08, 2.72, 2.05, 1.20]


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def noise(x, y, seed=0):
    """Deterministic fine texture, so the body doesn't jump randomly."""
    n = math.sin(x * 127.1 + y * 311.7 + seed * 74.7) * 43758.5453
    return (n - math.floor(n)) * 2.0 - 1.0


def glyph_for(value, ramp=RAMP):
    value = clamp(value)
    return ramp[min(len(ramp) - 1, int(value * (len(ramp) - 1) + 0.5))]


def color_for(value, palette):
    value = clamp(value)
    return palette[min(len(palette) - 1, int(value * (len(palette) - 1) + 0.5))]


def put(grid, colors, x, y, char, color):
    if 0 <= x < COLS and 0 <= y < ROWS:
        grid[y][x] = char
        colors[y][x] = color


def put_text(grid, colors, x, y, text, color):
    for i, ch in enumerate(text):
        put(grid, colors, x + i, y, ch, color)


def build_frame(frame_no):
    grid = [[" " for _ in range(COLS)] for _ in range(ROWS)]
    colors = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    # Slightly left of centre like the reference footage.
    cx = int(COLS * 0.44)
    flame_top = 10

    # 1) Organic flickering flame with a bright inner core.
    sway = (
        math.sin(frame_no * 0.18) * 0.62
        + math.sin(frame_no * 0.071 + 1.4) * 0.38
    )
    width_pulse = 1.0 + 0.055 * math.sin(frame_no * 0.27)
    flame_height = len(FLAME_WIDTHS)

    for row, base_width in enumerate(FLAME_WIDTHS):
        y = flame_top + row
        t = row / (flame_height - 1)
        centre = cx + sway * (0.20 + 0.80 * t)
        centre += math.sin(frame_no * 0.13 + t * 5.3) * 0.22
        half_width = base_width * width_pulse

        left = math.floor(centre - half_width - 0.5)
        right = math.ceil(centre + half_width + 0.5)

        for x in range(left, right + 1):
            dx = x - centre
            edge = half_width - abs(dx)
            if edge < -0.35:
                continue

            edge_light = clamp((edge + 0.35) / 1.05)
            core = clamp(1.0 - abs(dx) / max(half_width, 0.25))
            turbulence = noise(x, y, frame_no // 2) * 0.10
            inner_glow = 0.25 + 0.52 * (core ** 1.35)
            height_glow = 0.12 * math.sin(math.pi * t)
            brightness = clamp(
                (0.24 + 0.38 * edge_light + inner_glow
                 + height_glow + turbulence) * (0.80 + 0.20 * t)
            )

            # A pale, narrow core is strongest slightly below the tip.
            if core > 0.70 and 0.28 < t < 0.84:
                brightness = clamp(brightness + 0.15)

            char = glyph_for(brightness, FLAME_RAMP)
            color = color_for(brightness, FLAME_PALETTE)
            if char != " ":
                put(grid, colors, x, y, char, color)

    # 2) Small wick under the flame.
    wick_y = flame_top + flame_height
    put(grid, colors, cx, wick_y, "|", "#5b3519")
    put(grid, colors, cx, wick_y + 1, "|", "#6c3b18")

    # 3) Melted wax rim: uneven top, bright edge, darker underside.
    rim_y = wick_y + 2
    rim_width = 15
    rim_chars = ["~", "=", "~", "-", "~", "s", "~", "=", "~"]
    for dx in range(-rim_width // 2, rim_width // 2 + 1):
        x = cx + dx
        edge = abs(dx) / (rim_width / 2)
        wave = math.sin(dx * 0.8 + frame_no * 0.025)
        if edge > 0.88 and wave < -0.1:
            continue
        brightness = clamp(0.40 + 0.33 * (1 - edge) + noise(x, rim_y) * 0.05)
        char = rim_chars[(dx + frame_no // 8) % len(rim_chars)]
        put(grid, colors, x, rim_y, char, color_for(brightness, WAX_PALETTE))

    # 4) Wax body, shaded by a soft light source above/front.
    body_top = rim_y + 1
    body_bottom = 48
    body_height = body_bottom - body_top

    for y in range(body_top, body_bottom + 1):
        t = (y - body_top) / body_height

        # Slightly rounded shoulders and a softly narrowing base.
        if t < 0.07:
            half_width = 5.7 + 1.1 * t / 0.07
        elif t < 0.80:
            half_width = 6.8 + 0.16 * math.sin(t * 4.0)
        else:
            half_width = 6.8 - 0.9 * ((t - 0.80) / 0.20)

        for x in range(cx - 10, cx + 11):
            dx = x - cx
            norm_x = dx / max(half_width, 0.2)
            edge_distance = half_width - abs(dx)

            # Two small wax drips are part of the silhouette.
            drip_left = dx == -4 and body_top + 2 <= y <= body_top + 4
            drip_right = (
                (dx == 3 and body_top + 2 <= y <= body_top + 5)
                or (dx == 4 and y == body_top + 6)
            )

            if edge_distance < -0.35 and not (drip_left or drip_right):
                continue

            edge_factor = clamp((edge_distance + 0.45) / 1.8, 0.10, 1.0)
            # Bright wax around the upper front; deep amber lower down.
            top_glow = 0.30 * math.exp(-((t - 0.16) / 0.18) ** 2)
            centre_light = 0.34 * math.exp(-((norm_x + 0.20) / 0.57) ** 2)
            side_shadow = 0.22 * (abs(norm_x) ** 1.30)
            bottom_shadow = 0.27 * (t ** 1.3)
            horizontal_ridges = 0.045 * math.sin(y * 1.55 + dx * 0.16)
            grain = noise(x, y, 23) * 0.075
            flicker = 0.025 * math.sin(frame_no * 0.09 + y * 0.12 + x * 0.08)

            brightness = clamp(
                (0.31 + top_glow + centre_light - side_shadow
                 - bottom_shadow + horizontal_ridges + grain + flicker)
                * edge_factor
            )

            if drip_left or drip_right:
                brightness = max(brightness, 0.23 - 0.02 * (y - body_top))

            char = glyph_for(brightness)
            # The outline fades into the black instead of drawing a hard box.
            if edge_distance < 0.65:
                char = glyph_for(brightness * 0.72, "  ..,:;irsxX")

            if char != " ":
                put(
                    grid, colors, x, y, char,
                    color_for(brightness, WAX_PALETTE),
                )

    # Soft base shadow/reflection, sparse and dim; no title or caption.
    ground_y = 50
    rng = random.Random(3000 + frame_no // 3)
    for dx in range(-19, 20):
        distance = abs(dx)
        if distance < 5:
            brightness = 0.10 + rng.random() * 0.035
        else:
            brightness = max(0.0, 0.075 - (distance - 5) * 0.004)

        if brightness > 0.022 and rng.random() < 0.58:
            char = rng.choice([".", ":", "'", "`", "~"])
            put(
                grid, colors, cx + dx, ground_y, char,
                color_for(brightness, WAX_PALETTE),
            )

    # Flickering loose embers around the flame.
    spark_rng = random.Random(810 + frame_no // 2)
    for _ in range(5):
        y = flame_top + spark_rng.randint(3, 14)
        dx = spark_rng.choice([-13, -11, -9, -8, 8, 9, 11, 13])
        x = cx + dx + round(math.sin(frame_no * 0.11 + y) * 0.5)
        char = spark_rng.choice([".", "'", "`", "*"])
        put(grid, colors, x, y, char, spark_rng.choice(SPARK_PALETTE))

    return grid, colors


class CandleApp:
    def __init__(self, root):
        self.root = root
        root.title("Candle")
        root.configure(bg=BLACK)
        root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=COLS * CELL_W,
            height=ROWS * CELL_H,
            bg=BLACK,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(padx=PAD_X, pady=PAD_Y)

        font = ("Consolas", 9, "bold")
        self.items = []
        self.last_state = [
            [None for _ in range(COLS)] for _ in range(ROWS)
        ]

        for y in range(ROWS):
            row_items = []
            for x in range(COLS):
                item = self.canvas.create_text(
                    x * CELL_W + CELL_W // 2,
                    y * CELL_H + CELL_H // 2,
                    text="",
                    fill=BLACK,
                    font=font,
                    anchor="center",
                )
                row_items.append(item)
            self.items.append(row_items)

        self.frame_no = 0
        self.running = True
        root.bind("<Escape>", self.close)
        root.bind("q", self.close)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.animate()

    def animate(self):
        if not self.running:
            return

        grid, colors = build_frame(self.frame_no)
        for y in range(ROWS):
            for x in range(COLS):
                state = (grid[y][x], colors[y][x])
                if state != self.last_state[y][x]:
                    self.canvas.itemconfigure(
                        self.items[y][x],
                        text=state[0],
                        fill=state[1] if state[0] != " " else BLACK,
                    )
                    self.last_state[y][x] = state

        self.frame_no += 1
        self.root.after(75, self.animate)

    def close(self, _event=None):
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = max(0, (screen_w - WINDOW_W) // 2)
    y = max(0, (screen_h - WINDOW_H) // 2)
    root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")
    CandleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
