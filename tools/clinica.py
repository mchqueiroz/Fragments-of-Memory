"""A Clínica (Cena 10, set/1991, linha F): a enfermaria onde Misha acorda sem memória e ganha outro nome.

Uso: blender -b -P tools/clinica.py        -> art/models/clinica.glb
Dramaturgia: cama de ferro, soro, criado-mudo com o passaporte novo, prontuário "ПЕТРОВ А. И.", espelho sobre a pia, janela
para o outono, porta de vidro fosco com a placa "ПАЛАТА 7". Tinta verde até a cintura, linóleo, radiador pintado.
Eixos: X leste, Y norte (frente do jogador), Z cima. Porta ao sul (x 0.9..1.8); janela ao norte (x -1.3..-0.1).
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


def clinica():
    random.seed(1991)
    LINO, PL, GRN, MT, WD = mat("linoleum"), mat("plaster"), mat("paint_green"), mat("metal"), mat("wood_dark")
    CHART, PASS, VIEW, PLATE = mat("prontuario"), mat("passport"), mat("autumn_view", emit_tex=True, strength=1.3), mat("ward_plate")
    WHITE = mat(None, color=(0.82, 0.82, 0.78))
    SHEET = mat(None, color=(0.86, 0.85, 0.80))
    BLANKET = mat(None, color=(0.40, 0.45, 0.50))
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    GLASS = mat(None, emit=(0.75, 0.85, 0.90), strength=0.5, color=(0.7, 0.8, 0.85))
    FROST = mat(None, emit=(0.85, 0.92, 0.95), strength=1.4, color=(0.8, 0.9, 0.9))
    BAG = mat(None, emit=(0.85, 0.80, 0.55), strength=0.6, color=(0.8, 0.75, 0.5))
    MIRROR = mat(None, emit=(0.10, 0.13, 0.16), strength=0.4, color=(0.1, 0.12, 0.15))
    W, D, H = 4.0, 3.6, 2.8
    hx, hy = W / 2, D / 2

    # ---- casca (porta ao sul x 0.9..1.8; janela ao norte x -1.3..-0.1, peitoril 0.9) -------------------------------------------
    box(LINO, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, ((-hx - 0.2 + 0.9) / 2, -hy - 0.1, H / 2), (0.9 + hx + 0.2, 0.2, H))
    box(PL, ((1.8 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 1.8, 0.2, H))
    box(PL, (1.35, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    box(PL, ((-hx - 0.2 - 1.3) / 2, hy + 0.1, H / 2), (hx + 0.2 - 1.3, 0.2, H))
    box(PL, ((-0.1 + hx + 0.2) / 2, hy + 0.1, H / 2), (hx + 0.2 + 0.1, 0.2, H))
    box(PL, (-0.7, hy + 0.1, 0.45), (1.2, 0.2, 0.9))
    box(PL, (-0.7, hy + 0.1, 2.1 + (H - 2.1) / 2), (1.2, 0.2, H - 2.1))
    for (c, s) in (((-hx + 0.02, 0, 0.7), (0.04, D, 1.4)), ((hx - 0.02, 0, 0.7), (0.04, D, 1.4)),
                   ((0, hy - 0.02, 0.7), (W, 0.04, 1.4)), ((0, -hy + 0.02, 0.7), (W, 0.04, 1.4))):
        box(GRN, c, s, col=False)                                                           # tinta verde até a cintura
    panel(VIEW, (-0.7, hy + 0.02, 1.5), (1.15, 0.02, 1.15), "-y")                           # o outono lá fora
    for dx in (-1.3, -0.1, -0.7):
        box(WD, (dx, hy - 0.04, 1.5), (0.05, 0.1, 1.25), col=False)
    for z in (0.9, 1.5, 2.1):
        box(WD, (-0.7, hy - 0.04, z), (1.3, 0.1, 0.05), col=False)

    # ---- cama de ferro com lençol e cobertor ----------------------------------------------------------------------------------------
    for dy in (-0.95, 1.15):                                                                # cabeceira e pés de ferro
        box(MT, (-1.2, 0.1 + dy * 0.99, 0.55), (0.9, 0.03, 0.65), col=False)
    for dx in (-0.43, 0.43):
        for dy in (-0.95, 1.15):
            box(MT, (-1.2 + dx, 0.1 + dy * 0.99, 0.3), (0.03, 0.03, 0.6), col=False)
    box(MT, (-1.2, 0.1, 0.30), (0.88, 1.95, 0.04))
    box(SHEET, (-1.2, 0.1, 0.40), (0.84, 1.85, 0.16), col=False)                            # colchão
    box(BLANKET, (-1.2, -0.25, 0.50), (0.86, 1.1, 0.06), col=False)
    box(SHEET, (-1.2, 0.85, 0.52), (0.55, 0.32, 0.10), col=False)                           # travesseiro com a marca da cabeça

    # ---- soro em pedestal, criado-mudo, cadeira ---------------------------------------------------------------------------------------
    cyl(MT, (-0.6, 0.5, 0.95), 0.015, 1.9, n=6, col=False)
    box(MT, (-0.6, 0.5, 0.03), (0.4, 0.4, 0.04), col=False)
    box(BAG, (-0.6, 0.5, 1.75), (0.12, 0.04, 0.22), col=False)
    box(MT, (-0.6, 0.5, 1.9), (0.3, 0.02, 0.02), col=False)
    box(BLACK, (-0.78, 0.5, 1.2), (0.01, 0.01, 1.1), col=False)                             # tubo até a cama
    box(WD, (-0.35, 1.5, 0.28), (0.45, 0.45, 0.56))
    flat(PASS, (-0.4, 1.5, 0.585), (0.10, 0.14, 0.01), rz=0.3)                              # passaporte novo
    props.mug(-0.25, 1.65, 0.56)
    box(MT, (0.5, -0.4, 0.22), (0.38, 0.38, 0.04))                                          # banqueta
    for dx in (-0.15, 0.15):
        for dy in (-0.15, 0.15):
            box(MT, (0.5 + dx, -0.4 + dy, 0.1), (0.03, 0.03, 0.2), col=False)

    # ---- armário de aço, pia com espelho, prontuário ---------------------------------------------------------------------------------------
    box(MT, (hx - 0.3, -0.5, 0.9), (0.5, 1.2, 1.8))
    box(GLASS, (hx - 0.56, -0.5, 1.4), (0.01, 0.9, 0.8), col=False)
    box(WHITE, (hx - 0.3, 1.3, 0.8), (0.5, 0.5, 0.15))                                      # pia
    box(WHITE, (hx - 0.3, 1.3, 0.35), (0.12, 0.12, 0.7), col=False)
    cyl(MT, (hx - 0.25, 1.3, 1.0), 0.015, 0.2, n=6, col=False)
    panel(MIRROR, (hx - 0.03, 1.3, 1.6), (0.04, 0.55, 0.7), "-x")
    box(MT, (hx - 0.045, 1.3, 1.6), (0.01, 0.62, 0.77), col=False)
    panel(CHART, (hx - 0.03, -1.3, 1.5), (0.04, 0.32, 0.42), "-x")

    # ---- porta de vidro fosco com a placa da enfermaria --------------------------------------------------------------------------------
    box(WD, (1.35, -hy + 0.02, 1.0), (0.9, 0.04, 2.0), col=False)
    box(FROST, (1.35, -hy + 0.05, 1.45), (0.5, 0.01, 0.7), col=False)
    panel(PLATE, (1.35, -hy + 0.04, 1.95), (0.25, 0.02, 0.12), "+y")

    # ---- vida: rodapé, radiador, relógio, interruptor, lixeira, cartaz e cinzeiro proibido ------------------------------------
    props.baseboard(WD, hx, hy, 0.1, gaps=[("S", 0.9, 1.8)])
    props.radiator("N", -0.7, hy, w=1.0)
    props.wall_clock("E", hx, -1.5, 2.2)
    props.switch("S", 0.6, -hy)
    props.bin_(0.7, 1.4)
    props.poster("sign_nosmoke", "S", -0.6, -hy, 1.8, 0.28, 0.28)
    props.vent("W", -hx, -1.2, 2.3)
    props.podstakannik(-0.1, 1.4, 0.56)
    kit.export("clinica")


if __name__ == "__main__":
    kit.reset()
    clinica()
