#!/usr/bin/env python3
"""Generates the ten wall textures used by index.html's raycaster (one per
sector, referenced via LEVELS[i].wallTexture). Procedural, not photographic -
every sector gets a texture whose *structure* (masonry coursing, plank
seams, veins, cracks) matches its theme, not just a recolored noise field.
Re-run after editing to regenerate textures/wall_*.png.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 128
RNG_BASE = 20260928  # arbitrary fixed seed so regeneration is deterministic


def rng(seed):
    return np.random.default_rng(RNG_BASE + seed)


def smooth_noise(size, seed, blur):
    r = rng(seed)
    field = r.random((size, size)).astype(np.float32)
    img = Image.fromarray((field * 255).astype(np.uint8), "L")
    img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return (arr - arr.min()) / max(1e-6, arr.max() - arr.min())


def base_fill(color):
    arr = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    arr[:, :] = np.array(color, dtype=np.float32)
    return arr


def apply_mult(arr, mult):
    return np.clip(arr * mult[..., None], 0, 255)


def apply_add(arr, add):
    return np.clip(arr + add[..., None], 0, 255)


def top_light(size=SIZE, strength=0.22):
    """Subtle overall lighting gradient, top-lit like the game's own sky."""
    rows = np.linspace(1 + strength * 0.5, 1 - strength * 0.5, size, dtype=np.float32)
    return np.repeat(rows[:, None], size, axis=1)


def fine_grain(seed, amount=10):
    r = rng(seed)
    return (r.random((SIZE, SIZE)).astype(np.float32) - 0.5) * 2 * amount


def block_coursing(seed, rows, mortar_dark=60, mortar_width=3, jitter=6, bevel=18):
    """Running-bond brick/ice-block grid: horizontal courses + staggered
    vertical seams, each block getting a light top/left bevel and dark
    bottom/right bevel for masonry depth."""
    mult = np.ones((SIZE, SIZE), dtype=np.float32)
    add = np.zeros((SIZE, SIZE), dtype=np.float32)
    r = rng(seed)
    row_h = SIZE / rows
    for ry in range(rows + 1):
        y = int(round(ry * row_h)) + int(r.integers(-jitter, jitter + 1))
        y0, y1 = max(0, y - mortar_width // 2), min(SIZE, y + mortar_width // 2 + 1)
        if y0 < y1:
            add[y0:y1, :] -= mortar_dark
    offsets = []
    cols_per_row = max(2, int(round(SIZE / (row_h * 1.6))))
    col_w = SIZE / cols_per_row
    for ry in range(rows):
        stagger = (col_w / 2) if ry % 2 else 0
        offsets.append(stagger)
        for cx in range(cols_per_row + 1):
            x = int(round(cx * col_w + stagger)) + int(r.integers(-jitter, jitter + 1))
            x0, x1 = max(0, x - mortar_width // 2), min(SIZE, x + mortar_width // 2 + 1)
            y_top = int(ry * row_h)
            y_bot = int(min(SIZE, (ry + 1) * row_h))
            if x0 < x1 and y_top < y_bot:
                add[y_top:y_bot, x0:x1] -= mortar_dark
    # Bevel: brighten a couple rows just under each horizontal mortar line,
    # darken a couple rows just above the next one - reads as a rounded
    # block face catching light from above.
    for ry in range(rows + 1):
        y = int(round(ry * row_h))
        if 0 <= y + bevel // 6 < SIZE:
            add[y:min(SIZE, y + 2), :] += 22
        if 0 <= y - 2 < SIZE:
            add[max(0, y - 2):y, :] -= 14
    return mult, add


def wood_grain_noise(seed, y_scale=10, blur=1.0):
    """Coarse-in-Y, full-resolution-in-X noise resized back up to SIZE: the
    vertical resize interpolates smoothly top-to-bottom (so each streak stays
    roughly constant along a plank's length) while every column still gets
    its own random value (so streaks vary side to side) - real wood grain
    runs along the grain, not across it."""
    r = rng(seed)
    small = r.random((y_scale, SIZE)).astype(np.float32)
    img = Image.fromarray((small * 255).astype(np.uint8), "L").resize((SIZE, SIZE), Image.BILINEAR)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return arr


def vertical_planks(seed, plank_count=6, mortar_dark=50, jitter=4, grain_strength=14):
    mult = np.ones((SIZE, SIZE), dtype=np.float32)
    add = np.zeros((SIZE, SIZE), dtype=np.float32)
    r = rng(seed)
    plank_w = SIZE / plank_count
    for cx in range(plank_count + 1):
        x = int(round(cx * plank_w)) + int(r.integers(-jitter, jitter + 1))
        x0, x1 = max(0, x - 2), min(SIZE, x + 2)
        if x0 < x1:
            add[:, x0:x1] -= mortar_dark
    # Wood grain: irregular streaks running the length of each plank, plus a
    # finer close-grain layer for texture at normal viewing distance.
    grain = wood_grain_noise(seed + 500, y_scale=10, blur=1.0)
    fine = wood_grain_noise(seed + 700, y_scale=28, blur=0.6)
    add += (grain - 0.5) * grain_strength + (fine - 0.5) * (grain_strength * 0.4)
    return mult, add


def veins(seed, count, width=2, glow=False):
    """Jagged crack/vein lines via a short random walk per vein."""
    img = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(img)
    r = rng(seed)
    for _ in range(count):
        x, y = r.integers(0, SIZE), r.integers(0, SIZE)
        pts = [(x, y)]
        steps = r.integers(6, 14)
        for _ in range(steps):
            x = np.clip(x + r.integers(-14, 15), 0, SIZE - 1)
            y = np.clip(y + r.integers(-14, 15), 0, SIZE - 1)
            pts.append((x, y))
        draw.line(pts, fill=255, width=int(width))
    if glow:
        img = img.filter(ImageFilter.GaussianBlur(1.6))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return arr


def sparkle(seed, count, size_px=(1, 2), blur=0.5):
    img = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(img)
    r = rng(seed)
    for _ in range(count):
        x, y = int(r.integers(0, SIZE)), int(r.integers(0, SIZE))
        s = int(r.integers(size_px[0], size_px[1] + 1))
        draw.ellipse([x - s, y - s, x + s, y + s], fill=int(r.integers(160, 256)))
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(img, dtype=np.float32) / 255.0


def rock_blotch(seed):
    """Two-octave blotchy luminance field for rough rock: a big-scale slow
    variation (patches of lighter/darker stone) plus a smaller-scale layer on
    top for closer surface roughness. Wider range than a single smooth_noise
    call so it actually reads as uneven rock instead of a flat tint."""
    big = smooth_noise(SIZE, seed, blur=9)
    small = smooth_noise(SIZE, seed + 1, blur=2.5)
    return 0.45 + big * 0.75 * 0.7 + small * 0.75 * 0.3


def finalize(arr, name):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(f"{name}.png")
    print(f"wrote {name}.png")


def gen_ice_fortress():
    # Carved ice-block masonry: pale blue, crisp mortar, frosty grain.
    base = base_fill([150, 205, 232])
    lum = top_light() * (0.85 + smooth_noise(SIZE, 1, 3) * 0.3)
    mult, add = block_coursing(2, rows=4, mortar_dark=45, bevel=18)
    arr = apply_add(apply_mult(base, lum * mult), add + fine_grain(3, 6))
    spk = sparkle(4, 60)
    arr = apply_add(arr, spk * 70)
    finalize(arr, "wall_ice_fortress")


def gen_frozen_caverns():
    # Rough dark cave rock with mineral veins.
    base = base_fill([96, 122, 132])
    lum = rock_blotch(10)
    arr = apply_mult(base, lum)
    arr = apply_add(arr, fine_grain(11, 16))
    v = veins(12, count=5, width=2, glow=False)
    arr = apply_add(arr, -v * 90)
    finalize(arr, "wall_frozen_caverns")


def gen_blizzard_wastes():
    # Wind-carved snow-brick: pale, soft undulating drifts, no hard mortar.
    base = base_fill([222, 232, 238])
    drift = smooth_noise(SIZE, 20, 8)
    lum = 0.82 + drift * 0.35
    arr = apply_mult(base, lum * top_light(strength=0.15))
    arr = apply_add(arr, fine_grain(21, 8))
    spk = sparkle(22, 50, size_px=(1, 1))
    arr = apply_add(arr, spk * 90)
    finalize(arr, "wall_blizzard_wastes")


def gen_emperors_keep():
    # Ornate carved stone blocks, warm firelit palette.
    base = base_fill([150, 76, 56])
    mult, add = block_coursing(30, rows=3, mortar_dark=55, bevel=20, jitter=3)
    lum = top_light(strength=0.3) * (0.85 + smooth_noise(SIZE, 31, 4) * 0.25)
    arr = apply_add(apply_mult(base, lum * mult), add + fine_grain(32, 8))
    finalize(arr, "wall_emperors_keep")


def gen_frozen_harbor():
    # Weathered dock timber, teal-gray, horizontal grain per plank.
    base = base_fill([92, 132, 138])
    mult, add = vertical_planks(40, plank_count=5, mortar_dark=48, grain_strength=16)
    lum = top_light(strength=0.2)
    arr = apply_add(apply_mult(base, lum * mult), add)
    finalize(arr, "wall_frozen_harbor")


def gen_crystal_caverns():
    # Dark rock riddled with glowing crystal veins.
    base = base_fill([58, 74, 110])
    lum = rock_blotch(50)
    arr = apply_mult(base, lum)
    arr = apply_add(arr, fine_grain(51, 12))
    v = veins(52, count=7, width=3, glow=True)
    glow_color = np.array([140, 215, 255], dtype=np.float32)
    arr = arr + v[..., None] * glow_color * 1.15
    finalize(arr, "wall_crystal_caverns")


def gen_aurora_tundra():
    # Frosted ice under aurora light - pale green/teal with sparkle.
    base = base_fill([178, 218, 205])
    lum = 0.85 + smooth_noise(SIZE, 60, 6) * 0.3
    arr = apply_mult(base, lum * top_light(strength=0.18))
    spk = sparkle(61, 26, size_px=(1, 1), blur=0.7)
    arr = apply_add(arr, spk * 80)
    arr = apply_add(arr, fine_grain(62, 6))
    finalize(arr, "wall_aurora_tundra")


def gen_christmas_village():
    # Festive chalet timber, deep green with warm mortar accents.
    base = base_fill([70, 122, 82])
    mult, add = vertical_planks(70, plank_count=6, mortar_dark=40, grain_strength=12)
    lum = top_light(strength=0.22)
    arr = apply_add(apply_mult(base, lum * mult), add)
    # A thin warm accent line two-thirds down each plank run, like painted trim.
    trim_y = int(SIZE * 0.66)
    arr[trim_y:trim_y + 3, :, 0] += 60
    arr[trim_y:trim_y + 3, :, 1] += 20
    finalize(arr, "wall_christmas_village")


def gen_northern_lights_ruins():
    # Ancient crumbling purple-gray stone, heavy dark cracking.
    base = base_fill([118, 100, 150])
    lum = rock_blotch(80)
    arr = apply_mult(base, lum)
    arr = apply_add(arr, fine_grain(81, 14))
    v = veins(82, count=8, width=3, glow=False)
    arr = apply_add(arr, -v * 110)
    finalize(arr, "wall_northern_lights_ruins")


def gen_frozen_throne():
    # Grand ornate royal stone with glowing veins - the finale sector.
    base = base_fill([172, 62, 58])
    mult, add = block_coursing(90, rows=3, mortar_dark=50, bevel=22, jitter=2)
    lum = top_light(strength=0.3) * (0.85 + smooth_noise(SIZE, 91, 4) * 0.2)
    arr = apply_add(apply_mult(base, lum * mult), add)
    v = veins(92, count=4, width=2, glow=True)
    glow_color = np.array([255, 210, 120], dtype=np.float32)
    arr = arr + v[..., None] * glow_color * 0.8
    finalize(arr, "wall_frozen_throne")


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gen_ice_fortress()
    gen_frozen_caverns()
    gen_blizzard_wastes()
    gen_emperors_keep()
    gen_frozen_harbor()
    gen_crystal_caverns()
    gen_aurora_tundra()
    gen_christmas_village()
    gen_northern_lights_ruins()
    gen_frozen_throne()
