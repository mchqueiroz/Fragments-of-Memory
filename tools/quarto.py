"""Quarto de Lena (Cena 7, T-6h, linha A): o quarto parado, onde a voz da fita ainda toca.

Uso: blender -b -P tools/quarto.py        -> art/models/quarto.glb
Dramaturgia: cama feita e manta dobrada com cuidado, chinelos e bengala, gravador com fitas, caderno com "Миша" escrito
dezenas de vezes, frasco de remédios, fotos, janela com gelo, vela junto ao ícone, cartão "Serioja, lembre de mim".
Eixos: X leste, Y norte (frente do jogador), Z cima. Porta ao sul (x 0.75..1.65); janela ao norte.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402, F401

import kit  # noqa: E402
import props  # noqa: E402
from gabinete import flat, panel  # noqa: E402
from kit import box, cyl, mat  # noqa: E402


def quarto():
    random.seed(1992)
    WP, PQ, PL, WD, MT = mat("wallpaper"), mat("parquet"), mat("plaster"), mat("wood_dark"), mat("metal")
    RG, ICON = mat("rug"), mat("icon")
    NB, CARD, FROST = mat("notebook_misha"), mat("card_lena"), mat("frost", emit_tex=True, strength=0.9)
    P_LENA, P_TEAM, TAPE = mat("pic_lena"), mat("pic_team"), mat("tape_label")
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    LINEN = mat(None, color=(0.78, 0.76, 0.70))
    WOOL = mat(None, color=(0.42, 0.20, 0.22))
    SLIPPER = mat(None, color=(0.45, 0.18, 0.20))
    AMBER = mat(None, emit=(0.55, 0.30, 0.08), strength=0.5, color=(0.45, 0.25, 0.08))
    FLAME = mat(None, emit=(1.0, 0.7, 0.25), strength=5.0, color=(1, 0.7, 0.2))
    WAX = mat(None, color=(0.88, 0.85, 0.75))
    W, D, H = 4.0, 3.6, 2.7
    hx, hy = W / 2, D / 2

    # ---- casca (porta ao sul, x 0.75..1.65; janela ao norte, x -1.1..0.1, peitoril 0.9) -----------------------------------
    box(PQ, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(WP, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(WP, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(WP, ((-hx - 0.2 + 0.75) / 2, -hy - 0.1, H / 2), (0.75 + hx + 0.2, 0.2, H))
    box(WP, ((1.65 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 1.65, 0.2, H))
    box(WP, (1.2, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    box(WP, ((-hx - 0.2 - 1.1) / 2, hy + 0.1, H / 2), (hx + 0.2 - 1.1, 0.2, H))
    box(WP, ((0.1 + hx + 0.2) / 2, hy + 0.1, H / 2), (hx + 0.2 - 0.1, 0.2, H))
    box(WP, (-0.5, hy + 0.1, 0.45), (1.2, 0.2, 0.9))
    box(WP, (-0.5, hy + 0.1, 2.0 + (H - 2.0) / 2), (1.2, 0.2, H - 2.0))
    box(FROST, (-0.5, hy + 0.0, 1.45), (1.1, 0.02, 1.05), col=False)                        # vidro com gelo, luz azul fria
    for dx in (-1.1, 0.1, -0.5):
        box(WD, (dx, hy - 0.04, 1.45), (0.05, 0.1, 1.15), col=False)
    for z in (0.9, 1.45, 2.0):
        box(WD, (-0.5, hy - 0.04, z), (1.3, 0.1, 0.05), col=False)
    box(RG, (0.0, -0.2, 0.011), (1.6, 2.0, 0.02), col=False)                                  # tapete

    # ---- cama feita, manta dobrada com cuidado, travesseiro, cartão dela ------------------------------------------------------
    box(WD, (-1.3, 0.2, 0.25), (0.9, 2.0, 0.5))
    box(LINEN, (-1.3, 0.25, 0.53), (0.84, 1.9, 0.06), col=False)
    box(LINEN, (-1.3, 0.95, 0.6), (0.6, 0.3, 0.1), col=False)                               # travesseiro
    box(WOOL, (-1.3, -0.62, 0.62), (0.7, 0.4, 0.12), col=False)                              # manta dobrada ao pé
    flat(CARD, (-1.3, 0.95, 0.655), (0.2, 0.14, 0.004), rz=0.1)

    # ---- chinelos e bengala ----------------------------------------------------------------------------------------------------------
    for dx, rz in ((-0.05, 0.1), (0.12, -0.05)):
        box(SLIPPER, (-0.65 + dx, -0.3, 0.03), (0.1, 0.26, 0.06), col=False, rz=rz)
    cyl(WD, (-0.52, -0.85, 0.45), 0.012, 0.9, n=6, col=False)                              # bengala encostada na cama
    box(WD, (-0.52, -0.82, 0.9), (0.02, 0.1, 0.03), col=False)

    # ---- criado-mudo: gravador, fitas, caderno, remédios --------------------------------------------------------------------------
    box(WD, (-0.35, 1.5, 0.28), (0.7, 0.45, 0.56))
    box(BLACK, (-0.55, 1.5, 0.62), (0.3, 0.2, 0.1), col=False)                              # gravador de fita
    for dx in (-0.08, 0.08):
        cyl(MT, (-0.55 + dx, 1.5, 0.685), 0.04, 0.02, n=10, col=False)
    for k in range(3):
        flat(TAPE, (-0.55, 1.3 + k * 0.01, 0.57 + k * 0.03), (0.09, 0.05, 0.03), rz=0.3 * k)    # pilha de fitas "ЛЕНА"
    flat(NB, (-0.25, 1.45, 0.566), (0.15, 0.2, 0.006), rz=0.2)                              # caderno
    cyl(AMBER, (-0.08, 1.6, 0.62), 0.025, 0.1, n=8, col=False)                              # frasco de remédios

    # ---- fotos na cabeceira, ícone com vela (leste) -----------------------------------------------------------------------------------
    panel(P_LENA, (-hx + 0.03, 0.2, 1.7), (0.04, 0.46, 0.58), "+x")
    panel(P_TEAM, (-hx + 0.03, -0.55, 1.55), (0.04, 0.55, 0.36), "+x")
    box(WD, (hx - 0.1, 0.8, 1.52), (0.2, 0.34, 0.03), col=False)                           # prateleira do ícone
    panel(ICON, (hx - 0.03, 0.8, 1.95), (0.02, 0.32, 0.44), "-x")
    cyl(WAX, (hx - 0.12, 0.8, 1.6), 0.02, 0.12, n=8, col=False)                              # vela
    box(FLAME, (hx - 0.12, 0.8, 1.68), (0.016, 0.016, 0.03), col=False)
    box(WD, (1.4, 1.2, 0.45), (0.5, 0.5, 0.9))                                               # cômoda
    # ---- detalhes de vida: rodapé, radiador, cortinas, livros e vaso na cômoda, relógio, tomada ------------------------------------
    props.baseboard(WD, hx, hy, 0.11, gaps=[("S", 0.75, 1.65)])
    props.radiator("N", -0.5, hy, w=1.0)
    props.switch("S", 0.5, -hy)
    props.outlet("E", hx, -1.2, 0.35)
    props.books(1.2, 1.2, 0.9, n=6, seed=8, height=(0.14, 0.22))
    props.jar(1.55, 1.1, 0.9, fill=(0.3, 0.45, 0.2))
    props.wall_clock("S", -1.2, -hy, 2.0)
    for cx in (-1.25, 0.25):                                                                  # cortinas
        box(props._c(0.35, 0.28, 0.30), (cx, hy - 0.1, 1.5), (0.3, 0.08, 1.9), col=False)
    # ---- autenticidade: copo de chá ao lado dos remédios, porta com corrente ----------------------------------------------------------
    props.podstakannik(-0.4, 1.7, 0.56)
    props.door("S", 1.2, -hy, 0.9, 2.05, angle=0.35)
    kit.export("quarto")


if __name__ == "__main__":
    kit.reset()
    quarto()
