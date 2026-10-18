# EmberRise — ASCII Candle & Fireworks

A small Python animation project built with **Tkinter**. It contains three versions: a standalone flickering ASCII candle, the candle combined with fireworks and a particle-based name reveal, and a faster 2× version of that combined animation.

## What's in the repository?

| File | What it does | Animation speed |
|---|---|---|
| `candle(1).py` | Runs only the flickering ASCII candle in a separate black window. The flame and wax are drawn with shaded text characters, with warm colours and subtle sparks. There are no fireworks and no name reveal. | Normal |
| `candle _firework.py` | Plays the full sequence: the ASCII candle flickers, fireworks launch from the flame and burst into colourful particles, then red particles fly in from the edges and assemble into **AVIRAL**. | Normal |
| `CANDLE_FIREWORK2.PY` | The same candle → fireworks → **AVIRAL** particle-reveal sequence, with the animation timing set to **2× speed** (`SPEED = 2.0`). | 2× |

The two combined versions are deliberately similar: the main difference is the playback speed. The standalone candle is the simpler version without the fireworks or name reveal.

## Requirements

- Python 3
- Tkinter, which is normally included with the standard Python installation on Windows

No third-party Python packages are required. The animations are visual only; they do not include audio.

## How to run

Open PowerShell or the VS Code terminal in the folder containing the files, then run the version you want:

**1. Standalone flickering candle**

```powershell
python "candle(1).py"
```

**2. Candle + fireworks + AVIRAL reveal (normal speed)**

```powershell
python "candle _firework.py"
```

**3. Candle + fireworks + AVIRAL reveal (2× speed)**

```powershell
python .\CANDLE_FIREWORK2.PY
```

Each script opens its own window. If Windows says that a file cannot be found, check that the filename in the command matches the filename shown in VS Code Explorer exactly.

## Controls

- **Standalone candle:** press `Esc` or `q`, or close the window with its X button.
- **Combined animations:** press `r` to restart the sequence, press `Esc`, or close the window with its X button.

## How it works

- **ASCII shading:** character density and colour palettes create the candle's flame and wax texture against a black background.
- **Flame movement:** small frame-to-frame changes create the flickering effect.
- **Fireworks:** rockets rise from the flame, leave short trails, and burst into particles using different patterns and colours.
- **Name reveal:** each letter of `AVIRAL` is represented as a small dot-matrix target. Red particles approach from the edges and settle into those target points.
- **Speed variant:** `CANDLE_FIREWORK2.PY` uses `SPEED = 2.0`; change it to `1.0` in the code for normal timing.

## Project note

This is a small creative coding project focused on ASCII art, animation, particle motion, and simple visual effects using Python's standard library.
