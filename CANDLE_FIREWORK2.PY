import math
import random
import time
import tkinter as tk

# ============================================================
# CANDLE + FIREWORKS + PARTICLE REVEAL: AVIRAL
# The fireworks launch from the flickering candle flame.
# After the final bursts fade, particles fly in from all four
# edges and assemble into a glowing red AVIRAL.
#
# Run: python candle_firework_aviral_2x.py
# No third-party packages required.
# Close with Esc or the window's X button.
# ============================================================

COLS, ROWS = 90, 62
CELL_W, CELL_H = 11, 10
PAD = 12
CANVAS_W, CANVAS_H = COLS * CELL_W, ROWS * CELL_H
WINDOW_W, WINDOW_H = CANVAS_W + PAD * 2, CANVAS_H + PAD * 2
BLACK = "#000000"
SPEED = 2.0  # 2x animation speed; set to 1.0 for normal speed

WAX_PALETTE = [
    "#100705", "#180906", "#220d07", "#2c1007", "#381407",
    "#471907", "#572008", "#69270a", "#7b2e0d", "#8e3710",
    "#a34214", "#b55019", "#c96320", "#d9782a", "#e78d37",
    "#f1a74c", "#f8c36d", "#ffdda0",
]
FLAME_PALETTE = [
    "#230804", "#3c1005", "#5a1706", "#762006", "#962908",
    "#b9360b", "#d84a0e", "#ef6412", "#ff8018", "#ff9c20",
    "#ffb632", "#ffd15c", "#ffe58a", "#fff2bc",
]
FIREWORK_PALETTES = [
    ["#ff3b30", "#ff7548", "#ffc06b", "#fff0bb"],
    ["#40c9ff", "#52f0d0", "#b0fff0", "#ffffff"],
    ["#b46bff", "#ed64ff", "#ffb2f9", "#fff0ff"],
    ["#ff4f94", "#ff9e48", "#ffe36e", "#fff6ce"],
    ["#78ff62", "#d1ff76", "#fff5a6", "#ffffff"],
    ["#6287ff", "#9aaaff", "#e0e7ff", "#ffffff"],
]
SPARK_PALETTE = ["#572008", "#92350c", "#c7510e", "#e98222", "#ffbd45"]
RED_NAME = ["#65000b", "#960015", "#c40020", "#ed1638", "#ff4057"]
RAMP = "  ..,,:;irsXA253hMHGS#9B&@"
FLAME_RAMP = " .,:;irsxX2358#@$"
FLAME_WIDTHS = [
    0.18, 0.38, 0.68, 1.05, 1.50, 1.98, 2.40,
    2.73, 2.90, 2.80, 2.50, 2.05, 1.48, 0.92,
]
NAME_PIXELS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
}
NAME = "AVIRAL"


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def noise(x, y, seed=0):
    n = math.sin(x * 127.1 + y * 311.7 + seed * 74.7) * 43758.5453
    return (n - math.floor(n)) * 2.0 - 1.0


def glyph_for(value, ramp=RAMP):
    idx = min(len(ramp) - 1, int(clamp(value) * (len(ramp) - 1) + 0.5))
    return ramp[idx]


def color_for(value, palette):
    idx = min(len(palette) - 1, int(clamp(value) * (len(palette) - 1) + 0.5))
    return palette[idx]


def put(grid, colors, x, y, char, color):
    if 0 <= x < COLS and 0 <= y < ROWS:
        grid[y][x] = char
        colors[y][x] = color


def build_candle_frame(frame_no):
    """Return character and colour grids for the continuously flickering candle."""
    grid = [[" " for _ in range(COLS)] for _ in range(ROWS)]
    colors = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    cx = COLS // 2
    flame_top = 24

    sway = (
        math.sin(frame_no * 0.18) * 0.66
        + math.sin(frame_no * 0.071 + 1.4) * 0.38
    )
    width_pulse = 1.0 + 0.055 * math.sin(frame_no * 0.27)
    flame_height = len(FLAME_WIDTHS)

    # Flame contours are shaded with character density, not a solid triangle.
    for row, base_width in enumerate(FLAME_WIDTHS):
        y = flame_top + row
        t = row / max(1, flame_height - 1)
        centre = cx + sway * (0.20 + 0.80 * t)
        centre += math.sin(frame_no * 0.13 + t * 5.3) * 0.22
        half_width = base_width * width_pulse

        for x in range(math.floor(centre - half_width - 0.5),
                       math.ceil(centre + half_width + 0.5) + 1):
            dx = x - centre
            edge = half_width - abs(dx)
            if edge < -0.35:
                continue

            edge_light = clamp((edge + 0.35) / 1.05)
            core = clamp(1.0 - abs(dx) / max(half_width, 0.25))
            turbulence = noise(x, y, frame_no // 2) * 0.10
            brightness = clamp(
                0.24 + 0.37 * edge_light + 0.33 * core ** 1.3
                + 0.08 * math.sin(math.pi * t) + turbulence
            )
            if core > 0.70 and 0.28 < t < 0.84:
                brightness = clamp(brightness + 0.12)

            char = glyph_for(brightness, FLAME_RAMP)
            if char != " ":
                put(grid, colors, x, y, char,
                    color_for(brightness, FLAME_PALETTE))

    # Wick.
    wick_y = flame_top + flame_height
    put(grid, colors, cx, wick_y, "|", "#56321b")
    put(grid, colors, cx, wick_y + 1, "|", "#6c3b18")

    # Irregular melted rim.
    rim_y = wick_y + 2
    rim_chars = ["~", "=", "~", "-", "~", "s", "~", "=", "~"]
    for dx in range(-8, 9):
        x = cx + dx
        edge = abs(dx) / 8.0
        if edge > 0.88 and math.sin(dx * 0.8) < -0.1:
            continue
        brightness = clamp(0.42 + 0.31 * (1 - edge) + noise(x, rim_y) * 0.05)
        char = rim_chars[(dx + frame_no // 8) % len(rim_chars)]
        put(grid, colors, x, rim_y, char, color_for(brightness, WAX_PALETTE))

    # Candle body with soft side shadows and granular wax texture.
    body_top, body_bottom = rim_y + 1, 57
    body_height = body_bottom - body_top
    for y in range(body_top, body_bottom + 1):
        t = (y - body_top) / max(1, body_height)
        half_width = 6.4 + 0.18 * math.sin(t * 4.0)
        if t < 0.10:
            half_width = 5.7 + 0.7 * t / 0.10
        elif t > 0.84:
            half_width -= 0.7 * ((t - 0.84) / 0.16)

        for x in range(cx - 10, cx + 11):
            dx = x - cx
            norm_x = dx / max(half_width, 0.2)
            edge_distance = half_width - abs(dx)
            drip_left = dx == -4 and body_top + 2 <= y <= body_top + 4
            drip_right = (
                (dx == 3 and body_top + 2 <= y <= body_top + 5)
                or (dx == 4 and y == body_top + 6)
            )
            if edge_distance < -0.35 and not (drip_left or drip_right):
                continue

            edge_factor = clamp((edge_distance + 0.45) / 1.8, 0.10, 1.0)
            top_glow = 0.26 * math.exp(-((t - 0.13) / 0.20) ** 2)
            centre_light = 0.33 * math.exp(-((norm_x + 0.20) / 0.60) ** 2)
            side_shadow = 0.24 * abs(norm_x) ** 1.3
            bottom_shadow = 0.27 * t ** 1.3
            texture = noise(x, y, 23) * 0.075
            ridges = 0.045 * math.sin(y * 1.55 + dx * 0.16)
            flicker = 0.022 * math.sin(frame_no * 0.09 + y * 0.12 + x * 0.08)
            brightness = clamp(
                (0.31 + top_glow + centre_light - side_shadow
                 - bottom_shadow + texture + ridges + flicker) * edge_factor
            )
            if drip_left or drip_right:
                brightness = max(brightness, 0.24)

            char = glyph_for(brightness)
            if edge_distance < 0.65:
                char = glyph_for(brightness * 0.72, "  ..,:;irsxX")
            if char != " ":
                put(grid, colors, x, y, char, color_for(brightness, WAX_PALETTE))

    # Sparse amber reflections under the wax; intentionally no text/caption.
    rng = random.Random(3000 + frame_no // 3)
    for dx in range(-18, 19):
        d = abs(dx)
        brightness = 0.10 + rng.random() * 0.025 if d < 5 else max(0, 0.07 - (d - 5) * 0.004)
        if brightness > 0.022 and rng.random() < 0.55:
            put(grid, colors, cx + dx, 59, rng.choice([".", ":", "'", "`", "~"]),
                color_for(brightness, WAX_PALETTE))

    # Flickering embers floating near the flame.
    spark_rng = random.Random(810 + frame_no // 2)
    for _ in range(5):
        y = flame_top + spark_rng.randint(3, 12)
        dx = spark_rng.choice([-13, -11, -9, -8, 8, 9, 11, 13])
        x = cx + dx + round(math.sin(frame_no * 0.11 + y) * 0.5)
        put(grid, colors, x, y, spark_rng.choice([".", "'", "`", "*"]),
            spark_rng.choice(SPARK_PALETTE))

    # Return approximate on-screen flame tip for the firework launch origin.
    flame_x = (cx + sway * 0.2) * CELL_W + CELL_W / 2
    flame_y = (flame_top + 4.4) * CELL_H
    return grid, colors, (flame_x, flame_y)


def make_name_targets():
    # 5x7 dot-matrix letters with one blank column between letters.
    pixel_x, pixel_y = 13, 15
    total_columns = len(NAME) * 5 + len(NAME) - 1
    total_width = (total_columns - 1) * pixel_x
    start_x = CANVAS_W / 2 - total_width / 2
    start_y = 112
    targets = []
    col = 0
    for letter in NAME:
        bitmap = NAME_PIXELS[letter]
        for row, row_bits in enumerate(bitmap):
            for bit, value in enumerate(row_bits):
                if value == "1":
                    targets.append((
                        start_x + (col + bit) * pixel_x,
                        start_y + row * pixel_y
                    ))
        col += 6
    return targets


class CandleFireworkApp:
    def __init__(self, root):
        self.root = root
        root.title("Candle Firework - AVIRAL")
        root.configure(bg=BLACK)
        root.resizable(False, False)
        self.canvas = tk.Canvas(
            root, width=CANVAS_W, height=CANVAS_H,
            bg=BLACK, highlightthickness=0, bd=0
        )
        self.canvas.pack(padx=PAD, pady=PAD)

        self.text_items = []
        self.previous_grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        font = ("Consolas", 9, "bold")
        for y in range(ROWS):
            row_items = []
            for x in range(COLS):
                item = self.canvas.create_text(
                    x * CELL_W + CELL_W // 2,
                    y * CELL_H + CELL_H // 2,
                    text="",
                    fill=BLACK,
                    font=font,
                    anchor="center"
                )
                row_items.append(item)
            self.text_items.append(row_items)

        self.frame_no = 0
        self.phase = "fireworks"
        self.phase_elapsed = 0.0
        self.launch_stop_time = 7.8
        self.next_launch = 0.25
        self.rockets = []
        self.fire_particles = []
        self.name_particles = []
        self.name_trails = []
        self.name_formed_at = None
        self.last_time = time.perf_counter()
        self.running = True

        root.bind("<Escape>", self.close)
        root.bind("r", self.restart)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.animate()

    def close(self, _event=None):
        self.running = False
        self.root.destroy()

    def restart(self, _event=None):
        for collection in (self.rockets, self.fire_particles,
                           self.name_particles, self.name_trails):
            for item in collection:
                ids = item.get("items", [])
                for canvas_id in ids:
                    self.canvas.delete(canvas_id)
                if item.get("item") is not None:
                    self.canvas.delete(item["item"])
        self.rockets.clear()
        self.fire_particles.clear()
        self.name_particles.clear()
        self.name_trails.clear()
        self.phase = "fireworks"
        self.phase_elapsed = 0.0
        self.next_launch = 0.25
        self.name_formed_at = None
        self.last_time = time.perf_counter()

    def launch_rocket(self, flame_origin):
        sx, sy = flame_origin
        # Rocket destinations vary to create a sky full of overlapping bursts.
        tx = random.uniform(65, CANVAS_W - 65)
        ty = random.uniform(42, 325)
        palette = random.choice(FIREWORK_PALETTES)
        duration = random.uniform(0.68, 1.22)
        item = self.canvas.create_oval(
            sx - 2, sy - 2, sx + 2, sy + 2,
            fill=palette[-1], outline=""
        )
        self.rockets.append({
            "sx": sx, "sy": sy, "x": sx, "y": sy,
            "tx": tx, "ty": ty, "elapsed": 0.0,
            "duration": duration, "palette": palette,
            "item": item, "trail_clock": 0.0,
        })

    def add_fire_particle(self, x, y, vx, vy, color, life, size,
                          gravity=95.0, drag=0.985):
        item = self.canvas.create_oval(
            x-size, y-size, x+size, y+size,
            fill=color, outline=""
        )
        self.fire_particles.append({
            "x": x, "y": y, "vx": vx, "vy": vy,
            "life": life, "max_life": life, "size": size,
            "gravity": gravity, "drag": drag,
            "color": color, "item": item
        })

    def burst(self, x, y, palette):
        style = random.choice(["sphere", "ring", "double", "spiral", "willow", "chrysanthemum"])
        count = random.randint(88, 132)
        base_angle = random.random() * math.tau

        for i in range(count):
            angle = base_angle + math.tau * i / count
            if style in ("sphere", "chrysanthemum", "willow"):
                angle += random.uniform(-0.035, 0.035)
            elif style == "spiral":
                angle = base_angle + i * 2.399963 + random.uniform(-0.04, 0.04)
            else:
                angle += random.uniform(-0.018, 0.018)

            speed = random.uniform(65, 210)
            if style == "ring":
                speed = random.uniform(145, 178)
            elif style == "double":
                speed = random.uniform(105, 145) if i % 2 else random.uniform(185, 225)
            elif style == "willow":
                speed = random.uniform(70, 165)

            color = palette[i % len(palette)] if i % 4 else random.choice(palette)
            life = random.uniform(0.85, 1.65)
            if style == "willow":
                life = random.uniform(1.20, 1.90)
            gravity = 112 if style == "willow" else random.uniform(48, 82)
            size = random.uniform(1.2, 2.7)

            self.add_fire_particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color, life, size, gravity=gravity,
                drag=random.uniform(0.975, 0.993)
            )

        # Central glitter flash and secondary tiny sparks.
        for _ in range(15):
            angle = random.random() * math.tau
            speed = random.uniform(18, 80)
            self.add_fire_particle(
                x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                random.choice(palette), random.uniform(0.22, 0.55),
                random.uniform(1.0, 2.0), gravity=20, drag=0.95
            )

    def update_rockets(self, dt, flame_origin):
        for rocket in self.rockets[:]:
            rocket["elapsed"] += dt
            p = clamp(rocket["elapsed"] / rocket["duration"])
            ease = 1 - (1 - p) ** 1.55
            rocket["x"] = rocket["sx"] + (rocket["tx"] - rocket["sx"]) * ease
            rocket["y"] = rocket["sy"] + (rocket["ty"] - rocket["sy"]) * ease
            self.canvas.coords(
                rocket["item"],
                rocket["x"] - 2.1, rocket["y"] - 2.1,
                rocket["x"] + 2.1, rocket["y"] + 2.1
            )

            rocket["trail_clock"] += dt
            if rocket["trail_clock"] >= 0.035:
                rocket["trail_clock"] = 0
                self.add_fire_particle(
                    rocket["x"], rocket["y"] + 2,
                    random.uniform(-10, 10), random.uniform(20, 65),
                    random.choice(["#ffb632", "#ff8018", "#fff0bc"]),
                    random.uniform(0.22, 0.42), random.uniform(1.0, 1.8),
                    gravity=30, drag=0.93
                )

            if p >= 1.0:
                self.canvas.delete(rocket["item"])
                self.burst(rocket["tx"], rocket["ty"], rocket["palette"])
                self.rockets.remove(rocket)

    def update_fire_particles(self, dt):
        for p in self.fire_particles[:]:
            p["life"] -= dt
            if p["life"] <= 0:
                self.canvas.delete(p["item"])
                self.fire_particles.remove(p)
                continue

            p["vx"] *= p["drag"] ** (dt * 60)
            p["vy"] = p["vy"] * (p["drag"] ** (dt * 60)) + p["gravity"] * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            fade = clamp(p["life"] / p["max_life"])
            r = max(0.45, p["size"] * (0.35 + 0.65 * fade))
            self.canvas.coords(
                p["item"], p["x"] - r, p["y"] - r,
                p["x"] + r, p["y"] + r
            )

    def create_name_particles(self):
        targets = make_name_targets()
        for index, (tx, ty) in enumerate(targets):
            side = random.choice(["left", "right", "top", "bottom"])
            if side == "left":
                sx, sy = -random.uniform(15, 80), random.uniform(20, CANVAS_H - 20)
            elif side == "right":
                sx, sy = CANVAS_W + random.uniform(15, 80), random.uniform(20, CANVAS_H - 20)
            elif side == "top":
                sx, sy = random.uniform(15, CANVAS_W - 15), -random.uniform(15, 70)
            else:
                sx, sy = random.uniform(15, CANVAS_W - 15), CANVAS_H + random.uniform(15, 70)

            shade = random.choice(RED_NAME)
            size = random.uniform(2.0, 3.4)
            glow = self.canvas.create_oval(
                sx - size*2.7, sy - size*2.7,
                sx + size*2.7, sy + size*2.7,
                fill="#390009", outline=""
            )
            core = self.canvas.create_oval(
                sx-size, sy-size, sx+size, sy+size,
                fill=shade, outline=""
            )
            self.name_particles.append({
                "x": sx, "y": sy, "sx": sx, "sy": sy,
                "tx": tx, "ty": ty, "delay": random.uniform(0, 0.70),
                "duration": random.uniform(1.15, 2.0),
                "elapsed": 0.0, "size": size, "shade": shade,
                "items": [glow, core], "index": index,
                "curve": random.uniform(-1.0, 1.0) * 42,
                "side": side
            })

    def update_name_particles(self, dt):
        all_arrived = True
        for p in self.name_particles:
            p["elapsed"] += dt
            local_t = (p["elapsed"] - p["delay"]) / p["duration"]
            if local_t < 0:
                all_arrived = False
                continue

            t = clamp(local_t)
            ease = t * t * (3 - 2*t)
            swirl = math.sin((1 - ease) * 4.2 + p["index"] * 0.21) * (1 - ease)
            x = p["sx"] + (p["tx"] - p["sx"]) * ease
            y = p["sy"] + (p["ty"] - p["sy"]) * ease
            x += swirl * p["curve"]
            y += math.cos((1 - ease) * 4 + p["index"] * 0.18) * (1 - ease) * 25

            if t < 0.99:
                all_arrived = False
                # A short red particle trail behind converging particles.
                if random.random() < 0.19:
                    trail_size = random.uniform(0.8, 1.6)
                    trail_color = random.choice(["#4a0008", "#75000f", "#a9001c"])
                    trail_item = self.canvas.create_oval(
                        x-trail_size, y-trail_size,
                        x+trail_size, y+trail_size,
                        fill=trail_color, outline=""
                    )
                    self.name_trails.append({
                        "x": x, "y": y, "life": random.uniform(0.18, 0.38),
                        "max_life": 0.38, "item": trail_item, "size": trail_size
                    })
            else:
                x = p["tx"] + math.sin(self.phase_elapsed * 2 + p["index"]) * 0.40
                y = p["ty"] + math.cos(self.phase_elapsed * 2 + p["index"]) * 0.35

            glow, core = p["items"]
            size = p["size"]
            self.canvas.coords(glow, x-size*2.7, y-size*2.7, x+size*2.7, y+size*2.7)
            self.canvas.coords(core, x-size, y-size, x+size, y+size)

        if all_arrived and self.name_formed_at is None:
            self.name_formed_at = self.phase_elapsed

    def update_name_trails(self, dt):
        for trail in self.name_trails[:]:
            trail["life"] -= dt
            if trail["life"] <= 0:
                self.canvas.delete(trail["item"])
                self.name_trails.remove(trail)

    def update_candle(self):
        grid, colors, flame_origin = build_candle_frame(self.frame_no)
        for y in range(ROWS):
            for x in range(COLS):
                state = (grid[y][x], colors[y][x])
                if state != self.previous_grid[y][x]:
                    self.canvas.itemconfigure(
                        self.text_items[y][x],
                        text=state[0],
                        fill=state[1] if state[0] != " " else BLACK,
                    )
                    self.previous_grid[y][x] = state
        return flame_origin

    def animate(self):
        if not self.running:
            return

        now = time.perf_counter()
        dt = min(now - self.last_time, 0.045)
        self.last_time = now
        dt *= SPEED
        self.phase_elapsed += dt
        self.frame_no += int(SPEED)

        flame_origin = self.update_candle()

        if self.phase == "fireworks":
            if self.phase_elapsed < self.launch_stop_time and self.phase_elapsed >= self.next_launch:
                self.launch_rocket(flame_origin)
                self.next_launch = self.phase_elapsed + random.uniform(0.30, 0.48)

            self.update_rockets(dt, flame_origin)
            self.update_fire_particles(dt)

            # Wait for the last rockets and all burst particles to finish.
            if (
                self.phase_elapsed >= self.launch_stop_time
                and not self.rockets
                and not self.fire_particles
            ):
                self.phase = "gather"
                self.phase_elapsed = 0.0
                self.create_name_particles()

        elif self.phase == "gather":
            self.update_name_particles(dt)
            self.update_name_trails(dt)

        self.root.after(33, self.animate)


def main():
    root = tk.Tk()
    root.configure(bg=BLACK)
    screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
    x = max(0, (screen_w - WINDOW_W) // 2)
    y = max(0, (screen_h - WINDOW_H) // 2)
    root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")
    CandleFireworkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
