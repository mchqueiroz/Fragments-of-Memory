"""Texturas de decalque (RGBA) para sujeira e desgaste: manchas de água, rachaduras, escorridos de ferrugem, marcas de sapato,
papéis soltos, descascado, fita. O Godot as projeta sobre paredes e chão (Room.decal / Room.scatter).

Uso: python3 -I tools/decals.py     -> grava art/tex/decal_*.png
Estilo: pixel art de poucos níveis, como as demais texturas; o alfa carrega a forma.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "art", "tex")
RNG = np.random.default_rng(1993)


def noise(n, power=2.0, seed=0):
    a = np.random.default_rng(seed).standard_normal((n, n))
    f = np.fft.fft2(a)
    k = np.sqrt(np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2)
    k[0, 0] = 1
    o = np.real(np.fft.ifft2(f / k ** power))
    return (o - o.min()) / (o.max() - o.min())


def save(name, rgb, alpha, levels=6):
    a = np.clip(alpha, 0, 1)
    a = np.round(a * levels) / levels
    img = np.dstack([np.clip(rgb, 0, 1), a])
    Image.fromarray((img * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, f"decal_{name}.png"))


def flat_rgb(n, color):
    return np.ones((n, n, 3)) * np.array(color)


def water_stain(n=64):
    yy, xx = np.mgrid[0:n, 0:n] / n
    r = np.hypot(xx - 0.5, yy - 0.5) + (noise(n, 1.6, 1) - 0.5) * 0.35
    ring = np.clip(1 - np.abs(r - 0.3) / 0.07, 0, 1) * 0.8
    fill = np.clip((0.3 - r) / 0.3, 0, 1) * 0.35
    save("stain", flat_rgb(n, (0.26, 0.20, 0.12)), ring + fill)


def streak(n=64):
    a = np.zeros((n, n))
    for x in RNG.integers(6, n - 6, 7):
        L = int(RNG.integers(n // 2, n - 4))
        w = int(RNG.integers(1, 3))
        for y in range(L):
            a[y, x:x + w] = np.maximum(a[y, x:x + w], (1 - y / L) ** 0.7 * 0.85)
    save("streak", flat_rgb(n, (0.30, 0.16, 0.08)), a * (0.6 + 0.4 * noise(n, 1.2, 2)))


def crack(n=64):
    img = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(img)

    def branch(x, y, ang, steps, w):
        for _ in range(steps):
            ang += RNG.normal(0, 0.45)
            nx, ny = x + np.cos(ang) * 2.2, y + np.sin(ang) * 2.2
            d.line([x, y, nx, ny], fill=255, width=w)
            x, y = nx, ny
            if RNG.random() < 0.12 and steps > 6:
                branch(x, y, ang + RNG.choice([-0.8, 0.8]), steps // 2, 1)
    branch(n * 0.5, 2, np.pi / 2, 28, 1)
    a = np.asarray(img).astype(float) / 255
    save("crack", flat_rgb(n, (0.07, 0.06, 0.06)), a * 0.9)


def scuff(n=64):
    a = np.zeros((n, n))
    for _ in range(9):
        y = int(RNG.integers(8, n - 8))
        x0 = int(RNG.integers(4, n // 2))
        L = int(RNG.integers(14, n - x0 - 2))
        for x in range(x0, x0 + L):
            a[y + int(np.sin(x * 0.3) * 1.5), x] = 0.6 * (1 - abs(x - x0 - L / 2) / (L / 2))
    save("scuff", flat_rgb(n, (0.70, 0.66, 0.58)), a)


def dirt(n=64):
    m = noise(n, 1.8, 3)
    yy, xx = np.mgrid[0:n, 0:n] / n
    soft = np.clip(1 - np.hypot(xx - 0.5, yy - 0.5) * 2.0, 0, 1)
    save("dirt", flat_rgb(n, (0.10, 0.08, 0.07)), soft * np.clip(m * 1.6 - 0.35, 0, 1) * 0.8)


def grime_edge(n=64):
    yy = np.mgrid[0:n, 0:n][0] / n
    m = noise(n, 1.4, 4)
    save("grime", flat_rgb(n, (0.06, 0.05, 0.05)), np.clip((1 - yy * 2.2), 0, 1) * (0.5 + 0.7 * m))


def peeling(n=64):
    m = noise(n, 1.7, 5)
    mask = (m > 0.62).astype(float)
    edge = np.clip(np.abs(m - 0.62) * 18, 0, 1)
    rgb = np.where((m > 0.62)[:, :, None], np.array((0.62, 0.58, 0.48)), np.array((0.12, 0.10, 0.09)))
    save("peeling", rgb, np.maximum(mask * 0.9, (1 - edge) * 0.7))


def paper(n=32):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([4, 3, n - 5, n - 4], fill=(225, 220, 200, 255))
    for y in range(7, n - 6, 3):
        d.line([7, y, n - 8 - int(RNG.integers(0, 6)), y], fill=(90, 90, 110, 255))
    img.save(os.path.join(OUT, "decal_paper.png"))


def tape(n=32):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 12, n - 3, 19], fill=(205, 195, 150, 200))
    img.save(os.path.join(OUT, "decal_tape.png"))


def puddle(n=64):
    m = noise(n, 1.5, 6)
    yy, xx = np.mgrid[0:n, 0:n] / n
    soft = np.clip(1 - np.hypot(xx - 0.5, yy - 0.5) * 2.1 - (m - 0.5) * 0.6, 0, 1)
    save("puddle", flat_rgb(n, (0.05, 0.07, 0.09)), np.clip(soft * 2.2, 0, 1) * 0.75)


if __name__ == "__main__":
    for fn in (water_stain, streak, crack, scuff, dirt, grime_edge, peeling, paper, tape, puddle):
        fn()
    print("decalques em", os.path.abspath(OUT))
