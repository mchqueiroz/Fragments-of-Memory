"""Porão do Kosmos (Cena 6, 19/ago/1991, linha F): o refúgio de Misha na noite do golpe.

Uso: blender -b -P tools/porao.py        -> art/models/porao.glb
Dramaturgia: mesa de luz com as plantas do Lethe, TV velha no balé em todos os canais, rádio com os anúncios do Comitê de
Emergência, champagne sem abrir, escadaria para a rua, o casaco de Irina com o broche da KGB. A maleta e o copo que vibra
com os tanques entram pelo script. Eixos: X leste, Y norte (frente do jogador), Z cima. Porta ao sul.
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


def porao():
    random.seed(1991)
    CON, MT, WD, PP = mat("concrete"), mat("metal"), mat("wood_dark"), mat("paper")
    LB, TV, CH = mat("lightbox_plans", emit_tex=True, strength=1.8), mat("tv_swans", emit_tex=True, strength=1.6), mat("champagne_label")
    COAT = mat("coat_irina")
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    GREEN = mat(None, emit=(0.1, 0.35, 0.18), strength=0.3, color=(0.1, 0.3, 0.15))
    GOLD = mat(None, emit=(0.9, 0.7, 0.2), strength=0.6, color=(0.8, 0.6, 0.2))
    RED = mat(None, color=(0.6, 0.08, 0.08))
    DIAL = mat(None, emit=(1.0, 0.65, 0.25), strength=1.5, color=(0.3, 0.2, 0.1))
    W, D, H = 7.0, 5.0, 2.8
    hx, hy = W / 2, D / 2

    # ---- casca de concreto (porta ao sul, x -0.45..0.45) --------------------------------------------------------
    box(CON, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(CON, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(CON, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(CON, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(CON, (0, hy + 0.1, H / 2), (W + 0.4, 0.2, H))
    box(CON, ((-hx - 0.2 - 0.45) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(CON, ((0.45 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(CON, (0, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    for k in range(4):                                                                       # canos ao teto
        cyl(MT, (0, -1.8 + k * 1.2, H - 0.25), 0.05, W, n=8, axis="x", col=False)
    cyl(MT, (-hx + 0.3, 0, H / 2), 0.07, H, n=8, col=False)

    # ---- escadaria para a rua, na parede norte (sobe para o leste) --------------------------------------------------
    for i in range(8):
        box(CON, (-0.5 + 0.4 * i, hy - 0.4, 0.14 * (i + 1)), (0.4, 0.8, 0.28 * (i + 1)))

    # ---- mesa de luz com as plantas, champagne, taça (entra pelo script, vibra) -------------------------------------------------------------------
    box(WD, (0.0, 1.2, 0.74), (2.0, 0.9, 0.05))
    for dx in (-0.9, 0.9):
        box(WD, (dx, 1.2, 0.36), (0.06, 0.8, 0.72), col=False)
    flat(LB, (0.0, 1.2, 0.77), (0.6, 0.45, 0.006))
    cyl(GREEN, (-0.5, 1.3, 0.925), 0.04, 0.32, n=8, col=False)                               # garrafa de champagne, fechada
    flat(CH, (-0.5, 1.255, 0.955), (0.05, 0.005, 0.07))

    # ---- TV velha sobre caixotes (leste), rádio na estante (oeste) -------------------------------------------------------
    box(WD, (hx - 0.4, -0.3, 0.3), (0.8, 0.8, 0.6))
    box(BLACK, (hx - 0.4, -0.3, 0.83), (0.55, 0.5, 0.48), col=False)
    panel(TV, (hx - 0.69, -0.3, 0.85), (0.02, 0.4, 0.32), "-x")
    box(MT, (-hx + 0.25, 0.8, 0.7), (0.4, 1.6, 0.04))                                          # estante e rádio
    box(MT, (-hx + 0.25, 0.0, 0.35), (0.4, 0.04, 0.7))
    box(MT, (-hx + 0.25, 1.6, 0.35), (0.4, 0.04, 0.7))
    box(WD, (-hx + 0.3, 0.8, 0.82), (0.22, 0.34, 0.2), col=False)
    box(DIAL, (-hx + 0.19, 0.8, 0.87), (0.02, 0.18, 0.04), col=False)
    for k in range(4):                                                                       # caixas e latas na estante
        box(random.choice([WD, PP, MT]), (-hx + 0.25, 0.2 + k * 0.35, 0.15), (0.3, 0.22, 0.3), col=False)

    # ---- casaco de Irina com o broche (parede norte, oeste) -----------------------------------------------------------------
    box(WD, (-2.4, hy - 0.04, 1.8), (0.5, 0.06, 0.06), col=False)
    box(WD, (-2.4, hy - 0.1, 1.78), (0.03, 0.08, 0.03), col=False)                             # gancho
    box(COAT, (-2.4, hy - 0.14, 1.3), (0.45, 0.14, 1.0), col=False)
    box(GOLD, (-2.3, hy - 0.22, 1.55), (0.04, 0.02, 0.04), col=False)                           # broche
    box(RED, (-2.3, hy - 0.235, 1.55), (0.02, 0.01, 0.02), col=False)
    # ---- detalhes de vida: rodapé, extintor, canos, caixotes, balde, cabos, garrafas, papéis, grade, relógio -------------------------
    props.baseboard(MT, hx, hy, 0.15, gaps=[("S", -0.45, 0.45)])
    props.extinguisher("S", 1.8, -hy)
    props.pipe_y(MT, 2.0, 2.4, -2.4, 2.4, 0.04)
    props.pipe_y(MT, 2.4, 2.4, -2.4, 2.4, 0.04)
    props.crate(-3.0, -1.5)
    props.crate(-3.0, -1.5, 0.45)
    props.crate(-2.4, -2.0, 0.0, 0.4, rz=0.3)
    props.bucket(-3.1, 2.0)
    props.bin_(2.6, -2.0)
    props.cable(BLACK, [(3.0, -0.3, 0.02), (2.0, -0.8, 0.02), (0.8, 0.3, 0.02)], 0.02)
    props.bottle(-3.25, 0.5, 0.72, h=0.3)
    props.bottle(-3.25, 1.1, 0.72, color=(0.25, 0.15, 0.08), h=0.25)
    props.papers(-0.9, 1.0, 0.775, n=4, seed=6)
    props.vent("S", -2.0, -hy, 2.3)
    props.switch("S", 1.0, -hy)
    props.outlet("E", hx, 1.5, 0.35)
    props.wall_clock("S", 2.6, -hy, 2.2)
    # ---- autenticidade: avisos, cartaz velho, painel de incêndio, rublos, talão, Prima, cinzeiro, porta com corrente -------------------
    props.poster("sign_nosmoke", "S", -1.2, -hy, 1.9, 0.3, 0.3)
    props.poster("fire_board", "E", hx, -1.7, 1.4, 0.5, 0.7)
    props.poster("poster_slogan", "W", -hx, -1.5, 1.8, 1.0, 0.65)
    props.flat_tex("ruble_note", 0.8, 1.3, 0.777, 0.16, 0.08, rz=0.2)
    props.flat_tex("talon", 0.9, 1.0, 0.777, 0.10, 0.10, rz=-0.3)
    props.flat_tex("prima_pack", -0.2, 1.4, 0.777, 0.08, 0.11, rz=0.6)
    props.ashtray(0.6, 0.95, 0.775)
    props.flat_tex("tv_guide", -3.0, -1.5, 0.905, 0.20, 0.26, rz=0.3)
    props.door("S", 0.0, -hy, 0.9, 2.05, angle=0.45)
    kit.export("porao")


if __name__ == "__main__":
    kit.reset()
    porao()
