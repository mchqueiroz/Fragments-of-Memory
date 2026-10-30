"""Cozinha dos Volkov (Cena 2, jun/1991, linha F): um apartamento "khrushchevka" apertado, onde Boris esperou o irmão.

Uso: blender -b -P tools/cozinha.py        -> art/models/cozinha.glb
Dramaturgia: oleado com marcas de copo, prato de comida coberto e frio (Boris esperou), garrafa de vodca pela metade, quepe e
jaqueta de milícia no gancho, o tabuleiro do pai, a foto dos pais com o canto queimado, calendário de junho de 1991.
Eixos: X leste, Y norte (frente do jogador), Z cima. A janela dá para o pátio, ao pôr do sol.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402, F401

import kit  # noqa: E402
import props  # noqa: E402
from gabinete import flat, panel  # noqa: E402
from kit import box, cyl, mat, xf  # noqa: E402


def cozinha():
    random.seed(1991)
    LINO, PL, GRN, WD = mat("linoleum"), mat("plaster"), mat("paint_green"), mat("wood_dark")
    MT, OIL, PP, CUR = mat("metal"), mat("oilcloth"), mat("paper"), mat("cardigan")
    SHADE, BRASS = mat("lampshade"), mat("brass")
    P_PAR, P_CAL = mat("pic_parents"), mat("calendar_1991")
    WHITE = mat(None, color=(0.80, 0.78, 0.72))
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    GLASS = mat(None, emit=(0.10, 0.35, 0.18), strength=0.4, color=(0.1, 0.3, 0.15))
    DUSK = mat(None, emit=(0.95, 0.52, 0.28), strength=1.1, color=(0, 0, 0))
    BLOCK = mat(None, color=(0.10, 0.08, 0.10))
    WIN = mat(None, emit=(1.0, 0.8, 0.45), strength=2.0, color=(0, 0, 0))
    DIAL = mat(None, emit=(1.0, 0.65, 0.25), strength=1.5, color=(0.3, 0.2, 0.1))
    JACKET = mat("uniform")
    Wd, Dd, H = 3.6, 3.0, 2.6
    hx, hy = Wd / 2, Dd / 2

    # ---- casca: linóleo, forro, paredes (porta no sul, janela no norte) -----------------------------
    box(LINO, (0, 0, -0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    box(PL, (-hx - 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    box(PL, (hx + 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    box(PL, ((-hx - 0.2 + 0.5) / 2, -hy - 0.1, H / 2), (0.5 + hx + 0.2, 0.2, H))     # sul, com a porta entre x=0.5 e 1.4
    box(PL, ((1.4 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 1.4, 0.2, H))
    box(PL, (0.95, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    sill, head = 0.95, 2.1
    box(PL, ((-hx - 0.2 - 0.7) / 2, hy + 0.1, H / 2), (hx + 0.2 - 0.7, 0.2, H))     # norte, janela x -0.7..0.5
    box(PL, ((0.5 + hx + 0.2) / 2, hy + 0.1, H / 2), (hx + 0.2 - 0.5, 0.2, H))
    box(PL, (-0.1, hy + 0.1, sill / 2), (1.2, 0.2, sill))
    box(PL, (-0.1, hy + 0.1, head + (H - head) / 2), (1.2, 0.2, H - head))
    for (c, s) in (((-hx + 0.02, 0, 0.6), (0.04, Dd, 1.2)), ((hx - 0.02, 0, 0.6), (0.04, Dd, 1.2)),
                   ((0, hy - 0.02, 0.6), (Wd, 0.04, 1.2)), ((0, -hy + 0.02, 0.6), (Wd, 0.04, 1.2))):
        box(GRN, c, s, col=False)
        box(WHITE, (c[0], c[1], 1.23), (max(s[0], 0.06), max(s[1], 0.06), 0.04), col=False)

    # ---- janela para o pátio, ao pôr do sol; Spidola no parapeito --------------------------------------
    for dx in (-0.72, 0.52):
        box(WD, (dx, hy - 0.04, (sill + head) / 2), (0.06, 0.1, head - sill + 0.1), col=False)
    for z in (sill - 0.03, head + 0.03):
        box(WD, (-0.1, hy - 0.04, z), (1.3, 0.1, 0.06), col=False)
    box(WD, (-0.1, hy - 0.04, (sill + head) / 2), (0.03, 0.06, head - sill), col=False)
    box(DUSK, (-0.1, hy + 0.12, (sill + head) / 2), (1.2, 0.02, head - sill), col=False)
    for i in range(7):                                                                   # prédios do pátio
        x = -0.65 + i * 0.18
        h = random.uniform(0.4, 0.95)
        box(BLOCK, (x, hy + 0.5, 1.0 + h / 2), (0.16, 0.1, h), col=False)
        for _ in range(random.randint(0, 2)):
            box(WIN, (x + random.uniform(-0.05, 0.05), hy + 0.44, 1.0 + random.uniform(0.1, h)), (0.04, 0.02, 0.04), col=False)
    box(WD, (-0.1, hy - 0.16, sill - 0.04), (1.35, 0.3, 0.06))                          # parapeito
    box(WD, (-0.35, hy - 0.2, sill + 0.09), (0.34, 0.16, 0.2), col=False)                 # rádio Spidola
    box(BLACK, (-0.42, hy - 0.285, sill + 0.09), (0.14, 0.01, 0.1), col=False)
    box(DIAL, (-0.28, hy - 0.285, sill + 0.14), (0.1, 0.01, 0.03), col=False)
    for dx in (-0.8, 0.6):
        box(CUR, (dx, hy - 0.2, 1.45), (0.3, 0.1, 1.6), col=False, rz=random.uniform(-0.05, 0.05))
    box(MT, (-0.1, hy - 0.2, 2.265), (1.8, 0.025, 0.025), col=False)                        # varão

    # ---- porta e gancheira: quepe e jaqueta de Boris -------------------------------------------------------
    for dx in (-0.5, 0.5):
        box(WD, (0.95 + dx, -hy + 0.04, 1.05), (0.1, 0.12, 2.1), col=False)
    box(WD, (0.95, -hy + 0.04, 2.15), (1.1, 0.12, 0.1), col=False)
    box(WD, (0.95, -hy + 0.02, 1.0), (0.88, 0.05, 2.0), col=True)
    box(WD, (-0.3, -hy + 0.05, 1.7), (0.9, 0.04, 0.08), col=False)                      # tábua de ganchos
    box(JACKET, (-0.5, -hy + 0.12, 1.25), (0.36, 0.1, 0.8), col=False)                  # jaqueta de milícia
    box(JACKET, (-0.05, -hy + 0.10, 1.62), (0.28, 0.2, 0.09), col=False)                # quepe
    box(WHITE, (-0.05, -hy + 0.2, 1.64), (0.12, 0.01, 0.05), col=False)                 # insígnia

    # ---- mesa com oleado, banquetas, prato coberto, vodca, isqueiro de Boris ----------------------------------
    with xf(-1.15, 0.2):
        box(WD, (0, 0, 0.74), (0.8, 1.2, 0.05))
        flat(OIL, (0, 0, 0.768), (0.8, 1.2, 0.006))
        for dx in (-0.34, 0.34):
            for dy in (-0.54, 0.54):
                box(WD, (dx, dy, 0.36), (0.05, 0.05, 0.72), col=False)
        cyl(WHITE, (0.05, -0.2, 0.775), 0.11, 0.02, n=10, col=False)                       # prato coberto por outro prato
        cyl(WHITE, (0.05, -0.2, 0.80), 0.11, 0.02, n=10, col=False)
        cyl(GLASS, (-0.15, 0.25, 0.86), 0.035, 0.2, n=8, col=False)                         # garrafa de vodca, pela metade
        for (x, y) in ((0.0, 0.32), (0.18, 0.18)):
            cyl(mat(None, emit=(0.8, 0.8, 0.8), strength=0.1, color=(0.7, 0.7, 0.7)), (x, y, 0.8), 0.025, 0.07, n=8, col=False)
        box(MT, (0.2, -0.05, 0.775), (0.045, 0.035, 0.012), col=False, rz=0.5)             # isqueiro de Boris
        flat(PP, (-0.2, -0.35, 0.774), (0.07, 0.045, 0.008), rz=0.3)                        # caixa de fósforos
    for (x, y, rz) in ((-0.5, 0.05, 0.4), (-0.5, 0.75, -0.3), (-1.2, -0.65, 0.1)):         # banquetas
        with xf(x, y, rz):
            box(WD, (0, 0, 0.45), (0.34, 0.34, 0.04))
            for dx in (-0.13, 0.13):
                for dy in (-0.13, 0.13):
                    box(WD, (dx, dy, 0.22), (0.04, 0.04, 0.44), col=False)
    box(mat("trousers"), (-0.5, 0.05, 0.62), (0.34, 0.1, 0.34), col=False)                  # jaqueta de Misha na banqueta

    # ---- fogão com chaleira, armário, geladeira ZIL, pia ------------------------------------------------------
    with xf(hx - 0.35, 0.2):
        box(WHITE, (0, 0, 0.45), (0.6, 0.7, 0.9))
        box(BLACK, (-0.2, 0, 0.91), (0.2, 0.2, 0.02), col=False)
        box(BLACK, (-0.2, 0.28, 0.91), (0.2, 0.2, 0.02), col=False)
        cyl(MT, (-0.2, 0, 1.03), 0.1, 0.22, n=10, col=False)                                  # chaleira
        box(MT, (-0.2, -0.13, 1.1), (0.03, 0.12, 0.03), col=False)                            # bico
        for k in range(4):
            cyl(BLACK, (0.3, -0.25 + k * 0.17, 0.7), 0.02, 0.03, n=6, col=False, axis="x")
    box(WD, (hx - 0.22, 0.2, 1.9), (0.4, 1.0, 0.7))                                           # armário suspenso
    panel(P_CAL, (hx - 0.03, -0.55, 1.5), (0.04, 0.4, 0.5), "-x")                           # calendário
    with xf(-hx + 0.4, -hy + 0.4):
        box(WHITE, (0, 0, 0.7), (0.6, 0.6, 1.4))
        box(BLACK, (0.31, 0.0, 1.0), (0.01, 0.02, 0.3), col=False)
    with xf(0.9, hy - 0.3):
        box(WHITE, (0, 0, 0.45), (0.7, 0.5, 0.9))
        box(MT, (0, 0.1, 1.0), (0.5, 0.3, 0.05), col=False)
        cyl(MT, (0, 0.2, 1.1), 0.015, 0.2, n=6, col=False)
        cyl(WHITE, (0.1, 0.0, 0.93), 0.1, 0.03, n=10, col=False)                              # louça na pia

    # ---- foto dos pais, tabuleiro do pai (modelo separado), lâmpada nua com abajur barato --------------------
    panel(P_PAR, (-hx + 0.03, 0.2, 1.75), (0.04, 0.72, 0.56), "+x")
    box(MT, (0, 0, H - 0.4), (0.012, 0.012, 0.8), col=False)
    cyl(SHADE, (0, 0, H - 0.88), 0.2, 0.2, n=10, r2=0.09, col=False)
    box(WIN, (0, 0, H - 0.96), (0.06, 0.06, 0.06), col=False)

    # ---- detalhes de vida: rodapé, panelas, pão, prateleira de potes, relógio, canos, tomadas, balde, caixote ------------------
    props.baseboard(WD, hx, hy, 0.11, gaps=[("S", 0.5, 1.4)])
    props.pot(1.25, 0.5, 0.92, 0.13, 0.17)                                                   # panela no fogo
    props.pot(1.25, 0.48, 1.09, 0.135, 0.02, color=(0.4, 0.4, 0.42))                         # tampa
    props.bread(-1.05, 0.65, 0.775)
    props.jar(-1.45, 0.6, 0.775, fill=(0.75, 0.70, 0.60))                                    # sal
    props.mug(-0.85, 0.55, 0.775)
    props.papers(-1.45, 0.05, 0.775, n=2, seed=4)
    box(WD, (1.2, hy - 0.12, 1.5), (0.9, 0.2, 0.04), col=False)                              # prateleira de potes ao lado da janela
    for k, fill in enumerate(((0.55, 0.35, 0.12), (0.6, 0.12, 0.10), (0.30, 0.45, 0.15), (0.75, 0.70, 0.60))):
        props.jar(0.9 + k * 0.2, hy - 0.12, 1.52, fill=fill)
    props.plate(1.55, hy - 0.12, 1.52)
    props.plate(1.55, hy - 0.12, 1.53)
    props.wall_clock("S", -1.2, -hy, 2.0)
    props.switch("S", 1.58, -hy)
    props.outlet("N", 1.3, hy, 0.4)
    props.outlet("E", hx, -0.9, 0.35)
    props.vent("E", hx, -0.9, 2.3)
    props.pipe_z(MT, hx - 0.08, -0.45, 0.0, 2.5)                                             # cano de gás atrás do fogão
    props.pipe_x(MT, hy - 0.15, 2.45, -1.7, 1.7)                                             # cano sob o teto
    props.radiator("N", -0.1, hy, w=1.0)
    props.crate(-1.5, 1.2, 0.0, 0.4, rz=0.15)
    props.bucket(1.45, 1.22)
    props.cable(BLACK, [(-0.2, -1.4, 0.02), (0.0, -1.0, 0.02), (0.3, -0.6, 0.02)])
    # ---- autenticidade 1991: podstakanniki, Belomor/Prima, talão de vodca, rublos, avoska, valenki, potes de tomate, cinzeiro --------
    props.podstakannik(-1.2, 0.45, 0.775)
    props.podstakannik(-0.85, 0.2, 0.775)
    props.flat_tex("prima_pack", -1.3, 0.05, 0.777, 0.09, 0.12, rz=0.4)
    props.flat_tex("talon", -1.45, 0.7, 0.777, 0.10, 0.10, rz=-0.2)
    props.flat_tex("ruble_note", -0.95, -0.2, 0.777, 0.16, 0.08, rz=0.3)
    props.flat_tex("newspaper", -1.15, 0.55, 0.777, 0.34, 0.24, rz=0.15)
    props.ashtray(-0.8, -0.25, 0.775)
    props.avoska("S", -0.2, -hy + 0.05, 1.25)
    props.valenki(0.2, -1.15, 0.3)
    props.jar(-0.6, hy - 0.18, sill - 0.01, fill=(0.70, 0.15, 0.10))                       # conserva entre a cortina e o rádio (o tabuleiro fica no meio)
    props.door_security("S", 0.95, -hy + 0.045)
    kit.export("cozinha")


if __name__ == "__main__":
    kit.reset()
    cozinha()
