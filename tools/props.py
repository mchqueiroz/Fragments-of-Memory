"""Biblioteca de adereços para dar vida às salas: rodapé, porta entreaberta, interruptor e tomada, grade de ventilação, canos,
livros, papéis, canecas, garrafas, panelas, caixotes, balde, lixeira, relógio de parede, extintor, cabos, luminária de teto.

Uso: `import props` nos scripts de modelo (tools/cozinha.py etc.) e chamar no nível de topo (nunca dentro de `with xf`).
Itens de parede: `x, y` é o ponto na parede e `wall` diz de que lado ela é ("N" y=+, "S" y=-, "E" x=+, "W" x=-); a frente do
item olha para dentro da sala. Tudo sem colisão, exceto os itens grandes (caixote, lixeira, balde).
"""
import math
import random

import kit
from kit import box, cyl, mat, xf

_ROT = {"N": 0.0, "S": math.pi, "E": -math.pi / 2, "W": math.pi / 2}   # gira o item (frente em -y local) para dentro da sala


def _c(r, g, b):
    return mat(None, color=(r, g, b))


def baseboard(m, hx, hy, h=0.12, gaps=()):
    """Rodapé em volta de uma sala retangular (centro na origem). `gaps` = [(wall, a, b)] vãos de porta (coordenada ao longo da parede)."""
    for wall, length, fixed, axis in (("N", hx * 2, hy, "x"), ("S", hx * 2, -hy, "x"), ("E", hy * 2, hx, "y"), ("W", hy * 2, -hx, "y")):
        spans = [(-length / 2, length / 2)]
        for gw, a, b in gaps:
            if gw == wall:
                spans = [s for lo, hi in spans for s in ((lo, min(hi, a)), (max(lo, b), hi)) if s[1] - s[0] > 0.05]
        sign = 1 if fixed > 0 else -1
        for lo, hi in spans:
            mid, ln = (lo + hi) / 2, hi - lo
            if axis == "x":
                box(m, (mid, fixed - sign * 0.03, h / 2), (ln, 0.06, h), col=False)
            else:
                box(m, (fixed - sign * 0.03, mid, h / 2), (0.06, ln, h), col=False)


def door_leaf(m, x, y, w, h, hinge_rot=0.9, knob=None, z=0.0):
    """Folha de porta entreaberta: a dobradiça fica em (x, y) e a porta gira `hinge_rot` rad."""
    with xf(x, y, hinge_rot):
        box(m, (w / 2, 0, h / 2 + z), (w, 0.045, h), col=False)
        if knob:
            box(knob, (w - 0.08, -0.04, 1.0 + z), (0.05, 0.05, 0.05), col=False)


def switch(wall, x, y, z=1.25):
    plate, bt = _c(0.82, 0.80, 0.72), _c(0.55, 0.53, 0.48)
    with xf(x, y, _ROT[wall]):
        box(plate, (0, -0.012, z), (0.08, 0.024, 0.12), col=False)
        box(bt, (0, -0.028, z + 0.01), (0.03, 0.016, 0.05), col=False)


def outlet(wall, x, y, z=0.35):
    plate, hole = _c(0.80, 0.78, 0.70), _c(0.08, 0.07, 0.07)
    with xf(x, y, _ROT[wall]):
        box(plate, (0, -0.012, z), (0.08, 0.024, 0.08), col=False)
        for dx in (-0.016, 0.016):
            box(hole, (dx, -0.026, z), (0.008, 0.006, 0.02), col=False)


def vent(wall, x, y, z=2.3, w=0.35, h=0.2):
    frame, slat = _c(0.45, 0.45, 0.46), _c(0.06, 0.06, 0.07)
    with xf(x, y, _ROT[wall]):
        box(frame, (0, -0.012, z), (w, 0.024, h), col=False)
        for k in range(5):
            box(slat, (0, -0.028, z - h / 2 + 0.03 + k * (h - 0.06) / 4), (w - 0.04, 0.008, 0.012), col=False)


def pipe_x(m, y, z, x0, x1, r=0.04):
    cyl(m, ((x0 + x1) / 2, y, z), r, abs(x1 - x0), n=8, col=False, axis="x")


def pipe_y(m, x, z, y0, y1, r=0.04):
    cyl(m, (x, (y0 + y1) / 2, z), r, abs(y1 - y0), n=8, col=False, axis="y")


def pipe_z(m, x, y, z0, z1, r=0.04):
    cyl(m, (x, y, (z0 + z1) / 2), r, abs(z1 - z0), n=8, col=False)


def books(x, y, z, n=10, along="x", seed=1, height=(0.18, 0.28), thick=(0.025, 0.05)):
    """Fileira de livros sobre uma prateleira em (x, y, z=topo da prateleira)."""
    r = random.Random(seed)
    cols = [_c(*c) for c in ((0.45, 0.20, 0.18), (0.20, 0.30, 0.40), (0.55, 0.45, 0.25), (0.25, 0.35, 0.25), (0.30, 0.28, 0.26),
                              (0.60, 0.55, 0.45), (0.15, 0.15, 0.20))]
    pos = 0.0
    for _ in range(n):
        t, hh = r.uniform(*thick), r.uniform(*height)
        lean = r.uniform(-0.08, 0.08) if r.random() < 0.15 else 0.0
        if along == "x":
            box(r.choice(cols), (x + pos + t / 2, y, z + hh / 2), (t, 0.17, hh), col=False, rz=lean)
        else:
            box(r.choice(cols), (x, y + pos + t / 2, z + hh / 2), (0.17, t, hh), col=False, rz=lean)
        pos += t + 0.003


def papers(x, y, z, n=3, seed=1, size=(0.21, 0.30)):
    """Pilha bagunçada de folhas sobre uma superfície em (x, y, z=topo)."""
    r = random.Random(seed)
    pp = _c(0.80, 0.78, 0.70)
    for k in range(n):
        box(pp, (x + r.uniform(-0.03, 0.03), y + r.uniform(-0.03, 0.03), z + 0.003 + k * 0.004),
            (size[0], size[1], 0.003), col=False, rz=r.uniform(-0.5, 0.5))


def mug(x, y, z, color=(0.75, 0.73, 0.68)):
    cyl(_c(*color), (x, y, z + 0.045), 0.035, 0.09, n=8, col=False)
    box(_c(*color), (x + 0.045, y, z + 0.05), (0.02, 0.012, 0.05), col=False)


def bottle(x, y, z, color=(0.10, 0.30, 0.15), h=0.28):
    gl = mat(None, emit=color, strength=0.25, color=color)
    cyl(gl, (x, y, z + h * 0.4), 0.035, h * 0.8, n=8, col=False)
    cyl(gl, (x, y, z + h * 0.9), 0.016, h * 0.25, n=6, col=False)


def jar(x, y, z, fill=(0.55, 0.35, 0.12)):
    cyl(mat(None, emit=fill, strength=0.3, color=fill), (x, y, z + 0.06), 0.045, 0.12, n=8, col=False)
    cyl(_c(0.5, 0.5, 0.52), (x, y, z + 0.125), 0.047, 0.015, n=8, col=False)


def pot(x, y, z, r=0.12, h=0.16, color=(0.55, 0.55, 0.57)):
    cyl(_c(*color), (x, y, z + h / 2), r, h, n=10, col=False)
    box(_c(0.1, 0.1, 0.1), (x + r + 0.05, y, z + h * 0.8), (0.12, 0.03, 0.02), col=False)


def plate(x, y, z, r=0.11):
    cyl(_c(0.82, 0.80, 0.74), (x, y, z + 0.008), r, 0.016, n=12, col=False)


def bread(x, y, z):
    box(_c(0.55, 0.38, 0.18), (x, y, z + 0.05), (0.26, 0.11, 0.09), col=False, rz=0.2)


def crate(x, y, z=0.0, s=0.45, rz=0.0, color=(0.40, 0.30, 0.18)):
    box(_c(*color), (x, y, z + s / 2), (s, s, s), col=True, rz=rz)
    for dz in (0.08, s - 0.08):
        box(_c(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7), (x, y, z + dz), (s + 0.01, s + 0.01, 0.03), col=False, rz=rz)


def bucket(x, y, z=0.0, color=(0.40, 0.42, 0.45)):
    cyl(_c(*color), (x, y, z + 0.15), 0.17, 0.30, n=10, r2=0.14, col=True)


def bin_(x, y, z=0.0):
    cyl(_c(0.22, 0.24, 0.26), (x, y, z + 0.22), 0.16, 0.44, n=10, col=True)
    for k in range(3):
        box(_c(0.7, 0.68, 0.6), (x + 0.04 * k - 0.04, y + 0.03, z + 0.45), (0.08, 0.06, 0.012), col=False, rz=0.8 * k)


def wall_clock(wall, x, y, z=2.0, r=0.17):
    face, rim, hand = _c(0.82, 0.80, 0.72), _c(0.08, 0.08, 0.09), _c(0.05, 0.05, 0.05)
    with xf(x, y, _ROT[wall]):
        cyl(rim, (0, -0.02, z), r + 0.015, 0.03, n=14, col=False, axis="y")
        cyl(face, (0, -0.036, z), r, 0.01, n=14, col=False, axis="y")
        box(hand, (0.0, -0.045, z + 0.05), (0.012, 0.006, 0.1), col=False)
        box(hand, (0.04, -0.045, z), (0.08, 0.006, 0.012), col=False)


def extinguisher(wall, x, y, z=0.0):
    with xf(x, y, _ROT[wall]):
        cyl(_c(0.65, 0.08, 0.06), (0, -0.09, z + 0.28), 0.07, 0.5, n=10, col=False)
        cyl(_c(0.1, 0.1, 0.1), (0, -0.09, z + 0.55), 0.03, 0.06, n=8, col=False)
        box(_c(0.3, 0.3, 0.3), (0, -0.02, z + 0.30), (0.12, 0.03, 0.05), col=False)


def cable(m, pts, r=0.012):
    """Cabo seguindo uma polilinha de pontos (x, y, z), em segmentos retos (fios soltos no chão ou na parede)."""
    for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        if ln > 0.01:
            box(m, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (ln, r * 2, r * 2), col=False, rz=math.atan2(dy, dx))


def ceiling_lamp(x, y, z, kind="tube"):
    body = _c(0.78, 0.78, 0.74)
    if kind == "tube":
        box(body, (x, y, z), (1.25, 0.2, 0.06), col=False)
        box(mat(None, emit=(0.9, 0.95, 1.0), strength=2.0, color=(0.8, 0.85, 0.9)), (x, y, z - 0.035), (1.15, 0.12, 0.02), col=False)
    else:
        cyl(body, (x, y, z), 0.14, 0.04, n=10, col=False)


def radiator(wall, x, y, w=0.9, z=0.15):
    mt = _c(0.62, 0.60, 0.55)
    with xf(x, y, _ROT[wall]):
        for k in range(int(w / 0.07)):
            box(mt, (-w / 2 + 0.035 + k * 0.07, -0.07, z + 0.3), (0.05, 0.1, 0.6), col=False)
        box(mt, (0, -0.07, z + 0.58), (w, 0.1, 0.03), col=False)
        box(mt, (0, -0.07, z + 0.03), (w, 0.1, 0.03), col=False)


def notice_board(wall, x, y, z=1.7, w=0.8, h=0.55, seed=1):
    r = random.Random(seed)
    cork, pap = _c(0.50, 0.36, 0.22), _c(0.82, 0.80, 0.72)
    with xf(x, y, _ROT[wall]):
        box(cork, (0, -0.015, z), (w, 0.03, h), col=False)
        for _ in range(6):
            box(pap, (r.uniform(-w / 2 + 0.1, w / 2 - 0.1), -0.034, z + r.uniform(-h / 2 + 0.08, h / 2 - 0.08)),
                (r.uniform(0.1, 0.18), 0.004, r.uniform(0.12, 0.22)), col=False)


# ======================================================================================================================
# Objetos soviéticos de 1993 (cotidiano, burocracia, paranoia). Texturas de tools/russian.py.
# ======================================================================================================================
_FACE = {"N": "-y", "S": "+y", "E": "-x", "W": "+x"}    # para onde a face do cartaz olha (para dentro da sala)


def poster(tex, wall, x, y, z, w, h):
    """Cartaz/aviso/quadro numa parede: (x, y) = ponto na parede, z = centro; w x h em metros."""
    from gabinete import panel
    off = {"N": (0, -0.015), "S": (0, 0.015), "E": (-0.015, 0), "W": (0.015, 0)}[wall]
    size = (w, 0.02, h) if wall in ("N", "S") else (0.02, w, h)
    panel(mat(tex), (x + off[0], y + off[1], z), size, _FACE[wall])


def flat_tex(tex, x, y, z, w, h, rz=0.0):
    """Papel/cartão/nota solto sobre uma superfície (imagem na face de cima)."""
    from gabinete import flat
    flat(mat(tex), (x, y, z), (w, h, 0.004), rz=rz)


def podstakannik(x, y, z):
    """Copo de chá no suporte de metal (podstakannik), o 'copo soviético' por excelência."""
    cyl(mat(None, emit=(0.55, 0.30, 0.08), strength=0.35, color=(0.45, 0.25, 0.08)), (x, y, z + 0.052), 0.030, 0.104, n=10, col=False)
    cyl(_c(0.68, 0.66, 0.60), (x, y, z + 0.04), 0.035, 0.08, n=10, col=False)
    box(_c(0.68, 0.66, 0.60), (x + 0.048, y, z + 0.055), (0.02, 0.012, 0.06), col=False)


def ashtray(x, y, z):
    cyl(_c(0.50, 0.50, 0.52), (x, y, z + 0.01), 0.06, 0.02, n=10, col=False)
    for k in range(5):
        box(_c(0.85, 0.82, 0.72), (x + 0.025 * math.cos(k * 1.3), y + 0.025 * math.sin(k * 1.3), z + 0.03), (0.03, 0.008, 0.008),
            col=False, rz=k)


def avoska(wall, x, y, z=1.2):
    """Sacola de rede (avoska) pendurada com batatas: toda cozinha soviética tem uma."""
    net, pot_ = _c(0.78, 0.72, 0.55), _c(0.45, 0.34, 0.20)
    with xf(x, y, _ROT[wall]):
        box(net, (0, -0.09, z), (0.20, 0.14, 0.32), col=False)
        for dx, dz in ((-0.05, -0.1), (0.05, -0.08), (0.0, -0.02), (-0.04, 0.05), (0.05, 0.04)):
            box(pot_, (dx, -0.09, z + dz), (0.07, 0.06, 0.06), col=False, rz=dx * 9)
        box(_c(0.1, 0.1, 0.1), (0, -0.03, z + 0.2), (0.012, 0.012, 0.08), col=False)


def valenki(x, y, rz=0.0):
    """Par de valenki (botas de feltro cinza) deixadas perto da porta."""
    felt = _c(0.40, 0.38, 0.36)
    for dx in (-0.07, 0.07):
        with xf(x, y, rz):
            box(felt, (dx, 0, 0.17), (0.10, 0.12, 0.34), col=False)
            box(felt, (dx, -0.07, 0.05), (0.10, 0.20, 0.10), col=False)


def bust(x, y, z, scale=1.0):
    """Busto de gesso de Lenin sobre um pedestal, resto de um escritório do Estado."""
    gy = _c(0.82, 0.80, 0.74)
    box(gy, (x, y, z + 0.03 * scale), (0.14 * scale, 0.14 * scale, 0.06 * scale), col=False)
    box(gy, (x, y, z + 0.11 * scale), (0.12 * scale, 0.08 * scale, 0.10 * scale), col=False)
    cyl(gy, (x, y, z + 0.21 * scale), 0.05 * scale, 0.10 * scale, n=8, col=False)
    box(gy, (x, y - 0.045 * scale, z + 0.19 * scale), (0.04 * scale, 0.025 * scale, 0.05 * scale), col=False)   # barbicha


def books_red(x, y, z, n=8, along="x"):
    """Volumes iguais de capa vermelha com título dourado: as 'obras completas' de toda estante soviética."""
    red, gold = _c(0.55, 0.10, 0.10), _c(0.80, 0.65, 0.25)
    for k in range(n):
        o = k * 0.043
        if along == "x":
            box(red, (x + o, y, z + 0.13), (0.04, 0.17, 0.26), col=False)
            box(gold, (x + o, y - 0.088, z + 0.2), (0.03, 0.004, 0.02), col=False)
        else:
            box(red, (x, y + o, z + 0.13), (0.17, 0.04, 0.26), col=False)
            box(gold, (x - 0.088, y + o, z + 0.2), (0.004, 0.03, 0.02), col=False)


def lab_coat(wall, x, y, z=1.2):
    white = _c(0.82, 0.80, 0.74)
    with xf(x, y, _ROT[wall]):
        box(_c(0.35, 0.28, 0.2), (0, -0.04, z + 0.62), (0.40, 0.04, 0.04), col=False)
        box(white, (0, -0.10, z + 0.1), (0.38, 0.12, 0.95), col=False)
        for sx in (1, -1):
            box(white, (sx * 0.21, -0.10, z - 0.03), (0.07, 0.10, 0.55), col=False)


def door_security(wall, x, y, z=1.0):
    """Paranoia de morador soviético: duas fechaduras, corrente de segurança e olho mágico. (x, y) = ponto na face interna da porta."""
    brass, blk = _c(0.72, 0.60, 0.25), _c(0.06, 0.06, 0.06)
    with xf(x, y, _ROT[wall]):
        for dz in (0.0, 0.27):
            box(brass, (-0.22, -0.012, z + dz), (0.07, 0.024, 0.11), col=False)
            box(blk, (-0.22, -0.026, z + dz), (0.012, 0.01, 0.03), col=False)
        for k in range(5):                                                    # corrente de segurança
            box(brass, (-0.12 + k * 0.03, -0.02, z + 0.55), (0.025, 0.008, 0.012), col=False)
        box(brass, (-0.30, -0.015, z + 0.55), (0.04, 0.03, 0.03), col=False)
        cyl(blk, (0.0, -0.014, z + 0.62), 0.018, 0.02, n=8, col=False, axis="y")     # olho mágico


def door(wall, c, y, w=0.9, h=2.05, angle=0.5, with_security=True):
    """Porta de madeira entreaberta no vão centrado em c da parede `wall` (y = coordenada da parede). A folha gira para dentro."""
    wood, trim = mat("wood_dark"), _c(0.18, 0.12, 0.08)
    brass = _c(0.72, 0.60, 0.25)
    sgn = {"S": 1, "N": -1}.get(wall, 1)
    hx_, hy_ = c - w / 2, y + sgn * 0.03
    with xf(hx_, hy_, sgn * angle):
        box(wood, (w / 2, 0, h / 2), (w, 0.045, h), col=False)
        box(trim, (w / 2, -sgn * 0.024, h * 0.7), (w - 0.2, 0.01, h * 0.28), col=False)
        box(trim, (w / 2, -sgn * 0.024, h * 0.28), (w - 0.2, 0.01, h * 0.32), col=False)
        box(brass, (w - 0.08, sgn * 0.04, 1.0), (0.06, 0.05, 0.03), col=False)
        if with_security:
            for dz in (0.0, 0.27):
                box(brass, (w - 0.24, sgn * 0.03, 1.2 + dz), (0.07, 0.02, 0.11), col=False)
            for k in range(5):
                box(brass, (w - 0.36 + k * 0.03, sgn * 0.03, 1.75), (0.025, 0.008, 0.012), col=False)
