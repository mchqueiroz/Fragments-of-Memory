"""Gabinete de Sergei, Moscou 1993 — cenografia com intenção (cada objeto conta algo).

Uso: blender -b -P tools/gabinete.py        -> art/models/gabinete.glb
Princípios (direção de arte):
  * nada é decorativo: cada peça existe por um motivo da história e de uma pessoa específica;
  * assimetria e desgaste: objetos tortos, usados, fora do lugar;
  * 1993: papel de parede desbotado com retângulo claro onde havia o retrato de Lenin (retirado em 1991),
    painel verde de instituto, tapete de parede, fita de papel nas janelas, samovar, telefone de disco;
  * mistério: espelho coberto de preto (costume russo após uma morte), segunda porta com luz por baixo,
    dois copos de chá (um intocado), calendário parado em março de 1992, retrato de Lena virado para a cadeira.
Eixos: X leste, Y norte (frente do jogador), Z cima. Frente das fotos: ver `panel`.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402, F401

import kit  # noqa: E402
import props  # noqa: E402
from kit import box, cyl, mat, xf  # noqa: E402

# índice da face de uma caixa que olha para cada direção (ver kit.box): -y=2, +y=3, -x=4, +x=5, topo=1
FACE = {"-y": 2, "+y": 3, "-x": 4, "+x": 5, "top": 1}
# cantos (UV) da face visível para ficar "em pé" e sem espelhar
QUAD = [(0, 0), (1, 0), (1, 1), (0, 1)]


def panel(m, c, size, facing, rz=0.0):
    """Quadro/cartaz/foto: a imagem inteira em UMA face; `size` = (x, y, z) da caixa no mundo."""
    vis = FACE[facing]
    box(m, c, size, col=False, rz=rz, face_uv=lambda fi: QUAD if fi == vis else [(0.03, 0.03)] * 4)


def flat(m, c, size, rz=0.0):
    """Papel/pasta sobre uma superfície, imagem na face de cima."""
    box(m, c, size, col=False, rz=rz, face_uv=lambda fi: QUAD if fi == 1 else [(0.03, 0.03)] * 4)


def gabinete():
    random.seed(1993)
    WP, PQ, PL = mat("wallpaper"), mat("parquet_square"), mat("plaster")
    GREEN, WD, LT, MT = mat("paint_green"), mat("wood_dark"), mat("leather"), mat("metal")
    PP, RG, BK, CUR = mat("paper"), mat("rug"), mat("books"), mat("cardigan")
    BRASS, CLOTH, SHADE = mat("brass"), mat("black_cloth"), mat("lampshade")
    PATCH, KOVER = mat("wallpaper_patch"), mat("kover_wall")
    P_LENA, P_TEAM, P_POSTER = mat("pic_lena"), mat("pic_team"), mat("poster_space")
    P_DIPL, P_CAL, P_NEWS = mat("diploma"), mat("calendar_1992"), mat("newspaper")
    P_PLATE, P_ICON, P_PAP = mat("door_plate"), mat("icon"), mat("papirosy")
    P_TAPE, P_FOLD = mat("tape_label"), mat("folder_secret")
    NIGHT = mat(None, emit=(0.03, 0.06, 0.14), strength=0.4, color=(0, 0, 0))
    CITY = mat(None, emit=(1.0, 0.8, 0.4), strength=2.5, color=(0, 0, 0))
    AMBER = mat(None, emit=(1.0, 0.65, 0.25), strength=1.6, color=(0.4, 0.3, 0.1))
    GLASSTEA = mat(None, emit=(0.55, 0.22, 0.05), strength=0.9, color=(0.25, 0.1, 0.03))
    OLDTEA = mat(None, emit=(0.4, 0.15, 0.04), strength=0.35, color=(0.2, 0.08, 0.02))
    CRYSTAL = mat(None, emit=(0.4, 0.5, 0.6), strength=0.35, color=(0.5, 0.55, 0.6))
    GREENLAMP = mat(None, emit=(0.25, 0.8, 0.45), strength=1.2, color=(0.1, 0.3, 0.15))
    REDLAMP = mat(None, emit=(1.0, 0.1, 0.05), strength=3.0, color=(0.3, 0.02, 0.02))
    DOORLIGHT = mat(None, emit=(1.0, 0.8, 0.45), strength=4.0, color=(0.5, 0.4, 0.2))
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    DARK = mat(None, color=(0.04, 0.05, 0.08))
    WHITE = mat(None, color=(0.78, 0.76, 0.70))
    SLIPPER = mat(None, color=(0.45, 0.18, 0.20))
    COAT = mat("trousers")
    Wd, Dd, H = 6.4, 5.6, 3.3
    hx, hy = Wd / 2, Dd / 2
    PANEL = 1.1  # altura da pintura verde

    # ---- piso, teto, vigas, tapete corredor (dá caminho até a mesa) ---------------------------
    box(PQ, (0, 0, -0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    for y in (-1.2, 1.2):
        box(WD, (0, y, H - 0.1), (Wd, 0.25, 0.2))
    box(RG, (0.1, -0.5, 0.011), (1.1, 3.9, 0.02), col=False)
    box(RG, (-0.6, 1.0, 0.011), (1.7, 1.2, 0.02), col=False, rz=0.07)     # tapete torto sob a mesa

    # ---- paredes: papel desbotado em cima, tinta verde embaixo; vãos: porta sul, 2 janelas, porta de Lena
    def wall(x0, x1, y, z0, z1, thick=0.2, m=WP):
        box(m, ((x0 + x1) / 2, y, (z0 + z1) / 2), (x1 - x0, thick, z1 - z0))

    box(WP, (-hx - 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    box(WP, (hx + 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    wall(-hx - 0.2, 1.6, -hy - 0.1, 0, H)            # sul: porta entre x=1.6 e 2.6
    wall(2.6, hx + 0.2, -hy - 0.1, 0, H)
    wall(1.6, 2.6, -hy - 0.1, 2.2, H)
    sill, head = 0.95, 2.55                           # norte: janelas em x=±1.6, porta de Lena entre 2.3 e 3.2
    wall(-hx - 0.2, -2.2, hy + 0.1, 0, H)
    wall(-1.0, 1.0, hy + 0.1, 0, H)
    wall(2.2, 2.3, hy + 0.1, 0, H)
    wall(3.2, hx + 0.2, hy + 0.1, 0, H)
    wall(2.3, 3.2, hy + 0.1, 2.15, H)
    for xc in (-1.6, 1.6):
        wall(xc - 0.6, xc + 0.6, hy + 0.1, 0, sill)
        wall(xc - 0.6, xc + 0.6, hy + 0.1, head, H)

    def paint(x0, x1, y0, y1):
        """Faixa de pintura verde de instituto + friso branco; é fina e fica colada na parede."""
        box(GREEN, ((x0 + x1) / 2, (y0 + y1) / 2, PANEL / 2), (max(x1 - x0, 0.04), max(y1 - y0, 0.04), PANEL), col=False)
        box(WHITE, ((x0 + x1) / 2, (y0 + y1) / 2, PANEL + 0.025), (max(x1 - x0, 0.06), max(y1 - y0, 0.06), 0.05), col=False)

    paint(-hx, -hx + 0.03, -hy, hy)
    paint(hx - 0.03, hx, -hy, hy)
    paint(-hx, 1.6, -hy, -hy + 0.03)
    paint(2.6, hx, -hy, -hy + 0.03)
    for a, b in ((-hx, -2.2), (-1.0, 1.0), (2.2, 2.3)):
        paint(a, b, hy - 0.03, hy)
    paint(3.2, hx, hy - 0.03, hy)
    for xc in (-1.6, 1.6):
        paint(xc - 0.6, xc + 0.6, hy - 0.03, hy)
    for (c, s) in (((-hx + 0.05, 0, H - 0.08), (0.1, Dd, 0.14)), ((hx - 0.05, 0, H - 0.08), (0.1, Dd, 0.14)),
                   ((0, hy - 0.05, H - 0.08), (Wd, 0.1, 0.14)), ((0, -hy + 0.05, H - 0.08), (Wd, 0.1, 0.14))):
        box(PL, c, s, col=False)

    # ---- janelas: caixilho duplo, fita de papel de inverno, cortinas, radiador, noite lá fora -----------
    for xc in (-1.6, 1.6):
        for dx in (-0.62, 0.62):
            box(WD, (xc + dx, hy - 0.04, (sill + head) / 2), (0.06, 0.1, head - sill + 0.1), col=False)
        for z in (sill - 0.03, head + 0.03):
            box(WD, (xc, hy - 0.04, z), (1.3, 0.1, 0.06), col=False)
        box(WD, (xc, hy - 0.04, (sill + head) / 2), (0.03, 0.06, head - sill), col=False)
        box(WD, (xc, hy - 0.04, (sill + head) / 2 + 0.1), (1.2, 0.06, 0.03), col=False)
        box(NIGHT, (xc, hy + 0.12, (sill + head) / 2), (1.2, 0.02, head - sill), col=False)
        for z in (sill + 0.02, head - 0.02, (sill + head) / 2 + 0.1):          # fita de papel nas frestas
            box(PP, (xc, hy - 0.075, z), (1.18, 0.004, 0.03), col=False)
        for dx in (-0.29, 0.29):
            box(PP, (xc + dx, hy - 0.075, (sill + head) / 2), (0.03, 0.004, head - sill), col=False)
        box(WD, (xc, hy - 0.2, sill - 0.04), (1.5, 0.35, 0.06), col=False)
        for dx in (-0.85, 0.85):
            box(CUR, (xc + dx, hy - 0.18, 1.75), (0.42, 0.13, 2.5), col=False, rz=random.uniform(-0.04, 0.04))
        box(MT, (xc, hy - 0.12, 0.42), (1.0, 0.12, 0.6))
        for k in range(8):
            box(MT, (xc - 0.42 + k * 0.12, hy - 0.12, 0.42), (0.03, 0.14, 0.62), col=False)
    for i in range(14):
        x = -2.4 + i * 0.36
        h = random.uniform(1.0, 2.2)
        box(DARK, (x, hy + 0.9, h / 2 + 0.4), (0.34, 0.1, h), col=False)
        for _ in range(random.randint(1, 3)):
            box(CITY, (x + random.uniform(-0.1, 0.1), hy + 0.84, random.uniform(0.7, h + 0.3)), (0.05, 0.02, 0.05), col=False)

    # ---- porta de entrada (sul) e a porta de Lena (norte), com luz vazando por baixo -------------
    for dx in (-0.55, 0.55):
        box(WD, (2.1 + dx, -hy + 0.04, 1.1), (0.1, 0.12, 2.2), col=False)
    box(WD, (2.1, -hy + 0.04, 2.25), (1.2, 0.12, 0.1), col=False)
    box(WD, (2.1, -hy + 0.02, 1.05), (0.98, 0.05, 2.1))
    box(MT, (1.7, -hy + 0.08, 1.0), (0.04, 0.06, 0.12), col=False)
    for dx in (-0.5, 0.5):
        box(WD, (2.75 + dx, hy - 0.04, 1.08), (0.1, 0.12, 2.15), col=False)
    box(WD, (2.75, hy - 0.04, 2.18), (1.1, 0.12, 0.1), col=False)
    box(WD, (2.75, hy - 0.02, 1.05), (0.88, 0.05, 2.1), col=True)
    box(MT, (2.4, hy - 0.07, 1.0), (0.04, 0.06, 0.12), col=False)
    box(DOORLIGHT, (2.75, hy - 0.03, 0.012), (0.86, 0.01, 0.02), col=False)    # luz por baixo da porta
    for dx, rz in ((-0.07, 0.4), (0.08, 0.15)):                               # chinelos de Lena junto à porta
        box(SLIPPER, (2.55 + dx, hy - 0.4, 0.03), (0.09, 0.24, 0.06), col=False, rz=rz)

    # ---- parede norte entre as janelas: retângulo claro do retrato removido + prego ------------------
    panel(PATCH, (0, hy - 0.012, 2.1), (0.64, 0.01, 0.84), "-y")
    # ---- parede leste: tapete de parede sobre o sofá, cartaz espacial, canto do ícone ---------------
    panel(KOVER, (hx - 0.012, -0.6, 1.95), (0.01, 1.28, 1.76), "-x")
    panel(P_POSTER, (hx - 0.015, 1.15, 1.65), (0.02, 0.64, 0.96), "-x")
    box(WD, (hx - 0.05, 2.15, 1.82), (0.12, 0.34, 0.03), col=False)            # prateleira do ícone
    panel(P_ICON, (hx - 0.03, 2.15, 2.07), (0.02, 0.32, 0.44), "-x")
    box(REDLAMP, (hx - 0.1, 2.15, 1.92), (0.05, 0.05, 0.08), col=False)        # lamparina vermelha
    # ---- parede sul: foto da equipe, calendário parado em março/92, diploma, relógio -----------------
    panel(P_TEAM, (-2.75, -hy + 0.02, 2.05), (1.04, 0.02, 0.64), "+y")
    panel(P_CAL, (-2.0, -hy + 0.02, 2.0), (0.48, 0.012, 0.64), "+y")
    panel(P_DIPL, (-1.25, -hy + 0.02, 1.95), (0.96, 0.02, 0.72), "+y", rz=0.03)
    box(WD, (-0.45, -hy + 0.03, 2.45), (0.34, 0.05, 0.34), col=False)
    box(PP, (-0.45, -hy + 0.058, 2.45), (0.28, 0.01, 0.28), col=False)
    box(BLACK, (-0.45, -hy + 0.066, 2.50), (0.012, 0.01, 0.1), col=False)
    box(BLACK, (-0.43, -hy + 0.066, 2.45), (0.08, 0.01, 0.012), col=False)
    # ---- espelho coberto por pano preto (parede norte, esquerda) -------------------------------------
    box(WD, (-2.72, hy - 0.03, 1.0), (0.66, 0.05, 1.9), col=False)
    box(CLOTH, (-2.72, hy - 0.06, 1.1), (0.62, 0.025, 1.95), col=False)
    box(CLOTH, (-2.55, hy - 0.075, 0.7), (0.2, 0.025, 0.5), col=False, rz=0.1)  # dobra do pano

    # ---- "stenka": estante e vitrine na parede oeste -------------------------------------------------
    with xf(-hx + 0.2, 0.0):
        box(WD, (-0.16, 0, 1.55), (0.03, 4.2, 3.1))
        for y in (-2.1, 2.1):
            box(WD, (0, y, 1.55), (0.36, 0.05, 3.1))
        for k in range(7):
            z = 0.12 + k * 0.5
            box(WD, (0, 0, z), (0.36, 4.2, 0.04))
            if k == 6:
                break
            y = -2.0
            while y < 1.95:
                if k in (2, 3) and -0.6 < y < 0.6:      # vitrine central: cristais, não livros
                    box(CRYSTAL, (-0.02, y + 0.07, z + 0.12), (0.06, 0.06, 0.18), col=False)
                    y += random.uniform(0.12, 0.22)
                    continue
                w = random.uniform(0.03, 0.07)
                d = random.uniform(0.2, 0.3)
                h = random.uniform(0.22, 0.4)
                box(BK, (-0.14 + d / 2, y + w / 2, z + 0.02 + h / 2), (d, w, h), col=False, uv=(random.random(), 0.0),
                    rz=random.choice([0, 0, 0, 0, 0.05]))
                y += w + 0.002
                if random.random() < 0.05:
                    y += random.uniform(0.1, 0.3)
        flat(P_FOLD, (0.0, -1.5, 1.74), (0.3, 0.22, 0.03), rz=0.2)             # pasta "СЕКРЕТНО" largada na prateleira

    # ---- mesa de trabalho -----------------------------------------------------------------------------
    with xf(0, 1.55):
        box(WD, (0, 0, 0.74), (2.2, 0.95, 0.06))
        for dx in (-0.85, 0.85):
            box(WD, (dx, 0, 0.36), (0.55, 0.85, 0.7))
            for k in range(3):
                box(MT, (dx, -0.43, 0.14 + k * 0.22), (0.1, 0.02, 0.025), col=False)
        box(WD, (0, 0.36, 0.45), (1.1, 0.04, 0.5), col=False)
        flat(P_NEWS, (0.3, -0.12, 0.775), (0.56, 0.4, 0.008), rz=0.2)           # Izvestia de 3/out/1993
        flat(PP, (0.55, 0.12, 0.783), (0.3, 0.4, 0.008), rz=-0.3)
        flat(P_FOLD, (-0.55, -0.2, 0.775), (0.3, 0.22, 0.02), rz=-0.15)         # pasta SECRETO
        flat(P_PAP, (0.05, 0.3, 0.78), (0.1, 0.07, 0.025), rz=0.5)              # maço de Belomor
        cyl(MT, (0.18, 0.28, 0.785), 0.05, 0.03, n=8, col=False)                 # cinzeiro
        box(BLACK, (0.8, 0.18, 0.80), (0.2, 0.22, 0.07), col=False, rz=0.2)      # telefone de disco
        cyl(MT, (0.8, 0.14, 0.845), 0.045, 0.012, n=8, col=False)
        box(BLACK, (0.77, 0.24, 0.86), (0.18, 0.05, 0.04), col=False, rz=0.2)
        box(MT, (-0.25, 0.1, 0.8), (0.36, 0.3, 0.1), col=False, rz=0.1)          # máquina de escrever
        box(BLACK, (-0.25, 0.1, 0.86), (0.3, 0.2, 0.03), col=False, rz=0.1)
        flat(PP, (-0.25, 0.22, 0.98), (0.22, 0.005, 0.25), rz=0.1)
        for (x, y, full) in ((0.62, -0.3, False), (-0.15, -0.34, True)):          # copos de chá: um usado, um INTOCADO
            cyl(BRASS, (x, y, 0.80), 0.04, 0.09, n=8, col=False)
            cyl(GLASSTEA if full else OLDTEA, (x, y, 0.815), 0.03, 0.06, n=8, col=False)
        box(WD, (-0.9, 0.38, 0.88), (0.2, 0.03, 0.26), col=False, rz=0.1)        # retrato de Lena virado p/ a cadeira
        panel(P_LENA, (-0.9, 0.365, 0.88), (0.17, 0.01, 0.22), "-y", rz=0.1)
        box(MT, (-0.85, 0.0, 0.79), (0.2, 0.14, 0.04), col=False)                # abajur de banqueiro
        box(MT, (-0.85, 0.0, 0.93), (0.03, 0.03, 0.26), col=False)
        box(GREENLAMP, (-0.85, 0.0, 1.07), (0.34, 0.14, 0.12), col=False)
        flat(P_PLATE, (0.0, -0.4, 0.776), (0.2, 0.07, 0.012))                    # plaquinha "Morozov S. I."
    with xf(0.1, 2.3, 0.15):                                                      # cadeira de Sergei, empurrada
        box(LT, (0, 0, 0.48), (0.5, 0.5, 0.1))
        box(LT, (0, 0.22, 0.85), (0.5, 0.08, 0.7))
        for dx in (-0.2, 0.2):
            for dy in (-0.2, 0.2):
                box(WD, (dx, dy, 0.22), (0.05, 0.05, 0.44), col=False)
    with xf(0.45, 0.35, math.pi + 0.3):                                           # cadeira de visita, puxada para trás
        box(LT, (0, 0, 0.45), (0.46, 0.46, 0.08))
        box(LT, (0, 0.2, 0.8), (0.46, 0.07, 0.62))
        for dx in (-0.18, 0.18):
            for dy in (-0.18, 0.18):
                box(WD, (dx, dy, 0.2), (0.045, 0.045, 0.4), col=False)

    # ---- sofá, mesa de centro, criado-mudo com gravador de fita, samovar --------------------------------
    with xf(2.45, -0.6, -math.pi / 2):  # costas do sofá contra a parede leste
        box(LT, (0, 0, 0.25), (2.0, 0.9, 0.5))
        box(LT, (0, 0.38, 0.75), (2.0, 0.18, 0.55))
        for dx in (-0.95, 0.95):
            box(LT, (dx, 0, 0.55), (0.18, 0.9, 0.4))
    with xf(1.15, -0.6):
        box(WD, (0, 0, 0.45), (0.7, 1.1, 0.05))
        for dx in (-0.3, 0.3):
            for dy in (-0.5, 0.5):
                box(WD, (dx, dy, 0.21), (0.05, 0.05, 0.42), col=False)
    with xf(2.6, 1.05):                                                       # criado-mudo com o gravador da Lena
        box(WD, (0, 0, 0.3), (0.45, 0.4, 0.6))
        box(MT, (0, 0, 0.66), (0.38, 0.28, 0.1), col=False)
        for dx in (-0.09, 0.09):
            cyl(BLACK, (dx, 0.0, 0.725), 0.075, 0.02, n=10, col=False)       # carretéis
        for k in range(3):
            flat(P_TAPE, (-0.1 + k * 0.1, -0.1, 0.62), (0.09, 0.05, 0.04), rz=0.3 * k)
    with xf(-2.15, -1.15):                                                    # mesinha com samovar
        box(WD, (0, 0, 0.38), (0.55, 0.55, 0.04))
        for dx in (-0.22, 0.22):
            for dy in (-0.22, 0.22):
                box(WD, (dx, dy, 0.18), (0.04, 0.04, 0.36), col=False)
        cyl(BRASS, (0, 0, 0.58), 0.13, 0.34, n=10, col=False)
        cyl(BRASS, (0, 0, 0.8), 0.09, 0.11, n=10, r2=0.05, col=False)
        cyl(BRASS, (0, 0, 0.88), 0.05, 0.05, n=8, col=False)
        box(BRASS, (0.17, 0, 0.62), (0.1, 0.03, 0.03), col=False)
    with xf(-2.6, -2.3):                                                      # arquivo de aço com o rádio
        box(MT, (0, 0, 0.65), (0.5, 0.6, 1.3))
        for k in range(4):
            box(BLACK, (0, -0.31, 0.2 + k * 0.3), (0.4, 0.02, 0.22), col=False)
            box(MT, (0, -0.33, 0.2 + k * 0.3), (0.12, 0.02, 0.03), col=False)
        box(WD, (0, 0, 1.40), (0.34, 0.16, 0.2), col=False, rz=0.1)
        box(BLACK, (-0.06, -0.082, 1.40), (0.16, 0.01, 0.12), col=False, rz=0.1)
        box(AMBER, (0.1, -0.082, 1.44), (0.08, 0.01, 0.03), col=False, rz=0.1)
        box(MT, (0.1, -0.085, 1.37), (0.03, 0.02, 0.03), col=False, rz=0.1)
    with xf(2.8, 1.6):                                                        # abajur de pé
        cyl(MT, (0, 0, 0.8), 0.02, 1.6, n=6)
        box(MT, (0, 0, 0.02), (0.3, 0.3, 0.04), col=False)
        cyl(SHADE, (0, 0, 1.55), 0.22, 0.3, n=8, r2=0.12, col=False)
    with xf(0.95, -2.45):                                                     # cabideiro com casaco e ushanka
        cyl(WD, (0, 0, 0.9), 0.025, 1.8, n=6)
        box(WD, (0, 0, 0.03), (0.4, 0.4, 0.06), col=False)
        box(COAT, (0, 0.02, 1.35), (0.42, 0.14, 0.9), col=False)
        box(COAT, (0.12, 0.02, 1.55), (0.2, 0.12, 0.3), col=False, rz=0.3)
    cyl(MT, (0, -hy + 0.25, H - 0.35), 0.05, Wd, n=8, axis="x", col=False)       # canos de aquecimento
    cyl(MT, (-hx + 0.3, -hy + 0.25, H / 2 - 0.2), 0.04, H - 0.5, n=8, col=False)
    box(BLACK, (0, 0.0, H - 0.5), (0.015, 0.015, 0.8), col=False)                # pendente com abajur de tecido
    cyl(SHADE, (0, 0.0, H - 0.98), 0.30, 0.26, n=10, r2=0.13, col=False)
    box(CITY, (0, 0.0, H - 1.09), (0.07, 0.07, 0.07), col=False)
    # ---- detalhes de vida: rodapé, interruptor, tomadas, grade, lixeira, canecas e papéis na mesa ---------------------------------
    props.baseboard(WD, hx, hy, 0.12, gaps=[("S", 1.6, 2.6), ("N", 2.3, 3.2)])
    props.switch("S", 1.4, -hy)
    props.outlet("W", -hx, 1.0, 0.35)
    props.outlet("E", hx, 2.0, 0.35)
    props.vent("S", 0.0, -hy, 2.8)
    props.bin_(-1.2, 2.3)
    props.mug(-0.75, 1.2, 0.77)
    props.papers(0.9, 1.75, 0.77, n=3, seed=7)
    props.cable(BLACK, [(-0.85, 1.55, 0.78), (-1.3, 1.9, 0.02), (-1.6, 2.4, 0.02)])
    # ---- autenticidade 1993: guia de TV, Prima, rublos, cinzeiro, copos de chá, fechaduras e olho mágico ---------------------------
    props.flat_tex("tv_guide", 1.15, -0.95, 0.478, 0.20, 0.26, rz=0.2)
    props.flat_tex("prima_pack", 1.0, -0.35, 0.478, 0.08, 0.11, rz=-0.5)
    props.flat_tex("ruble_note", 0.8, -0.45, 0.478, 0.16, 0.08, rz=0.4)
    props.podstakannik(1.3, -0.45, 0.475)
    props.ashtray(1.35, -0.85, 0.475)
    props.door_security("S", 2.1, -hy + 0.045)
    props.door_security("N", 2.75, hy - 0.045)
    kit.export("gabinete")


if __name__ == "__main__":
    kit.reset()
    gabinete()
