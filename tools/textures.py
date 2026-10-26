"""Gera as texturas pixeladas do jogo (tileáveis) em art/tex/*.png.

Uso: python3 tools/textures.py
Estilo: paleta suja e dessaturada, grão, manchas de umidade, quantizado para parecer PS1/Obra Dinn.
"""
import os
import numpy as np
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "art", "tex")
os.makedirs(OUT, exist_ok=True)
N = 128


def noise(n=N, power=2.0, seed=0):
    """Ruído suave tileável (filtro 1/f^power no domínio da frequência), em [0,1]."""
    a = np.random.default_rng(seed).standard_normal((n, n))
    f = np.fft.fft2(a)
    k = np.sqrt(np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2)
    k[0, 0] = 1
    f = f / k ** power
    f[0, 0] = 0
    o = np.real(np.fft.ifft2(f))
    return (o - o.min()) / (o.max() - o.min())


def grain(n=N, seed=1, amt=0.06):
    return 1 + (np.random.default_rng(seed).random((n, n)) - 0.5) * 2 * amt


def save(name, rgb, levels=20):
    """rgb: array HxWx3 em [0,1]. Quantiza e grava PNG."""
    a = np.clip(rgb, 0, 1)
    a = np.round(a * levels) / levels
    Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))


def tint(base, shade):
    return np.array(base)[None, None, :] * shade[:, :, None]


def wallpaper():
    y, x = np.mgrid[0:N, 0:N]
    stripe = ((x // 8) % 2).astype(float)
    motif = ((x % 16 == 8) & (y % 16 == 8)).astype(float) + ((x % 16 == 7) & (y % 16 == 9)).astype(float) * 0.5
    shade = 0.78 + stripe * 0.08 + motif * 0.12
    stain = noise(seed=3, power=2.6)
    damp = np.clip((stain - 0.55) * 2.5, 0, 1) * 0.35
    shade = shade * grain(seed=4) * (1 - damp)
    base = (0.34, 0.38, 0.27)
    save("wallpaper", tint(base, shade))


def parquet():
    y, x = np.mgrid[0:N, 0:N]
    plank_w, plank_h = 16, 64
    row = x // plank_w
    off = (row % 2) * (plank_h // 2)
    cell = ((y + off) // plank_h)
    rng = np.random.default_rng(5)
    tone = 0.75 + rng.random((N // plank_w + 1, N // plank_h + 2))[row % (N // plank_w + 1), cell % (N // plank_h + 2)] * 0.35
    g = noise(seed=6, power=1.2)
    fiber = 0.9 + 0.2 * np.sin((x + g * 12) * 0.9)
    seam = ((x % plank_w == 0) | ((y + off) % plank_h == 0)).astype(float)
    shade = tone * fiber * grain(seed=7, amt=0.05) * (1 - seam * 0.5)
    shade *= 1 - np.clip(noise(seed=8, power=2.4) - 0.6, 0, 1) * 0.8
    save("parquet", tint((0.42, 0.27, 0.15), shade))


def plaster():
    s = 0.8 * (0.8 + noise(seed=9, power=1.8) * 0.4) * grain(seed=10, amt=0.04)
    save("plaster", tint((0.62, 0.60, 0.53), s))


def wood_dark():
    y, x = np.mgrid[0:N, 0:N]
    g = noise(seed=11, power=1.6)
    s = 0.7 + 0.3 * np.sin((y + g * 24) * 0.5) * 0.5 + 0.2 * g
    save("wood_dark", tint((0.30, 0.18, 0.10), s * grain(seed=12)))


def leather():
    s = 0.7 + noise(seed=13, power=1.4) * 0.5
    crack = (noise(seed=14, power=3.0) > 0.78).astype(float) * 0.35
    save("leather", tint((0.32, 0.12, 0.09), (s - crack) * grain(seed=15)))


def metal():
    scratch = (np.random.default_rng(16).random((N, N)) > 0.985).astype(float) * 0.25
    s = 0.75 + noise(seed=17, power=2.2) * 0.3 + scratch
    rust = np.clip(noise(seed=18, power=2.5) - 0.62, 0, 1)
    img = tint((0.36, 0.40, 0.42), s * grain(seed=19))
    img = img * (1 - rust[:, :, None]) + rust[:, :, None] * np.array([0.45, 0.22, 0.10])
    save("metal", img)


def paper():
    s = 0.85 + noise(seed=20, power=2.0) * 0.2
    rng = np.random.default_rng(21)
    txt = np.zeros((N, N))
    for r in range(8, N, 8):
        x0 = 6
        while x0 < N - 8:
            w = int(rng.integers(3, 9))
            txt[r:r + 2, x0:x0 + w] = 0.55
            x0 += w + 3
    save("paper", tint((0.78, 0.74, 0.60), s * (1 - txt * 0.8)))


def rug():
    y, x = np.mgrid[0:N, 0:N]
    d = np.abs(((x % 32) - 16)) + np.abs(((y % 32) - 16))
    lattice = ((d % 8) < 3).astype(float)
    border = ((x < 8) | (x > N - 9) | (y < 8) | (y > N - 9)).astype(float)
    base = np.array([0.42, 0.09, 0.08])
    gold = np.array([0.62, 0.48, 0.20])
    m = np.clip(lattice * 0.6 + border, 0, 1)[:, :, None]
    img = base * (1 - m) + gold * m
    save("rug", img * grain(seed=22, amt=0.08)[:, :, None] * (0.8 + noise(seed=23) * 0.3)[:, :, None])


def books():
    """Faixa 128x32: lombadas coloridas (cada 4px uma coluna) para estantes."""
    rng = np.random.default_rng(24)
    pal = [(0.45, 0.10, 0.08), (0.10, 0.22, 0.32), (0.30, 0.30, 0.12), (0.35, 0.22, 0.10),
           (0.12, 0.28, 0.16), (0.55, 0.50, 0.35), (0.25, 0.10, 0.25), (0.20, 0.20, 0.22)]
    img = np.zeros((32, N, 3))
    x = 0
    while x < N:
        w = int(rng.integers(3, 8))
        c = np.array(pal[int(rng.integers(len(pal)))]) * (0.8 + rng.random() * 0.4)
        img[:, x:x + w] = c
        img[4:6, x:x + w] = c * 1.5
        img[26:28, x:x + w] = c * 1.5
        img[:, x] *= 0.4
        x += w
    save("books", np.clip(img * grain(N, seed=25, amt=0.05)[:32, :, None], 0, 1))


def chessboard():
    y, x = np.mgrid[0:64, 0:64]
    sq = (((x // 8) + (y // 8)) % 2).astype(float)
    a = np.array([0.80, 0.72, 0.55]) * sq[:, :, None] + np.array([0.20, 0.10, 0.06]) * (1 - sq)[:, :, None]
    save("chessboard", a * grain(64, seed=26, amt=0.05)[:, :, None])


def crt():
    y, x = np.mgrid[0:64, 0:64]
    scan = 0.7 + 0.3 * ((y % 2) == 0)
    s = (0.5 + noise(64, seed=27, power=1.5) * 0.5) * scan
    img = np.stack([s * 0.15, s * 0.75, s * 0.35], axis=-1)
    for r in (10, 18, 26, 34):  # linhas de "texto" do terminal
        img[r:r + 2, 6:6 + int(20 + 20 * ((r * 7) % 3 / 3))] = (0.5, 1.0, 0.6)
    save("crt", img)


def cloth(name, base, seed):
    y, x = np.mgrid[0:N, 0:N]
    knit = 0.85 + 0.15 * (((x + y) % 4) < 2)
    save(name, tint(base, knit * (0.85 + noise(seed=seed, power=1.5) * 0.3) * grain(seed=seed + 1, amt=0.05)))


def hair(name, base, seed):
    save(name, tint(base, 0.7 + noise(seed=seed, power=1.2) * 0.5))


def face(name, skin, brow, eye=(0.12, 0.10, 0.08), mouth=(0.45, 0.22, 0.20), age=0.0, seed=0):
    """Rosto 64x64 pintado: a coluna da direita é pele lisa (usada pelas outras faces da cabeça)."""
    img = Image.new("RGB", (64, 64), tuple(int(c * 255) for c in skin))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    c = lambda t: tuple(int(v * 255) for v in t)
    shade = tuple(int(v * 255 * 0.78) for v in skin)
    d.rectangle([0, 52, 63, 63], fill=shade)               # sombra do queixo
    d.rectangle([0, 0, 63, 6], fill=shade)                 # sombra da testa/cabelo
    d.rectangle([12, 22, 24, 24], fill=c(brow))            # sobrancelhas
    d.rectangle([38, 22, 50, 24], fill=c(brow))
    for ex in (14, 38):                                    # olhos
        d.rectangle([ex, 28, ex + 10, 33], fill=(235, 230, 215))
        d.rectangle([ex + 3, 28, ex + 7, 33], fill=c(eye))
        d.rectangle([ex, 34, ex + 10, 35], fill=shade)
    d.rectangle([29, 36, 34, 46], fill=shade)              # nariz
    d.rectangle([22, 50, 41, 52], fill=c(mouth))           # boca
    for _ in range(int(age * 14)):                         # rugas / marcas
        x0 = int(rng.integers(6, 56))
        d.line([x0, 40, x0 + 3, 44], fill=shade)
    d.rectangle([60, 0, 63, 63], fill=tuple(int(v * 255) for v in skin))  # coluna lisa
    img.save(os.path.join(OUT, name + ".png"))


def face_states(prefix, skin, brow, hair_col, age=0.8, seed=1, eye=(0.12, 0.10, 0.08), mouth=(0.45, 0.22, 0.20)):
    """Gera 3 quadros do rosto (neutral, blink, talk). A coluna direita é pele lisa, usada nas outras faces da cabeça."""
    c = lambda t: tuple(int(v * 255) for v in t)
    shade = tuple(int(v * 255 * 0.76) for v in skin)
    dark = tuple(int(v * 255 * 0.55) for v in skin)
    for state in ("neutral", "blink", "talk"):
        rng = np.random.default_rng(seed)
        img = Image.new("RGB", (64, 64), c(skin))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 63, 5], fill=c(hair_col))                 # linha do cabelo
        d.polygon([(0, 6), (63, 6), (63, 9), (32, 7), (0, 9)], fill=shade)
        d.rectangle([0, 54, 63, 63], fill=shade)                      # sombra sob o queixo
        for bx in (11, 38):                                           # sobrancelhas (inclinadas)
            d.polygon([(bx, 24), (bx + 14, 21), (bx + 14, 24), (bx, 26)], fill=c(brow))
        for ex in (13, 38):                                           # olhos
            if state == "blink":
                d.line([ex, 31, ex + 11, 31], fill=dark, width=2)
            else:
                d.rectangle([ex, 28, ex + 11, 33], fill=(232, 228, 214))
                d.rectangle([ex + 3, 28, ex + 8, 33], fill=c(eye))
                d.point([ex + 4, 29], fill=(255, 255, 255))
                d.line([ex, 27, ex + 11, 27], fill=dark)               # pálpebra
            d.line([ex, 36, ex + 11, 36], fill=shade)                  # olheira
        d.rectangle([29, 33, 35, 46], fill=shade)                     # lateral do nariz
        d.rectangle([27, 46, 37, 47], fill=dark)                      # narinas
        d.line([22, 40, 19, 50], fill=shade)                          # sulcos nasolabiais
        d.line([42, 40, 45, 50], fill=shade)
        if state == "talk":
            d.rectangle([22, 50, 41, 56], fill=(40, 12, 12))
            d.rectangle([24, 50, 39, 51], fill=(220, 215, 200))
        else:
            d.rectangle([23, 51, 40, 52], fill=c(mouth))
            d.line([22, 51, 24, 53], fill=shade)
            d.line([41, 51, 39, 53], fill=shade)
        for _ in range(int(age * 18)):                                # rugas e barba por fazer
            x0, y0 = int(rng.integers(6, 56)), int(rng.integers(12, 22))
            d.line([x0, y0, x0 + 4, y0], fill=shade)
        for _ in range(int(age * 60)):
            d.point([int(rng.integers(8, 55)), int(rng.integers(44, 60))], fill=dark)
        d.rectangle([60, 0, 63, 63], fill=c(skin))
        img.save(os.path.join(OUT, f"{prefix}_{state}.png"))


if __name__ == "__main__" and "--lena" in __import__("sys").argv:   # só Lena (cena 4): não refaz o resto
    face_states("face_lena", (0.82, 0.70, 0.62), (0.30, 0.20, 0.14), (0.35, 0.22, 0.14), age=0.0, seed=7, mouth=(0.72, 0.32, 0.34))
    cloth("dress_lena", (0.42, 0.36, 0.46), 41)
    hair("hair_lena", (0.35, 0.22, 0.14), 42)
    print("Lena ok")
elif __name__ == "__main__" and "--irina" in __import__("sys").argv:   # só Irina (cena 6)
    face_states("face_irina", (0.80, 0.64, 0.55), (0.45, 0.30, 0.18), (0.62, 0.40, 0.22), age=0.0, seed=11, eye=(0.10, 0.25, 0.22), mouth=(0.75, 0.15, 0.20))
    cloth("coat_irina", (0.12, 0.13, 0.15), 51)
    hair("hair_irina", (0.62, 0.40, 0.22), 52)
    print("Irina ok")
elif __name__ == "__main__" and "--extra" in __import__("sys").argv:   # só os personagens extras (cenas 12 e 13)
    face_states("face_trainer", (0.74, 0.58, 0.48), (0.40, 0.38, 0.36), (0.55, 0.52, 0.50), age=0.7, seed=21)
    cloth("tracksuit", (0.15, 0.20, 0.38), 61)
    face_states("face_inter", (0.70, 0.56, 0.46), (0.12, 0.10, 0.08), (0.12, 0.10, 0.08), age=0.5, seed=23, eye=(0.18, 0.14, 0.08))
    cloth("coat_dark", (0.20, 0.16, 0.12), 62)
    print("extras ok")
elif __name__ == "__main__":
    face_states("face_sergei", (0.74, 0.60, 0.50), (0.55, 0.55, 0.55), (0.62, 0.62, 0.60), age=0.8, seed=1)
    wallpaper(); parquet(); plaster(); wood_dark(); leather(); metal(); paper(); rug(); books(); chessboard(); crt()
    cloth("cardigan", (0.30, 0.27, 0.16), 30)
    cloth("trousers", (0.14, 0.14, 0.16), 32)
    hair("hair_grey", (0.62, 0.62, 0.60), 34)
    hair("hair_dark", (0.17, 0.12, 0.09), 35)
    cloth("uniform", (0.30, 0.34, 0.40), 37)  # farda da milícia
    face_states("face_boris", (0.72, 0.55, 0.44), (0.16, 0.12, 0.09), (0.17, 0.12, 0.09), age=0.45, seed=3)
    face("face_sergei", (0.74, 0.60, 0.50), (0.55, 0.55, 0.55), age=0.8, seed=1)
    print("texturas em", os.path.abspath(OUT))
