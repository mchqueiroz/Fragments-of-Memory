"""Imagens com significado para a ambientação russa de 1993 (pixel art procedural, texto em cirílico).

Uso: python3 tools/russian.py     -> grava art/tex/*.png
Cada peça existe por um motivo da história (ver docs/): o retrato de Lena, o calendário parado em março de 1992,
o jornal de 3 de outubro de 1993, a mancha clara onde ficava o retrato de Lenin, o canto do ícone, etc.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "art", "tex")
os.makedirs(OUT, exist_ok=True)
BOLD = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf"
SERIF = "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"
RNG = np.random.default_rng(1993)


def font(path, size):
    return ImageFont.truetype(path, size)


def text(d, xy, s, size, fill, path=BOLD, anchor="la"):
    d.fontmode = "1"  # sem antialias: pixel nítido
    d.text(xy, s, font=font(path, size), fill=fill, anchor=anchor)


def finish(img, name, grain=0.05, levels=24, sepia=False):
    a = np.asarray(img.convert("RGB")).astype(float) / 255.0
    if sepia:
        g = a @ np.array([0.299, 0.587, 0.114])
        a = np.stack([g * 1.0, g * 0.82, g * 0.62], axis=-1)
    a = a * (1 + (RNG.random(a.shape[:2]) - 0.5)[:, :, None] * 2 * grain)
    a = np.round(np.clip(a, 0, 1) * levels) / levels
    Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))


def noise(n, power=2.0, seed=0, m=None):
    m = m or n
    a = np.random.default_rng(seed).standard_normal((n, m))
    f = np.fft.fft2(a)
    k = np.sqrt(np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(m)[None, :] ** 2)
    k[0, 0] = 1
    o = np.real(np.fft.ifft2(f / k ** power))
    return (o - o.min()) / (o.max() - o.min())


# --------------------------------------------------------------------------------------------
# Fotos e quadros
# --------------------------------------------------------------------------------------------
def pic_lena():
    w, h = 56, 72
    img = Image.new("RGB", (w, h), (150, 140, 125))
    d = ImageDraw.Draw(img)
    for y in range(h):
        c = int(120 + 50 * (1 - y / h))
        d.line([0, y, w, y], fill=(c, c - 6, c - 14))
    d.ellipse([6, 50, 50, 100], fill=(60, 55, 70))                    # ombros (casaco escuro)
    d.rectangle([24, 42, 32, 54], fill=(225, 190, 165))               # pescoço
    d.ellipse([15, 14, 41, 48], fill=(235, 200, 175))                 # rosto
    d.pieslice([12, 8, 44, 42], 180, 360, fill=(70, 50, 40))          # cabelo
    d.ellipse([20, 3, 36, 15], fill=(70, 50, 40))                     # coque
    d.rectangle([12, 16, 16, 40], fill=(70, 50, 40))
    d.rectangle([40, 16, 44, 40], fill=(70, 50, 40))
    for ex in (21, 32):
        d.rectangle([ex, 28, ex + 4, 29], fill=(245, 240, 230))
        d.rectangle([ex + 1, 28, ex + 3, 29], fill=(40, 30, 25))
        d.line([ex - 1, 25, ex + 5, 25], fill=(70, 50, 40))
    d.line([28, 31, 28, 37], fill=(190, 150, 130))
    d.rectangle([24, 41, 32, 42], fill=(150, 70, 70))                 # sorriso
    d.polygon([(0, h), (0, h - 20), (20, h)], fill=(10, 10, 10))      # fita de luto no canto
    d.rectangle([0, 0, w - 1, h - 1], outline=(235, 225, 200))
    finish(img, "pic_lena", grain=0.07, sepia=True)


def pic_team():
    w, h = 104, 64
    img = Image.new("RGB", (w, h), (130, 130, 135))
    d = ImageDraw.Draw(img)
    for y in range(h):
        c = int(150 - 50 * y / h)
        d.line([0, y, w, y], fill=(c, c, c + 4))
    d.polygon([(66, h), (74, 6), (82, 6), (90, h)], fill=(205, 205, 210))   # ogiva do foguete
    d.polygon([(74, 6), (78, -6), (82, 6)], fill=(205, 205, 210))
    d.line([78, 8, 78, h], fill=(120, 120, 125))
    d.rectangle([0, 48, w, h], fill=(70, 70, 72))
    xs = [8, 18, 28, 38, 48, 58, 98]
    for i, x in enumerate(xs):
        top = 26 + int(RNG.integers(0, 6))
        d.rectangle([x - 4, top + 9, x + 4, 56], fill=(225, 225, 230))     # jaleco branco
        d.ellipse([x - 3, top, x + 3, top + 7], fill=(215, 185, 165))
        d.rectangle([x - 3, top - 1, x + 3, top + 1], fill=(60, 50, 45) if i % 3 else (170, 170, 170))
    text(d, (3, 3), "ИКИ  1984", 7, (240, 240, 240), REG)
    d.rectangle([0, 0, w - 1, h - 1], outline=(235, 235, 235))
    finish(img, "pic_team", grain=0.08, sepia=True)


def poster_space():
    w, h = 64, 96
    img = Image.new("RGB", (w, h), (225, 205, 160))
    d = ImageDraw.Draw(img)
    d.polygon([(0, h), (0, 60), (64, 16), (64, 40)], fill=(190, 40, 35))       # faixa diagonal vermelha
    d.polygon([(30, 70), (36, 66), (52, 24), (58, 28), (40, 70), (34, 76)], fill=(25, 25, 30))
    d.polygon([(52, 24), (60, 8), (58, 28)], fill=(25, 25, 30))                 # foguete na diagonal
    cx, cy = 18, 24                                                             # estrela
    pts = []
    for i in range(10):
        r = 14 if i % 2 == 0 else 6
        a = -np.pi / 2 + i * np.pi / 5
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    d.polygon(pts, fill=(240, 190, 40), outline=(25, 25, 30))
    text(d, (32, 84), "К ЗВЁЗДАМ!", 8, (30, 25, 25), BOLD, "ma")
    text(d, (32, 2), "СЛАВА ТРУДУ", 6, (160, 30, 30), BOLD, "ma")
    d.rectangle([0, 0, w - 1, h - 1], outline=(40, 30, 25))
    finish(img, "poster_space", grain=0.05)


def diploma():
    w, h = 96, 72
    img = Image.new("RGB", (w, h), (232, 222, 190))
    d = ImageDraw.Draw(img)
    d.rectangle([3, 3, w - 4, h - 4], outline=(120, 40, 35))
    d.rectangle([6, 6, w - 7, h - 7], outline=(120, 40, 35))
    text(d, (w // 2, 10), "ДИПЛОМ", 11, (110, 30, 30), BOLD, "ma")
    text(d, (w // 2, 26), "Морозов Сергей Иванович", 6, (40, 35, 35), REG, "ma")
    text(d, (w // 2, 34), "окончил физический факультет", 5, (60, 55, 55), REG, "ma")
    text(d, (w // 2, 41), "МГУ имени М. В. Ломоносова", 5, (60, 55, 55), REG, "ma")
    d.ellipse([10, 50, 26, 66], fill=(170, 30, 30), outline=(110, 20, 20))
    text(d, (18, 58), "СССР", 4, (240, 220, 180), BOLD, "mm")
    d.line([48, 62, 62, 56, 70, 62, 84, 55], fill=(30, 30, 90))
    finish(img, "diploma", grain=0.05)


def calendar_1992():
    w, h = 48, 64
    img = Image.new("RGB", (w, h), (238, 232, 215))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 16], fill=(180, 35, 30))
    text(d, (w // 2, 8), "МАРТ", 9, (245, 235, 220), BOLD, "mm")
    text(d, (w // 2, 22), "1992", 6, (40, 35, 35), BOLD, "mm")
    for i, n in enumerate(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]):
        text(d, (3 + i * 6, 27), n[0], 5, (180, 35, 30) if i > 4 else (60, 55, 55), REG)
    day = 1
    for r in range(5):
        for c in range(7):
            if (r == 0 and c < 6) or day > 31:
                continue
            x, y = 3 + c * 6, 34 + r * 6
            text(d, (x, y), str(day), 4, (60, 55, 55), REG)
            if day <= 14:
                d.line([x - 1, y, x + 4, y + 5], fill=(30, 30, 140))      # dias riscados até o 14
            if day == 14:
                d.ellipse([x - 2, y - 1, x + 5, y + 6], outline=(180, 35, 30))
            day += 1
    finish(img, "calendar_1992", grain=0.05)


def newspaper():
    w, h = 112, 80
    img = Image.new("RGB", (w, h), (214, 208, 190))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 3), "ИЗВЕСТИЯ", 11, (30, 28, 28), SERIF, "ma")
    d.line([3, 17, w - 3, 17], fill=(40, 38, 38))
    text(d, (4, 19), "3 ОКТЯБРЯ 1993", 5, (60, 55, 55), REG)
    text(d, (w - 4, 19), "№ 191", 5, (60, 55, 55), REG, "ra")
    text(d, (4, 28), "ЧРЕЗВЫЧАЙНОЕ", 7, (20, 18, 18), BOLD)
    text(d, (4, 38), "ПОЛОЖЕНИЕ", 7, (20, 18, 18), BOLD)
    d.rectangle([66, 27, w - 4, 52], fill=(120, 118, 112))                   # foto: tanques
    for tx in (70, 88):
        d.rectangle([tx, 44, tx + 12, 48], fill=(40, 40, 38))
        d.rectangle([tx + 3, 41, tx + 9, 44], fill=(40, 40, 38))
        d.line([tx + 9, 42, tx + 20, 40], fill=(40, 40, 38))
    for col in range(3):
        for r in range(11):
            y = 56 + r * 2
            if y < h - 2:
                d.line([4 + col * 36, y, 4 + col * 36 + int(RNG.integers(18, 32)), y], fill=(90, 86, 82))
    finish(img, "newspaper", grain=0.06)


def door_plate():
    w, h = 64, 22
    img = Image.new("RGB", (w, h), (176, 140, 70))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(110, 80, 35))
    text(d, (w // 2, 6), "Начальник отдела", 6, (40, 28, 12), REG, "mm")
    text(d, (w // 2, 15), "Морозов С. И.", 7, (40, 28, 12), BOLD, "mm")
    finish(img, "door_plate", grain=0.06)


def icon():
    w, h = 32, 44
    img = Image.new("RGB", (w, h), (170, 130, 40))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(110, 75, 20))
    d.ellipse([9, 4, 23, 18], fill=(210, 165, 60), outline=(120, 85, 20))      # nimbo dourado
    d.ellipse([12, 7, 20, 16], fill=(205, 165, 130))                           # rosto
    d.polygon([(6, 44), (8, 20), (24, 20), (26, 44)], fill=(40, 40, 90))       # manto azul
    d.polygon([(11, 20), (21, 20), (16, 36)], fill=(120, 30, 30))              # veste vermelha
    d.ellipse([13, 28, 19, 34], fill=(205, 165, 130))                          # criança
    d.point([14, 10], fill=(40, 30, 20))
    d.point([18, 10], fill=(40, 30, 20))
    finish(img, "icon", grain=0.08)


def papirosy():
    w, h = 32, 20
    img = Image.new("RGB", (w, h), (205, 190, 150))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 5], fill=(50, 80, 60))
    text(d, (w // 2, 3), "БЕЛОМОР", 5, (230, 225, 200), BOLD, "mm")
    text(d, (w // 2, 12), "КАНАЛ", 6, (60, 40, 30), BOLD, "mm")
    d.line([4, 17, w - 4, 17], fill=(60, 40, 30))
    finish(img, "papirosy", grain=0.06)


def tape_label():
    w, h = 32, 14
    img = Image.new("RGB", (w, h), (225, 215, 185))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 5), "ЛЕНА", 8, (40, 30, 110), BOLD, "mm")
    d.line([2, 11, w - 2, 11], fill=(150, 140, 120))
    text(d, (w // 2, 11), "1991", 3, (80, 70, 60), REG, "mm")
    finish(img, "tape_label", grain=0.05)


def folder_secret():
    w, h = 40, 28
    img = Image.new("RGB", (w, h), (190, 170, 120))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, w - 3, 8], fill=(225, 215, 185))
    text(d, (w // 2, 5), "ДЕЛО № 17", 5, (40, 35, 35), BOLD, "mm")
    d.rectangle([5, 14, w - 6, 24], outline=(170, 30, 30), width=1)
    text(d, (w // 2, 19), "СЕКРЕТНО", 5, (170, 30, 30), BOLD, "mm")
    finish(img, "folder_secret", grain=0.07)


# --------------------------------------------------------------------------------------------
# Acabamentos soviéticos
# --------------------------------------------------------------------------------------------
def kover_wall():
    """Tapete de parede (kover): vermelho-escuro com medalhão central e bordas, objeto icônico de 1970-90."""
    w, h = 128, 176
    img = Image.new("RGB", (w, h), (92, 22, 24))
    d = ImageDraw.Draw(img)
    for off, col in ((2, (176, 140, 70)), (7, (60, 14, 18)), (11, (176, 140, 70))):
        d.rectangle([off, off, w - 1 - off, h - 1 - off], outline=col)
    for y in range(16, h - 16, 8):                                                # bordas ornamentadas
        for x in (5, w - 6):
            d.rectangle([x - 1, y, x + 1, y + 3], fill=(176, 140, 70))
    cx, cy = w // 2, h // 2
    for r, col in ((44, (60, 14, 18)), (38, (150, 110, 50)), (32, (92, 22, 24)), (22, (176, 140, 70)),
                   (16, (60, 14, 18)), (8, (176, 140, 70))):
        d.polygon([(cx, cy - r * 1.3), (cx + r, cy), (cx, cy + r * 1.3), (cx - r, cy)], fill=col)
    for i in range(4):                                                            # florões nos cantos
        px, py = (24 if i % 2 == 0 else w - 24), (28 if i < 2 else h - 28)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], outline=(176, 140, 70))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(150, 110, 50))
    a = np.asarray(img).astype(float) / 255
    a *= (0.78 + noise(max(w, h), power=1.6, seed=4)[:h, :w] * 0.45)[:, :, None]
    for y in range(h - 8, h, 2):                                                  # franjas
        a[y, ::2] = (0.69, 0.55, 0.27)
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "kover_wall", grain=0.07)


def paint_green(n=128):
    """Tinta a óleo verde de instituto, metade inferior das paredes: arranhões, lascas, sujeira embaixo."""
    y, x = np.mgrid[0:n, 0:n]
    base = np.array([0.27, 0.40, 0.31])
    shade = 0.8 + noise(n, power=2.2, seed=21) * 0.35
    img = base[None, None, :] * shade[:, :, None]
    for _ in range(9):                                                            # arranhões de encosto de cadeira
        yy = int(RNG.integers(n // 2, n - 8))
        x0 = int(RNG.integers(0, n - 40))
        img[yy:yy + 1, x0:x0 + int(RNG.integers(14, 40))] *= 1.35
    chips = noise(n, power=1.1, seed=22) > 0.93                                   # lascas mostrando o reboco
    img[chips] = np.array([0.72, 0.70, 0.62])
    img *= (1 - 0.35 * (y / n) ** 3)[:, :, None]                                  # sujeira na base
    img *= (1 + (np.random.default_rng(23).random((n, n)) - 0.5) * 0.08)[:, :, None]
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "paint_green", grain=0.02)


def parquet_square(n=144):
    """Parquet em quadrados alternados (plétenka), comum em apartamentos soviéticos."""
    img = Image.new("RGB", (n, n))
    d = ImageDraw.Draw(img)
    sq = 24
    for by in range(0, n, sq):
        for bx in range(0, n, sq):
            vertical = ((bx // sq) + (by // sq)) % 2 == 0
            for k in range(4):
                base = np.array([108, 70, 38]) * (0.8 + RNG.random() * 0.4)
                col = tuple(int(c) for c in base)
                if vertical:
                    d.rectangle([bx + k * 6, by, bx + k * 6 + 5, by + sq - 1], fill=col, outline=(40, 24, 12))
                else:
                    d.rectangle([bx, by + k * 6, bx + sq - 1, by + k * 6 + 5], fill=col, outline=(40, 24, 12))
    a = np.asarray(img).astype(float) / 255
    a *= (0.75 + noise(n, power=2.0, seed=31) * 0.4)[:, :, None]
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "parquet_square", grain=0.05)


def wallpaper_patch():
    """Papel de parede que ficou intacto onde havia o retrato (retirado em 1991): mais claro, com sombra e prego."""
    w, h = 64, 84
    y, x = np.mgrid[0:h, 0:w]
    stripe = ((x // 8) % 2).astype(float)
    motif = ((x % 16 == 8) & (y % 16 == 8)).astype(float)
    shade = 1.0 + stripe * 0.10 + motif * 0.14
    img = np.array([0.50, 0.55, 0.40])[None, None, :] * shade[:, :, None]
    img[:2, :] *= 0.55
    img[:, :2] *= 0.6
    img[-1:, :] *= 1.2
    img[2:5, w // 2 - 1:w // 2 + 2] = (0.10, 0.09, 0.08)                          # prego e furo
    img[5:16, w // 2] = (0.38, 0.36, 0.30)                                        # marca do fio
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "wallpaper_patch", grain=0.03)


def lampshade():
    w, h = 64, 32
    y, x = np.mgrid[0:h, 0:w]
    pleat = 0.78 + 0.22 * ((x % 4) < 2)
    img = np.array([0.88, 0.70, 0.42])[None, None, :] * pleat[:, :, None]
    img[-3:, ::3] = (0.45, 0.30, 0.16)                                            # franjas
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "lampshade", grain=0.05)


def brass():
    n = 64
    y, x = np.mgrid[0:n, 0:n]
    img = np.array([0.72, 0.52, 0.20])[None, None, :] * (0.7 + 0.5 * np.abs(np.sin(x / n * np.pi * 3)))[:, :, None]
    img *= (0.8 + noise(n, power=2.0, seed=41) * 0.3)[:, :, None]
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "brass", grain=0.05)


def black_cloth():
    n = 64
    y, x = np.mgrid[0:n, 0:n]
    img = np.array([0.07, 0.07, 0.08])[None, None, :] * (0.7 + 0.5 * (np.sin(x / 3.5) > 0.2))[:, :, None]
    img *= (0.8 + noise(n, power=1.8, seed=42) * 0.4)[:, :, None]
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "black_cloth", grain=0.05)


def tulle():
    n = 64
    y, x = np.mgrid[0:n, 0:n]
    img = np.array([0.85, 0.86, 0.80])[None, None, :] * (0.7 + 0.3 * (((x + y) % 3) == 0))[:, :, None]
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "tulle", grain=0.03)


def concrete(n=128):
    """Concreto industrial: manchas, rachaduras e óleo."""
    y, x = np.mgrid[0:n, 0:n]
    base = np.array([0.30, 0.30, 0.31])
    img = base[None, None, :] * (0.7 + noise(n, power=2.0, seed=51) * 0.5)[:, :, None]
    stain = np.clip(noise(n, power=2.6, seed=52) - 0.62, 0, 1)
    img *= (1 - stain * 1.4)[:, :, None]
    r = np.random.default_rng(53)
    for _ in range(3):                                                           # rachaduras
        px, py = int(r.integers(0, n)), int(r.integers(0, n))
        for _ in range(60):
            img[py % n, px % n] *= 0.35
            px += int(r.integers(-1, 2)) + 1
            py += int(r.integers(-1, 2))
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "concrete", grain=0.05)


def hazard():
    w, h = 64, 16
    y, x = np.mgrid[0:h, 0:w]
    stripe = (((x + y) // 6) % 2).astype(float)
    img = np.stack([0.85 * stripe + 0.05, 0.72 * stripe + 0.05, 0.10 * stripe + 0.05], axis=-1)
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "hazard", grain=0.06)


def sign_exit():
    w, h = 48, 20
    img = Image.new("RGB", (w, h), (30, 110, 60))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(220, 235, 220))
    text(d, (w // 2 + 4, h // 2), "ВЫХОД", 8, (235, 245, 235), BOLD, "mm")
    d.polygon([(6, 10), (13, 5), (13, 15)], fill=(235, 245, 235))
    finish(img, "sign_exit", grain=0.05)


def sign_warn():
    w, h = 48, 32
    img = Image.new("RGB", (w, h), (170, 30, 25))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(240, 220, 180))
    text(d, (w // 2, 11), "ВНИМАНИЕ", 8, (245, 235, 215), BOLD, "mm")
    text(d, (w // 2, 22), "ОПАСНО", 7, (245, 235, 215), BOLD, "mm")
    finish(img, "sign_warn", grain=0.06)


def screen_lethe():
    w, h = 64, 48
    img = Image.new("RGB", (w, h), (8, 28, 16))
    d = ImageDraw.Draw(img)
    for i, (s, c) in enumerate((("ЛЕТА  v2.1", (120, 255, 150)), ("ОПЕРАТОР: —", (255, 200, 90)),
                                 ("ЦИКЛ: ОСТЫВАНИЕ", (120, 255, 150)), ("ДАННЫЕ: СБОЙ", (255, 90, 80)))):
        text(d, (3, 4 + i * 10), s, 6, c, REG)
    d.rectangle([3, 42, 8, 45], fill=(120, 255, 150))                              # cursor
    a = np.asarray(img).astype(float) / 255
    a[::2] *= 0.8                                                                  # linhas de varredura
    finish(Image.fromarray((a * 255).astype(np.uint8)), "screen_lethe", grain=0.05)


def missile_skin():
    w, h = 128, 64
    img = Image.new("RGB", (w, h), (84, 92, 58))
    d = ImageDraw.Draw(img)
    for x in (0, 40, 88):
        d.line([x, 0, x, h], fill=(50, 56, 34))                                    # emendas dos painéis
    a = np.asarray(img).astype(float) / 255
    a *= (0.75 + noise(max(w, h), power=2.0, seed=61)[:h, :w] * 0.5)[:, :, None]
    rust = np.clip(noise(max(w, h), power=2.4, seed=62)[:h, :w] - 0.6, 0, 1)
    a = a * (1 - rust[:, :, None]) + rust[:, :, None] * np.array([0.50, 0.25, 0.10])
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "missile_skin", grain=0.05)


def missile_stencil():
    """Estêncil único do míssil (decalque): fundo da mesma tinta oliva para fundir com o casco."""
    w, h = 160, 44
    img = Image.new("RGB", (w, h), (84, 92, 58))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 20), "ЛЕТА", 30, (225, 225, 210), BOLD, "mm")
    text(d, (w // 2, 39), "№ 004", 8, (225, 225, 210), REG, "mm")
    a = np.asarray(img).astype(float) / 255
    a *= (0.8 + noise(max(w, h), power=2.0, seed=63)[:h, :w] * 0.4)[:, :, None]
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "missile_stencil", grain=0.05)


def linoleum(n=128):
    """Linóleo de cozinha soviética: marrom-avermelhado com desenho de pedras e desgaste."""
    y, x = np.mgrid[0:n, 0:n]
    base = np.array([0.40, 0.24, 0.16])
    pebbles = (noise(n, power=1.1, seed=71) > 0.55).astype(float)
    img = base[None, None, :] * (0.75 + 0.35 * pebbles)[:, :, None]
    img *= (0.8 + noise(n, power=2.2, seed=72) * 0.3)[:, :, None]
    worn = np.clip(noise(n, power=2.8, seed=73) - 0.6, 0, 1) * 2.0                 # trilha gasta
    img = img * (1 - worn[:, :, None] * 0.5) + worn[:, :, None] * np.array([0.5, 0.45, 0.35]) * 0.3
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "linoleum", grain=0.05)


def oilcloth(n=64):
    """Toalha de oleado: xadrez creme e vermelho com cerejas desbotadas e marcas de copo."""
    img = Image.new("RGB", (n, n), (225, 215, 185))
    d = ImageDraw.Draw(img)
    for i in range(0, n, 16):
        d.rectangle([i, 0, i + 7, n], fill=(190, 60, 50))
        d.rectangle([0, i, n, i + 7], fill=(210, 150, 130))
    for cx, cy in ((8, 8), (40, 24), (24, 48)):
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(150, 20, 30))
    a = np.asarray(img).astype(float) / 255
    ring = np.clip(noise(n, power=1.6, seed=74) - 0.7, 0, 1) * 1.6                 # marcas de copo
    a = a * (1 - ring[:, :, None] * 0.35)
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "oilcloth", grain=0.06)


def pic_parents():
    w, h = 72, 56
    img = Image.new("RGB", (w, h), (140, 130, 115))
    d = ImageDraw.Draw(img)
    for y in range(h):
        c = int(120 + 40 * (1 - y / h))
        d.line([0, y, w, y], fill=(c, c - 5, c - 12))
    for x0, hair, tone in ((22, (50, 40, 35), (225, 190, 165)), (48, (90, 80, 70), (225, 190, 165))):
        d.ellipse([x0 - 16, 36, x0 + 16, 80], fill=(70, 70, 80))
        d.ellipse([x0 - 8, 12, x0 + 8, 34], fill=tone)
        d.pieslice([x0 - 9, 8, x0 + 9, 28], 180, 360, fill=hair)
        d.point([x0 - 4, 22], fill=(40, 30, 25))
        d.point([x0 + 4, 22], fill=(40, 30, 25))
        d.line([x0 - 3, 29, x0 + 3, 29], fill=(150, 80, 80))
    d.polygon([(w, 0), (w - 18, 0), (w, 18)], fill=(40, 30, 25))                    # canto queimado
    d.rectangle([0, 0, w - 1, h - 1], outline=(235, 225, 200))
    finish(img, "pic_parents", grain=0.07, sepia=True)


def calendar_1991():
    w, h = 48, 64
    img = Image.new("RGB", (w, h), (238, 232, 215))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 16], fill=(180, 35, 30))
    text(d, (w // 2, 8), "ИЮНЬ", 9, (245, 235, 220), BOLD, "mm")
    text(d, (w // 2, 22), "1991", 6, (40, 35, 35), BOLD, "mm")
    for i, n_ in enumerate(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]):
        text(d, (3 + i * 6, 27), n_[0], 5, (180, 35, 30) if i > 4 else (60, 55, 55), REG)
    day = 1
    for r in range(5):
        for c in range(7):
            if (r == 0 and c < 5) or day > 30:
                continue
            x, y = 3 + c * 6, 34 + r * 6
            text(d, (x, y), str(day), 4, (60, 55, 55), REG)
            if day == 19:                                                              # dia marcado: o jantar
                d.ellipse([x - 2, y - 1, x + 5, y + 6], outline=(180, 35, 30))
            day += 1
    finish(img, "calendar_1991", grain=0.05)


def emblem():
    n = 48
    img = Image.new("RGB", (n, n), (30, 34, 42))
    d = ImageDraw.Draw(img)
    d.ellipse([3, 3, n - 4, n - 14], outline=(210, 180, 90))
    pts = []
    for i in range(10):
        rr = 12 if i % 2 == 0 else 5
        a = -np.pi / 2 + i * np.pi / 5
        pts.append((n / 2 + rr * np.cos(a), 17 + rr * np.sin(a)))
    d.polygon(pts, fill=(200, 40, 35))
    text(d, (n // 2, n - 7), "КОСМОС", 8, (210, 180, 90), BOLD, "mm")
    finish(img, "emblem", grain=0.06)


def screen_log():
    w, h = 64, 48
    img = Image.new("RGB", (w, h), (8, 24, 14))
    d = ImageDraw.Draw(img)
    rows = (("ЖУРНАЛ ДОСТУПА", (120, 255, 150)), ("22:58 ВОЛКОВ Б.", (120, 255, 150)), ("23:07 ВХОД: Б.В.", (255, 200, 90)),
            ("23:15 УДАЛЕНО!", (255, 90, 80)), ("   ПОЛЬЗОВ.: Б.В.", (255, 90, 80)), ("23:16 ПУСТО", (120, 255, 150)))
    for i, (s, c) in enumerate(rows):
        text(d, (2, 2 + i * 7), s, 5, c, REG)
    a = np.asarray(img).astype(float) / 255
    a[::2] *= 0.8
    finish(Image.fromarray((a * 255).astype(np.uint8)), "screen_log", grain=0.05)


def note_code():
    w, h = 20, 20
    img = Image.new("RGB", (w, h), (235, 220, 110))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 6), "4-8-2-1", 5, (40, 40, 90), BOLD, "mm")
    text(d, (w // 2, 13), "стереть", 5, (150, 30, 30), REG, "mm")
    finish(img, "note_code", grain=0.05)


def label_volkov():
    w, h = 40, 14
    img = Image.new("RGB", (w, h), (225, 215, 185))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 4), "ВОЛКОВ М. И.", 5, (40, 35, 35), BOLD, "mm")
    text(d, (w // 2, 10), "ИЗЪЯТО", 5, (170, 30, 30), BOLD, "mm")
    finish(img, "label_volkov", grain=0.05)


def floppy_label():
    w, h = 24, 20
    img = Image.new("RGB", (w, h), (225, 220, 205))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 5), "ЛЕТА", 7, (30, 30, 110), BOLD, "mm")
    text(d, (w // 2, 13), "копия 1", 5, (120, 40, 40), REG, "mm")
    finish(img, "floppy_label", grain=0.05)


def blackboard():
    w, h = 64, 40
    img = Image.new("RGB", (w, h), (28, 44, 36))
    d = ImageDraw.Draw(img)
    ch = (215, 220, 205)
    for i, s in enumerate(("ψ(t)=Σ aₙe^{-iEt}", "dS/dt < 0", "T→0  ⇒  ρ→1", "ΔI = −ΔM", "Σ M = 0")):
        text(d, (3, 3 + i * 6), s, 5, ch, REG)
    d.ellipse([46, 24, 58, 36], outline=(240, 240, 225))                          # o símbolo do vazio ∅
    d.line([45, 37, 59, 23], fill=(240, 240, 225))
    d.line([2, 36, 30, 37], fill=(150, 160, 150))
    finish(img, "blackboard", grain=0.07)


def proto_panel():
    w, h = 40, 32
    img = Image.new("RGB", (w, h), (70, 74, 78))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 4, 32, 28], fill=(150, 115, 50), outline=(210, 170, 80))
    text(d, (20, 16), "ЛЕТА", 6, (60, 40, 15), BOLD, "mm")
    d.rectangle([2, 26, 38, 30], fill=(215, 205, 160))                              # fita crepe
    text(d, (20, 28), "НЕ ТРОГАТЬ", 4, (150, 30, 30), BOLD, "mm")
    finish(img, "proto_panel", grain=0.07)


def notebook_names():
    w, h = 24, 32
    img = Image.new("RGB", (w, h), (225, 215, 185))
    d = ImageDraw.Draw(img)
    for i, s in enumerate(("Борис", "Сергей", "Ирина", "Миша", "Лена")):
        y = 4 + i * 5
        text(d, (3, y), s, 4, (40, 40, 100), REG)
        if s != "Лена":
            d.line([2, y + 2, 21, y + 2], fill=(150, 30, 30))                       # nomes riscados; só o dela fica
    finish(img, "notebook_names", grain=0.05)


def tv_swans():
    w, h = 48, 36
    img = Image.new("RGB", (w, h), (30, 38, 70))
    d = ImageDraw.Draw(img)
    for i in range(h):                                                              # palco: azul de lago, mais claro ao fundo
        d.line([0, i, w, i], fill=(30 + i, 45 + i, 80 + i))
    for x0 in (14, 24, 34):                                                         # bailarinas de tutu branco
        d.ellipse([x0 - 1, 12, x0 + 1, 14], fill=(235, 220, 205))
        d.polygon([(x0, 15), (x0 - 4, 21), (x0 + 4, 21)], fill=(240, 240, 245))
        d.line([x0 - 1, 21, x0 - 1, 27], fill=(235, 220, 205))
        d.line([x0 + 1, 21, x0 + 1, 27], fill=(235, 220, 205))
    a = np.asarray(img).astype(float) / 255
    a[::2] *= 0.82
    a += (RNG.random(a.shape) - 0.5) * 0.10                                          # chuvisco de sinal ruim
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "tv_swans", grain=0.04)


def lightbox_plans():
    w, h = 48, 32
    img = Image.new("RGB", (w, h), (210, 225, 240))
    d = ImageDraw.Draw(img)
    ln = (40, 70, 140)
    d.rectangle([4, 4, w - 5, h - 5], outline=ln)
    d.ellipse([10, 10, 20, 22], outline=ln)
    d.line([20, 16, 40, 16], fill=ln)
    d.line([20, 12, 36, 12], fill=ln)
    d.line([20, 20, 36, 20], fill=ln)
    text(d, (w // 2, 27), "ЛЕТА / ЧЕРТЁЖ 4", 4, ln, REG, "mm")
    finish(img, "lightbox_plans", grain=0.04)


def champagne_label():
    w, h = 16, 24
    img = Image.new("RGB", (w, h), (40, 70, 40))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 6, w - 2, 17], fill=(225, 205, 130))
    text(d, (w // 2, 11), "ШАМП.", 4, (120, 30, 30), BOLD, "mm")
    finish(img, "champagne_label", grain=0.05)


def notebook_misha():
    w, h = 24, 32
    img = Image.new("RGB", (w, h), (225, 215, 185))
    d = ImageDraw.Draw(img)
    for i in range(7):                                                              # "Миша" escrito e reescrito, cada vez mais torto
        text(d, (2 + (i % 2) * 2, 2 + i * 4), "Миша", 4, (40, 40, 100), REG)
    finish(img, "notebook_misha", grain=0.05)


def card_lena():
    w, h = 24, 16
    img = Image.new("RGB", (w, h), (232, 224, 200))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 5), "Серёжа,", 5, (50, 40, 110), REG, "mm")
    text(d, (w // 2, 11), "помни обо мне", 4, (50, 40, 110), REG, "mm")
    finish(img, "card_lena", grain=0.05)


def frost():
    n = 32
    base = noise(n, 1.4, seed=5)
    img = np.zeros((n, n, 3))
    img[..., 0] = 0.55 + 0.25 * base
    img[..., 1] = 0.70 + 0.22 * base
    img[..., 2] = 0.88 + 0.12 * base
    for _ in range(14):                                                             # cristais de gelo: riscos ramificados
        x, y = int(RNG.integers(0, n)), int(RNG.integers(0, n))
        for _ in range(int(RNG.integers(4, 10))):
            img[y % n, x % n] = 1.0
            x += int(RNG.integers(-1, 2)); y += int(RNG.integers(-1, 2))
    finish(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)), "frost", grain=0.03)


def poster_slogan():
    w, h = 64, 40
    img = Image.new("RGB", (w, h), (150, 30, 28))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, w - 3, h - 3], outline=(225, 200, 150))
    d.ellipse([22, 6, 42, 24], outline=(225, 200, 150))                                  # foice e martelo estilizados
    d.line([26, 20, 38, 10], fill=(225, 200, 150), width=2)
    d.line([30, 10, 38, 20], fill=(225, 200, 150), width=1)
    text(d, (w // 2, 31), "СЛАВА ТРУДУ!", 6, (235, 225, 195), BOLD, "mm")
    finish(img, "poster_slogan", grain=0.10)                                              # cartaz velho e desbotado


def poster_safety():
    w, h = 40, 52
    img = Image.new("RGB", (w, h), (235, 200, 40))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(20, 20, 20), width=2)
    d.polygon([(20, 6), (36, 32), (4, 32)], outline=(20, 20, 20), width=2, fill=(235, 200, 40))
    d.polygon([(22, 14), (16, 24), (21, 24), (18, 31), (27, 20), (22, 20)], fill=(20, 20, 20))     # raio
    text(d, (w // 2, 38), "ОСТОРОЖНО!", 5, (20, 20, 20), BOLD, "mm")
    text(d, (w // 2, 46), "ВЫС. НАПРЯЖЕНИЕ", 3, (20, 20, 20), BOLD, "mm")
    finish(img, "poster_safety", grain=0.08)


def sign_nosmoke():
    w, h = 32, 32
    img = Image.new("RGB", (w, h), (235, 232, 222))
    d = ImageDraw.Draw(img)
    d.ellipse([3, 3, 28, 28], outline=(190, 30, 30), width=3)
    d.line([6, 25, 25, 6], fill=(190, 30, 30), width=3)
    d.rectangle([9, 15, 21, 17], fill=(40, 40, 40))
    finish(img, "sign_nosmoke", grain=0.06)


def fire_board():
    w, h = 40, 56
    img = Image.new("RGB", (w, h), (170, 30, 25))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 5), "ПОЖАРНЫЙ", 5, (240, 235, 215), BOLD, "mm")
    text(d, (w // 2, 11), "ЩИТ", 6, (240, 235, 215), BOLD, "mm")
    for i, c in enumerate(((190, 190, 190), (200, 140, 40), (110, 70, 40))):            # ferramentas: pá, balde, machado
        d.rectangle([5 + i * 12, 20, 11 + i * 12, 50], fill=c)
    finish(img, "fire_board", grain=0.07)


def pass_card():
    w, h = 32, 20
    img = Image.new("RGB", (w, h), (215, 205, 170))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 6], fill=(160, 40, 35))
    text(d, (w // 2, 3), "ПРОПУСК", 5, (240, 230, 200), BOLD, "mm")
    d.rectangle([3, 9, 11, 17], fill=(130, 120, 110))                                      # foto
    text(d, (21, 11), "КОСМОС", 4, (40, 40, 40), BOLD, "mm")
    d.line([14, 15, 28, 15], fill=(90, 80, 70))
    finish(img, "pass_card", grain=0.06)


def ruble_note():
    w, h = 40, 20
    img = Image.new("RGB", (w, h), (170, 190, 150))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(60, 90, 60))
    text(d, (w // 2, 5), "БИЛЕТ БАНКА РОССИИ", 3, (50, 70, 50), BOLD, "mm")
    text(d, (w // 2, 12), "1000", 8, (45, 70, 45), BOLD, "mm")
    text(d, (w // 2, 17), "РУБЛЕЙ", 3, (50, 70, 50), BOLD, "mm")
    finish(img, "ruble_note", grain=0.06)


def talon():
    w, h = 24, 24
    img = Image.new("RGB", (w, h), (225, 205, 170))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(120, 40, 40))
    text(d, (w // 2, 5), "ТАЛОН", 6, (120, 30, 30), BOLD, "mm")
    text(d, (w // 2, 12), "НА ВОДКУ", 4, (60, 50, 50), BOLD, "mm")
    text(d, (w // 2, 19), "0,5 л", 5, (60, 50, 50), REG, "mm")
    finish(img, "talon", grain=0.07)


def vodka_label():
    w, h = 20, 28
    img = Image.new("RGB", (w, h), (225, 220, 200))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 6], fill=(150, 30, 30))
    text(d, (w // 2, 3), "ВОДКА", 5, (240, 230, 205), BOLD, "mm")
    text(d, (w // 2, 12), "РУССКАЯ", 4, (30, 40, 90), BOLD, "mm")
    d.ellipse([6, 16, 14, 24], outline=(150, 30, 30))
    finish(img, "vodka_label", grain=0.06)


def prima_pack():
    w, h = 20, 28
    img = Image.new("RGB", (w, h), (200, 160, 40))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 9), "ПРИМА", 6, (140, 30, 30), BOLD, "mm")
    d.line([2, 15, w - 3, 15], fill=(140, 30, 30))
    text(d, (w // 2, 21), "без фильтра", 3, (70, 40, 30), REG, "mm")
    finish(img, "prima_pack", grain=0.06)


def tv_guide():
    w, h = 28, 36
    img = Image.new("RGB", (w, h), (225, 220, 200))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 4), "ПРОГРАММА", 4, (40, 40, 40), BOLD, "mm")
    text(d, (w // 2, 9), "ПЕРЕДАЧ", 4, (40, 40, 40), BOLD, "mm")
    for i, t in enumerate(("18.00 НОВОСТИ", "19.30 БАЛЕТ", "21.00 ВРЕМЯ", "22.30 ФИЛЬМ")):
        text(d, (2, 14 + i * 5), t, 3, (60, 60, 70), REG)
    finish(img, "tv_guide", grain=0.06)


def conspiracy_board():
    w, h = 80, 56
    img = Image.new("RGB", (w, h), (120, 88, 56))
    d = ImageDraw.Draw(img)
    pts = []
    for (x, y, label) in ((8, 6, "БОРИС?"), (34, 4, "СЕРГЕЙ"), (58, 8, "ИРИНА"), (10, 32, "МИША?"), (40, 34, "4-8-2-1"), (62, 34, "КТО Я?")):
        d.rectangle([x, y, x + 15, y + 15], fill=(225, 220, 205))                           # polaroide / cartão
        d.rectangle([x + 2, y + 2, x + 13, y + 10], fill=(110, 105, 100))
        text(d, (x + 8, y + 13), label, 3, (60, 20, 20), BOLD, "mm")
        pts.append((x + 8, y + 1))
    for a, b in ((0, 1), (1, 2), (0, 3), (3, 4), (2, 5), (4, 5), (1, 4)):                  # fios vermelhos ligando tudo
        d.line([pts[a], pts[b]], fill=(190, 30, 30), width=1)
    for p_ in pts:
        d.rectangle([p_[0] - 1, p_[1] - 1, p_[0] + 1, p_[1] + 1], fill=(230, 220, 60))     # alfinetes
    finish(img, "conspiracy_board", grain=0.07)


def newspaper_pravda():
    w, h = 32, 40
    img = Image.new("RGB", (w, h), (215, 205, 180))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 8], fill=(160, 35, 30))
    text(d, (w // 2, 4), "ПРАВДА", 6, (235, 225, 195), BOLD, "mm")
    for i in range(8):
        d.line([2, 12 + i * 3, w - 3 - (i % 3) * 4, 12 + i * 3], fill=(70, 65, 60))
    d.rectangle([2, 31, 14, 38], fill=(120, 115, 105))
    finish(img, "newspaper_pravda", grain=0.07)


def facade():
    """Fachada de prédio de painéis (khrushchyovka/brezhnevka): 4 colunas x 4 andares de janelas com cortinas, varandas e manchas."""
    n = 64
    img = Image.new("RGB", (n, n), (150, 148, 135))
    d = ImageDraw.Draw(img)
    for r_ in range(4):
        for c_ in range(4):
            x0, y0 = c_ * 16 + 3, r_ * 16 + 3
            d.rectangle([x0, y0, x0 + 9, y0 + 11], fill=(35, 45, 60), outline=(205, 200, 185))
            d.line([x0 + 5, y0, x0 + 5, y0 + 11], fill=(205, 200, 185))
            if (r_ * 5 + c_ * 3) % 4 == 0:
                d.rectangle([x0 + 1, y0 + 1, x0 + 4, y0 + 10], fill=(170, 130, 90))             # cortina
            d.rectangle([x0 - 1, y0 + 12, x0 + 10, y0 + 13], fill=(110, 108, 100))             # peitoril/varanda
        d.line([0, r_ * 16, n, r_ * 16], fill=(120, 118, 110))                                  # junta dos painéis
    for x in range(0, n, 16):
        d.line([x, 0, x, n], fill=(125, 123, 115))
    finish(img, "facade", grain=0.10)


def facade_emit():
    n = 64
    img = Image.new("RGB", (n, n), (0, 0, 0))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(77)
    for r_ in range(4):
        for c_ in range(4):
            if rng.random() < 0.35:
                x0, y0 = c_ * 16 + 3, r_ * 16 + 3
                d.rectangle([x0 + 1, y0 + 1, x0 + 8, y0 + 10], fill=(255, 190, 90))
    finish(img, "facade_emit", grain=0.0, levels=8)


def banner_soviets():
    w, h = 96, 16
    img = Image.new("RGB", (w, h), (165, 25, 25))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 8), "ВСЯ ВЛАСТЬ СОВЕТАМ!", 9, (240, 230, 205), BOLD, "mm")
    finish(img, "banner_soviets", grain=0.08)


def tv_news():
    w, h = 48, 36
    img = Image.new("RGB", (w, h), (28, 36, 60))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 26, w, h], fill=(150, 25, 25))
    text(d, (w // 2, 31), "ВЕСТИ · СРОЧНО", 5, (240, 235, 215), BOLD, "mm")
    d.ellipse([19, 6, 29, 16], fill=(190, 160, 135))                                          # apresentador
    d.rectangle([15, 16, 33, 26], fill=(40, 40, 50))
    a = np.asarray(img).astype(float) / 255
    a[::2] *= 0.8
    a += (RNG.random(a.shape) - 0.5) * 0.08
    finish(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)), "tv_news", grain=0.03)


def prontuario():
    w, h = 24, 32
    img = Image.new("RGB", (w, h), (230, 225, 205))
    d = ImageDraw.Draw(img)
    text(d, (w // 2, 4), "ИСТОРИЯ", 4, (40, 40, 60), BOLD, "mm")
    text(d, (w // 2, 9), "БОЛЕЗНИ", 4, (40, 40, 60), BOLD, "mm")
    d.line([2, 12, w - 3, 12], fill=(90, 90, 100))
    text(d, (w // 2, 17), "ПЕТРОВ А. И.", 4, (30, 30, 110), BOLD, "mm")
    text(d, (3, 22), "1958 г.р.", 3, (70, 70, 80), REG)
    text(d, (3, 27), "ТРАВМА / АМНЕЗИЯ", 3, (150, 30, 30), BOLD)
    finish(img, "prontuario", grain=0.05)


def passport():
    w, h = 20, 28
    img = Image.new("RGB", (w, h), (150, 25, 30))
    d = ImageDraw.Draw(img)
    d.ellipse([5, 5, 15, 15], outline=(220, 190, 90))
    text(d, (w // 2, 20), "ПАСПОРТ", 4, (225, 195, 100), BOLD, "mm")
    text(d, (w // 2, 25), "РФ", 4, (225, 195, 100), BOLD, "mm")
    finish(img, "passport", grain=0.07)


def autumn_view():
    w, h = 48, 40
    img = Image.new("RGB", (w, h), (170, 185, 195))
    d = ImageDraw.Draw(img)
    for i in range(h):
        d.line([0, i, w, i], fill=(150 + i // 3, 170 + i // 4, 185))
    d.rectangle([0, 30, w, h], fill=(110, 95, 70))
    for x0 in (8, 22, 38):
        d.rectangle([x0, 14, x0 + 2, 32], fill=(60, 45, 35))
        for _ in range(26):
            lx, ly = x0 + int(RNG.integers(-8, 9)), 8 + int(RNG.integers(0, 14))
            d.rectangle([lx, ly, lx + 2, ly + 2], fill=tuple(int(v) for v in RNG.choice([(215, 150, 40), (190, 100, 30), (225, 190, 60), (150, 70, 30)])))
    finish(img, "autumn_view", grain=0.05)


def ward_plate():
    w, h = 24, 12
    img = Image.new("RGB", (w, h), (225, 225, 215))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(40, 70, 110))
    text(d, (w // 2, 4), "ПАЛАТА 7", 5, (40, 70, 110), BOLD, "mm")
    text(d, (w // 2, 9), "ТИХО!", 3, (150, 30, 30), BOLD, "mm")
    finish(img, "ward_plate", grain=0.05)


def pic_brothers():
    w, h = 40, 32
    img = Image.new("RGB", (w, h), (205, 210, 215))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 22, w, h], fill=(235, 238, 240))                                         # neve
    for x0, hh, col in ((12, 14, (70, 60, 55)), (24, 9, (60, 70, 90))):                        # dois garotos: o mais velho e o menor
        d.ellipse([x0 - 3, 22 - hh - 4, x0 + 3, 22 - hh + 2], fill=(200, 160, 130))
        d.rectangle([x0 - 3, 22 - hh + 2, x0 + 3, 24], fill=col)
    d.line([16, 14, 22, 17], fill=(60, 55, 50))
    finish(img, "pic_brothers", grain=0.08, sepia=True)


if __name__ == "__main__":
    ALL = {f.__name__: f for f in (linoleum, oilcloth, pic_parents, calendar_1991, concrete, hazard, sign_exit, sign_warn, screen_lethe, missile_skin, missile_stencil, emblem, pic_lena, pic_team, poster_space, diploma, calendar_1992, newspaper, door_plate, icon, papirosy,
               tape_label, folder_secret, kover_wall, paint_green, parquet_square, wallpaper_patch, lampshade,
               brass, black_cloth, tulle, screen_log, note_code, label_volkov, floppy_label, blackboard, proto_panel, notebook_names, tv_swans, lightbox_plans, champagne_label, notebook_misha, card_lena, frost, poster_slogan, poster_safety, sign_nosmoke, fire_board, pass_card, ruble_note, talon, vodka_label, prima_pack, tv_guide, conspiracy_board, newspaper_pravda, facade, facade_emit, banner_soviets, tv_news, prontuario, passport, autumn_view, ward_plate, pic_brothers)}
    import sys
    for name in sys.argv[1:] or ALL:   # sem argumentos gera tudo; com nomes, só esses
        ALL[name]()
    print("imagens russas em", os.path.abspath(OUT))
