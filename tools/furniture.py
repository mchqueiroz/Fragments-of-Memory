"""Móveis e objetos grandes para as salas geradas por tools/episodios.py (Blender, estilo PS1, texel de 1 cm).

Cada função cria o móvel em (x, y) girado `rot` rad e devolve `bbox` = (cx, cy, topo_z, largura_x, profundidade_y), já com a
largura/profundidade trocadas quando o giro é de ~90°, para as pistas do jogo ganharem o colisor no lugar certo.
Não aninhar (kit.xf não compõe): chamar sempre no nível de topo.
"""
import math
import random

import props
from kit import box, cyl, mat, xf


def _c(r, g, b):
    return mat(None, color=(r, g, b))


def _bb(x, y, top, w, d, rot):
    swap = abs(math.sin(rot)) > 0.7
    return (x, y, top, d if swap else w, w if swap else d)


def desk(x, y, rot=0.0, w=1.4, d=0.7, drawers=True):
    WD = mat("wood_dark")
    with xf(x, y, rot):
        box(WD, (0, 0, 0.74), (w, d, 0.05))
        if drawers:
            box(WD, (-w / 2 + 0.2, 0, 0.36), (0.38, d - 0.06, 0.7))
            box(WD, (w / 2 - 0.03, 0, 0.36), (0.05, d - 0.06, 0.7), col=False)
            for k in range(3):
                box(mat("metal"), (-w / 2 + 0.2, -d / 2 + 0.01, 0.15 + k * 0.2), (0.1, 0.02, 0.025), col=False)
        else:
            for dx in (-w / 2 + 0.05, w / 2 - 0.05):
                box(WD, (dx, 0, 0.36), (0.05, d - 0.06, 0.7), col=False)
    return _bb(x, y, 0.765, w, d, rot)


def table(x, y, rot=0.0, w=1.2, d=0.8, h=0.75, top_mat="wood_dark"):
    WD = mat("wood_dark")
    with xf(x, y, rot):
        box(mat(top_mat), (0, 0, h - 0.025), (w, d, 0.05))
        for dx in (-w / 2 + 0.05, w / 2 - 0.05):
            for dy in (-d / 2 + 0.05, d / 2 - 0.05):
                box(WD, (dx, dy, (h - 0.05) / 2), (0.05, 0.05, h - 0.05), col=False)
    return _bb(x, y, h, w, d, rot)


def chair(x, y, rot=0.0, color=(0.30, 0.20, 0.12)):
    """Com rot=0 quem senta olha para +y (encosto em -y), como as escrivaninhas e os specs esperam."""
    m = _c(*color)
    with xf(x, y, rot):
        box(m, (0, 0, 0.45), (0.42, 0.42, 0.05), col=False)
        box(m, (0, -0.2, 0.75), (0.42, 0.04, 0.55), col=False)
        for dx in (-0.18, 0.18):
            for dy in (-0.18, 0.18):
                box(m, (dx, dy, 0.22), (0.04, 0.04, 0.44), col=False)
    return _bb(x, y, 0.5, 0.42, 0.42, rot)


def sofa(x, y, rot=0.0, w=2.0, d=0.9):
    LT = mat("leather")
    with xf(x, y, rot):
        box(LT, (0, 0, 0.25), (w, d, 0.5))
        box(LT, (0, d / 2 - 0.1, 0.75), (w, 0.2, 0.55))
        for dx in (-w / 2 + 0.09, w / 2 - 0.09):
            box(LT, (dx, 0, 0.55), (0.18, d, 0.4))
    return _bb(x, y, 0.55, w, d, rot)


def bed(x, y, rot=0.0, w=0.9, d=2.0, blanket=(0.40, 0.45, 0.50)):
    WD, SHEET = mat("wood_dark"), _c(0.84, 0.83, 0.78)
    with xf(x, y, rot):
        box(WD, (0, 0, 0.25), (w, d, 0.5))
        box(SHEET, (0, 0, 0.53), (w - 0.04, d - 0.1, 0.06), col=False)
        box(_c(*blanket), (0, -0.3, 0.58), (w - 0.02, d * 0.55, 0.06), col=False)
        box(SHEET, (0, d / 2 - 0.25, 0.60), (0.55, 0.32, 0.10), col=False)
        box(WD, (0, d / 2 + 0.01, 0.7), (w, 0.04, 0.6), col=False)
    return _bb(x, y, 0.6, w, d, rot)


def bookshelf(x, y, rot=0.0, w=1.0, d=0.32, h=2.0, seed=1):
    WD = mat("wood_dark")
    shelf_z = [0.05, 0.5, 0.95, 1.4, 1.85]
    with xf(x, y, rot):
        box(WD, (0, 0, h / 2), (w, d, h))
        for z in shelf_z:
            box(WD, (0, -0.02, z), (w - 0.04, d - 0.04, 0.03), col=False)
        for i, z in enumerate(shelf_z[:-1]):
            props.books(-w / 2 + 0.05, -d / 2 + 0.17, z + 0.02, n=int(w / 0.04), seed=seed + i)
    return _bb(x, y, h, w, d, rot)


def cabinet(x, y, rot=0.0, w=0.8, d=0.5, h=1.8, color=None):
    m = _c(*color) if color else mat("metal")
    with xf(x, y, rot):
        box(m, (0, 0, h / 2), (w, d, h))
        box(_c(0.05, 0.05, 0.06), (0, -d / 2 - 0.005, h / 2), (0.01, 0.02, h - 0.2), col=False)
        for k in range(2):
            box(mat("brass"), (-0.05 + k * 0.1, -d / 2 - 0.02, h * 0.55), (0.03, 0.03, 0.1), col=False)
    return _bb(x, y, h, w, d, rot)


def filing(x, y, rot=0.0, n=3):
    MT, BLK = mat("metal"), _c(0.05, 0.05, 0.06)
    with xf(x, y, rot):
        box(MT, (0, 0, 0.7), (0.5, 0.6, 1.4))
        for k in range(n + 1):
            box(BLK, (0, -0.305, 0.2 + k * 0.3), (0.4, 0.01, 0.22), col=False)
            box(MT, (0, -0.32, 0.2 + k * 0.3), (0.12, 0.02, 0.03), col=False)
    return _bb(x, y, 1.4, 0.5, 0.6, rot)


def console(x, y, rot=0.0, w=2.4, d=0.9):
    """Pupitre de controle: bancada com botões, luzes e dois monitores."""
    MT, BLK = mat("metal"), _c(0.05, 0.05, 0.06)
    SCR = mat(None, emit=(0.2, 1.0, 0.4), strength=2.0, color=(0.05, 0.25, 0.1))
    AMB = mat(None, emit=(1.0, 0.55, 0.1), strength=3.0, color=(0.4, 0.2, 0.05))
    RED = mat(None, emit=(1.0, 0.1, 0.05), strength=3.5, color=(0.4, 0.02, 0.02))
    with xf(x, y, rot):
        box(MT, (0, 0, 0.5), (w, d, 1.0))
        box(BLK, (0, -0.1, 1.02), (w - 0.1, d - 0.25, 0.05), col=False)
        for k in range(int(w / 0.2)):
            c = [AMB, RED, SCR][k % 3]
            box(c, (-w / 2 + 0.15 + k * 0.2, -d / 2 + 0.15, 1.06), (0.05, 0.05, 0.02), col=False)
        for sx in (-w / 4, w / 4):
            box(BLK, (sx, 0.15, 1.25), (0.6, 0.45, 0.45), col=False)
            box(SCR, (sx, -0.082, 1.27), (0.5, 0.02, 0.35), col=False)
    return _bb(x, y, 1.05, w, d, rot)


def computer(x, y, z, rot=0.0):
    """PC bege de 1993: monitor CRT, teclado e unidade."""
    BEIGE = _c(0.72, 0.70, 0.62)
    SCR = mat(None, emit=(0.2, 0.8, 0.35), strength=1.6, color=(0.05, 0.2, 0.1))
    with xf(x, y, rot, z):
        box(BEIGE, (0, 0.05, 0.2), (0.4, 0.38, 0.38), col=False)
        box(SCR, (0, -0.145, 0.22), (0.3, 0.02, 0.26), col=False)
        box(BEIGE, (0, -0.3, 0.02), (0.42, 0.14, 0.03), col=False)
        box(BEIGE, (0.32, 0.1, 0.1), (0.2, 0.36, 0.2), col=False)


def tv(x, y, rot=0.0):
    WD = mat("wood_dark")
    SCR = mat(None, emit=(0.6, 0.7, 0.9), strength=1.2, color=(0.2, 0.25, 0.3))
    with xf(x, y, rot):
        box(WD, (0, 0, 0.3), (0.7, 0.45, 0.6))
        box(_c(0.1, 0.1, 0.11), (0, 0, 0.85), (0.62, 0.45, 0.5), col=False)
        box(SCR, (0, -0.226, 0.87), (0.48, 0.02, 0.36), col=False)
        box(_c(0.1, 0.1, 0.1), (0.1, 0.0, 1.15), (0.01, 0.01, 0.3), col=False, rz=0.3)
    return _bb(x, y, 1.1, 0.7, 0.45, rot)


def bar(x, y, rot=0.0, w=3.0, d=0.7):
    WD = mat("wood_dark")
    r = random.Random(5)
    with xf(x, y, rot):
        box(WD, (0, 0, 0.55), (w, d, 1.1))
        box(_c(0.12, 0.08, 0.05), (0, 0, 1.12), (w + 0.1, d + 0.1, 0.05), col=False)
        for k in range(int(w / 0.3)):
            props.bottle(-w / 2 + 0.2 + k * 0.3, 0.1, 1.14, color=r.choice([(0.1, 0.3, 0.15), (0.3, 0.15, 0.05), (0.6, 0.6, 0.65)]))
        for k in range(int(w / 0.5)):
            cyl(_c(0.35, 0.18, 0.12), (-w / 2 + 0.3 + k * 0.5, -d / 2 - 0.4, 0.35), 0.17, 0.05, n=8, col=False)
            cyl(mat("metal"), (-w / 2 + 0.3 + k * 0.5, -d / 2 - 0.4, 0.17), 0.03, 0.34, n=6, col=False)
    return _bb(x, y, 1.15, w, d, rot)


def bench(x, y, rot=0.0, w=1.6, d=0.5):
    WD, MT = mat("wood_dark"), mat("metal")
    with xf(x, y, rot):
        box(WD, (0, 0, 0.45), (w, d, 0.05), col=False)
        box(WD, (0, d / 2 - 0.03, 0.75), (w, 0.04, 0.35), col=False)
        for dx in (-w / 2 + 0.1, w / 2 - 0.1):
            box(MT, (dx, 0, 0.22), (0.05, d - 0.05, 0.44), col=False)
    return _bb(x, y, 0.5, w, d, rot)


def locker(x, y, rot=0.0, n=3):
    MT = _c(0.35, 0.40, 0.45)
    for k in range(n):
        with xf(x + (k - (n - 1) / 2) * 0.42 * math.cos(rot), y + (k - (n - 1) / 2) * 0.42 * math.sin(rot), rot):
            box(MT, (0, 0, 0.95), (0.4, 0.45, 1.9))
            box(_c(0.1, 0.1, 0.1), (0, -0.23, 1.5), (0.18, 0.01, 0.2), col=False)
    return _bb(x, y, 1.9, 0.42 * n, 0.45, rot)


def crates(x, y, n=3, seed=1):
    r = random.Random(seed)
    for k in range(n):
        props.crate(x + r.uniform(-0.4, 0.4), y + r.uniform(-0.3, 0.3), 0.0, r.uniform(0.4, 0.55), rz=r.uniform(-0.3, 0.3))
    return (x, y, 0.55, 1.2, 1.0)


def rug(x, y, w=2.0, d=1.4, rot=0.0):
    with xf(x, y, rot):
        box(mat("rug"), (0, 0, 0.011), (w, d, 0.02), col=False)


def pillar(x, y, h=3.0, w=0.5):
    box(mat("concrete"), (x, y, h / 2), (w, w, h))
    return (x, y, h, w, w)


def vitrine(x, y, rot=0.0, w=1.0, d=0.6, content="bust"):
    """Vitrine de museu: base de madeira e caixa de vidro com um objeto."""
    GL = mat(None, emit=(0.6, 0.75, 0.85), strength=0.3, color=(0.5, 0.65, 0.75))
    with xf(x, y, rot):
        box(mat("wood_dark"), (0, 0, 0.45), (w, d, 0.9))
        box(GL, (0, 0, 1.2), (w - 0.04, d - 0.04, 0.6), col=False)
        if content == "bust":
            props.bust(0.0, 0.0, 0.9)
        elif content == "capsule":
            cyl(_c(0.55, 0.57, 0.6), (0, 0, 1.15), 0.12, 0.4, n=10, r2=0.04, col=False)
        else:
            box(_c(0.5, 0.5, 0.52), (0, 0, 1.0), (0.25, 0.18, 0.2), col=False)
    return _bb(x, y, 1.5, w, d, rot)


def phone_red(x, y, z):
    RD = _c(0.65, 0.06, 0.05)
    box(RD, (x, y, z + 0.04), (0.22, 0.2, 0.08), col=False)
    box(RD, (x, y, z + 0.1), (0.2, 0.05, 0.03), col=False)
    box(_c(0.9, 0.88, 0.8), (x, y + 0.05, z + 0.085), (0.1, 0.1, 0.005), col=False)


def lamp_table(x, y, z, color=(0.9, 0.7, 0.35)):
    box(_c(0.3, 0.3, 0.3), (x, y, z + 0.1), (0.04, 0.04, 0.2), col=False)
    cyl(mat(None, emit=color, strength=1.2, color=color), (x, y, z + 0.28), 0.13, 0.16, n=8, r2=0.08, col=False)


def curtains(x, y, wall="N", w=1.4, z=1.5, h=1.9, color=(0.35, 0.28, 0.30)):
    with xf(x, y, props._ROT[wall]):
        for cx in (-w / 2, w / 2):
            box(_c(*color), (cx, -0.1, z), (0.3, 0.08, h), col=False)
        box(mat("metal"), (0, -0.1, z + h / 2 + 0.05), (w + 0.5, 0.03, 0.03), col=False)


def missile(x, y, rot=0.0, length=4.0, r=0.5):
    """Míssil/cápsula deitado sobre dois berços de aço, com cone na ponta e estêncil."""
    MS = mat("missile_skin")
    with xf(x, y, rot):
        cyl(MS, (0, 0, r + 0.3), r, length, n=12, col=True, axis="y")
        cyl(MS, (0, length / 2 + 0.4, r + 0.3), r, 0.8, n=12, r2=0.06, col=False, axis="y")
        for dy in (-length * 0.3, length * 0.3):
            box(mat("metal"), (0, dy, 0.15), (1.3, 0.3, 0.3))
    return _bb(x, y, 2 * r + 0.3, 2 * r + 0.4, length + 0.8, rot)
