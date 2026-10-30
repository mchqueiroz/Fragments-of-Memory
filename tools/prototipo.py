"""Sala do Protótipo (Cena 4, jul/1991, linha F): o laboratório antigo onde o Lethe nasceu, em luz de verão.

Uso: blender -b -P tools/prototipo.py        -> art/models/prototipo.glb
Dramaturgia: a caixa de latão "ЛЕТА" com fita "НЕ ТРОГАТЬ", o quadro-negro cujas equações terminam num ∅, osciloscópios,
gravador de fita com a fita "ЛЕНА 1991", o caderno de Lena com nomes riscados, xícaras lascadas, fotos de Lena jovem.
Eixos: X leste, Y norte (frente do jogador), Z cima. Porta ao sul; janela ao norte.
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


def prototipo():
    random.seed(1991)
    PL, GRN, MT, WD = mat("plaster"), mat("paint_green"), mat("metal"), mat("wood_dark")
    PARQ = mat("parquet_square")
    BB, PROTO, TAPE, NB, PIC = mat("blackboard"), mat("proto_panel"), mat("tape_label"), mat("notebook_names"), mat("pic_lena")
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    WHITE = mat(None, color=(0.80, 0.78, 0.72))
    SCOPE = mat(None, emit=(0.2, 1.0, 0.4), strength=2.0, color=(0.05, 0.2, 0.1))
    SUN = mat(None, emit=(1.0, 0.9, 0.6), strength=2.5, color=(0, 0, 0))
    W, D, H = 6.0, 5.0, 3.0
    hx, hy = W / 2, D / 2

    # ---- casca (porta ao sul, x -0.45..0.45; janela ao norte, x -1.2..1.2) --------------------------------------
    box(PARQ, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, ((-hx - 0.2 - 0.45) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(PL, ((0.45 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(PL, (0, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    box(PL, ((-hx - 0.2 - 1.2) / 2, hy + 0.1, H / 2), (hx + 0.2 - 1.2, 0.2, H))
    box(PL, ((1.2 + hx + 0.2) / 2, hy + 0.1, H / 2), (hx + 0.2 - 1.2, 0.2, H))
    box(PL, (0, hy + 0.1, 0.9 / 2), (2.4, 0.2, 0.9))
    box(PL, (0, hy + 0.1, 2.3 + (H - 2.3) / 2), (2.4, 0.2, H - 2.3))
    # (janela aberta para o Kosmos: o céu e o prédio vêm do script, Room.backdrop_kosmos)
    for dx in (-1.2, 0.0, 1.2):
        box(WD, (dx, hy - 0.04, 1.6), (0.05, 0.1, 1.45), col=False)
    for z in (0.9, 1.6, 2.3):
        box(WD, (0, hy - 0.04, z), (2.5, 0.1, 0.05), col=False)
    for (c, s) in (((-hx + 0.02, 0, 0.6), (0.04, D, 1.2)), ((hx - 0.02, 0, 0.6), (0.04, D, 1.2)),
                   ((0, -hy + 0.02, 0.6), (W, 0.04, 1.2))):
        box(GRN, c, s, col=False)

    # ---- quadro-negro (oeste), com as equações que terminam no vazio ---------------------------------------------
    panel(BB, (-hx + 0.04, 0.3, 1.6), (0.04, 2.6, 1.3), "+x")
    box(WD, (-hx + 0.05, 0.3, 0.9), (0.06, 2.7, 0.04), col=False)                               # calha de giz

    # ---- bancada central: protótipo, gravador, caderno, xícaras --------------------------------------------------
    box(WD, (0.2, 1.6, 0.76), (2.6, 0.9, 0.05))
    for dx in (-1.2, 1.2):
        box(WD, (0.2 + dx, 1.6, 0.37), (0.06, 0.8, 0.74), col=False)
    box(MT, (0.0, 1.6, 0.97), (0.5, 0.4, 0.36), col=False)                                       # a caixa do Lethe
    panel(PROTO, (0.0, 1.39, 0.97), (0.46, 0.02, 0.32), "-y")
    box(BLACK, (0.9, 1.6, 0.85), (0.32, 0.22, 0.12), col=False)                                  # gravador de fita
    flat(TAPE, (0.9, 1.5, 0.911), (0.12, 0.06, 0.004))
    flat(NB, (-0.8, 1.5, 0.787), (0.14, 0.19, 0.006), rz=0.2)                                    # caderno de Lena
    for (x, y) in ((-0.45, 1.85), (-0.3, 1.75)):                                                 # xícaras de porcelana lascada
        cyl(WHITE, (x, y, 0.83), 0.045, 0.07, n=10, col=False)

    # ---- bancada leste: osciloscópios (o tabuleiro de Sergei entra pelo script) ---------------------------------------
    box(WD, (hx - 0.5, 0.2, 0.76), (0.8, 2.2, 0.05))
    for dy in (-0.9, 0.9):
        box(WD, (hx - 0.5, 0.2 + dy, 0.37), (0.7, 0.06, 0.74), col=False)
    for y in (0.7, 0.0):
        box(MT, (hx - 0.5, y, 1.0), (0.45, 0.4, 0.4), col=False)
        box(SCOPE, (hx - 0.72, y, 1.05), (0.02, 0.28, 0.22), col=False)
    panel(PIC, (hx - 0.03, 1.55, 1.7), (0.04, 0.5, 0.6), "-x")                                   # Lena jovem
    box(MT, (-1.6, hy - 0.4, 1.0), (0.8, 0.5, 2.0))                                              # armário de aço
    # ---- detalhes de vida: rodapé, radiador, livros, cabos, relógio, caixote, lixeira, luminárias ----------------------------------
    props.baseboard(WD, hx, hy, 0.12, gaps=[("S", -0.45, 0.45)])
    props.radiator("N", 0.0, hy, w=1.4)
    props.switch("S", 0.9, -hy)
    props.outlet("E", hx, -1.5, 0.35)
    props.outlet("W", -hx, -1.8, 0.35)
    props.books(-1.95, hy - 0.4, 2.0, n=9, seed=4)
    props.papers(-1.2, 1.7, 0.79, n=3, seed=5)
    props.bottle(-1.0, 1.95, 0.79)
    props.cable(BLACK, [(2.2, 0.7, 0.02), (1.2, 0.5, 0.02), (0.4, 1.1, 0.02)], 0.02)
    props.cable(BLACK, [(0.0, 1.4, 0.8), (0.5, 1.2, 0.79), (0.9, 1.4, 0.79)])
    props.wall_clock("S", -2.0, -hy, 2.2)
    props.crate(2.4, -1.8, 0.0, 0.45)
    props.bin_(-2.4, -2.0)
    props.ceiling_lamp(-1.0, 0.0, H - 0.05)
    props.ceiling_lamp(1.0, 0.0, H - 0.05)
    # ---- autenticidade: cartaz, proibido fumar, busto de Lenin, jalecos, chá, Prima, cinzeiro, passe, porta ----------------------------
    props.poster("poster_slogan", "S", 1.9, -hy, 2.1, 1.2, 0.8)
    props.poster("sign_nosmoke", "S", -1.0, -hy, 1.9, 0.3, 0.3)
    props.bust(-1.2, hy - 0.4, 2.0)
    props.lab_coat("W", -hx, -2.2)
    props.podstakannik(-0.55, 1.4, 0.79)
    props.podstakannik(0.2, 1.95, 0.79)
    props.flat_tex("prima_pack", -0.9, 1.45, 0.791, 0.08, 0.11, rz=0.4)
    props.flat_tex("pass_card", 0.6, 1.8, 0.791, 0.10, 0.065, rz=-0.3)
    props.ashtray(1.2, 1.8, 0.79)
    props.door("S", 0.0, -hy, 0.9, 2.05, angle=0.5)
    kit.export("prototipo")


if __name__ == "__main__":
    kit.reset()
    prototipo()
