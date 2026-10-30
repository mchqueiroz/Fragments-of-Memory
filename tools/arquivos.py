"""Os Arquivos do Kosmos (Cena 3, T-30 min, linha A): sala de arquivos e servidor, luz fluorescente falhando.

Uso: blender -b -P tools/arquivos.py        -> art/models/arquivos.glb
Dramaturgia: estantes de pastas com um buraco etiquetado "ВОЛКОВ М. И. — ИЗЪЯТО" (a pasta foi retirada), terminal com
a nota "4-8-2-1" e o log que acusa Boris, cabo de câmera arrancado, armário de Boris, gaveta trancada (o disquete).
Eixos: X leste, Y norte (frente do jogador), Z cima. Porta ao sul.
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
from kit import box, cyl, mat  # noqa: E402


def arquivos():
    random.seed(1993)
    CON, PL, GRN, MT = mat("concrete"), mat("plaster"), mat("paint_green"), mat("metal")
    WD, PP = mat("wood_dark"), mat("paper")
    SCR = mat("screen_log", emit_tex=True, strength=1.5)
    NOTE, LBL, PIC = mat("note_code"), mat("label_volkov"), mat("pic_team")
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    TUBE = mat(None, emit=(0.85, 0.95, 1.0), strength=2.2, color=(0.8, 0.85, 0.9))
    LED_G = mat(None, emit=(0.1, 1.0, 0.3), strength=3.0, color=(0, 0.3, 0.1))
    LED_R = mat(None, emit=(1.0, 0.1, 0.05), strength=3.5, color=(0.3, 0.02, 0.02))
    FOLDERS = [mat(None, color=c) for c in ((0.55, 0.48, 0.32), (0.42, 0.40, 0.30), (0.30, 0.34, 0.30), (0.5, 0.25, 0.2))]
    W, D, H = 6.0, 6.0, 3.0
    hx, hy = W / 2, D / 2

    # ---- casca (porta ao sul, x -0.45..0.45) ------------------------------------------------------------
    box(CON, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (0, hy + 0.1, H / 2), (W + 0.4, 0.2, H))
    box(PL, ((-hx - 0.2 - 0.45) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(PL, ((0.45 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 0.45, 0.2, H))
    box(PL, (0, -hy - 0.1, 2.1 + (H - 2.1) / 2), (0.9, 0.2, H - 2.1))
    for (c, s) in (((-hx + 0.02, 0, 0.6), (0.04, D, 1.2)), ((hx - 0.02, 0, 0.6), (0.04, D, 1.2)),
                   ((0, hy - 0.02, 0.6), (W, 0.04, 1.2))):
        box(GRN, c, s, col=False)
    for (x, y) in ((-1.4, 0.0), (1.4, 0.0), (0.0, 1.8)):                                   # luminárias
        box(TUBE, (x, y, H - 0.04), (1.2, 0.12, 0.05), col=False)

    # ---- estantes de arquivo no oeste; um buraco etiquetado onde estava a pasta de Volkov ----------------
    for y0 in (-1.6, 1.2):
        box(MT, (-hx + 0.3, y0 + 0.9, 1.0), (0.5, 0.05, 2.0))
        box(MT, (-hx + 0.3, y0 - 0.9, 1.0), (0.5, 0.05, 2.0))
        for z in (0.05, 0.7, 1.35, 2.0):
            box(MT, (-hx + 0.3, y0, z), (0.5, 1.85, 0.04), col=False)
        for z in (0.1, 0.75, 1.4):
            for k in range(14):
                if y0 == 1.2 and z == 0.75 and 5 <= k <= 6:
                    continue                                                                # o buraco: a pasta foi retirada
                box(random.choice(FOLDERS), (-hx + 0.3, y0 - 0.85 + k * 0.125, z + 0.22), (0.4, 0.07, 0.5), col=False,
                    rz=random.uniform(-0.04, 0.04))
    panel(LBL, (-hx + 0.55, 1.2 - 0.85 + 5.5 * 0.125, 0.75 + 0.05), (0.01, 0.34, 0.12), "+x")   # etiqueta sem pasta

    # ---- racks do servidor ao norte, cabo de câmera arrancado -----------------------------------------------
    for x in (-1.6, -0.9, -0.2):
        box(MT, (x, hy - 0.45, 1.0), (0.6, 0.8, 2.0))
        box(BLACK, (x, hy - 0.86, 1.0), (0.5, 0.02, 1.8), col=False)
        for k in range(8):
            box(LED_G if random.random() > 0.3 else LED_R, (x - 0.15 + 0.3 * (k % 2), hy - 0.88, 0.3 + k * 0.2), (0.03, 0.02, 0.03), col=False)
    box(BLACK, (-0.3, 1.9, 0.02), (0.02, 0.9, 0.02), col=False, rz=0.5)                         # cabo no chão
    cyl(BLACK, (-0.55, 2.2, 0.03), 0.04, 0.06, n=6, col=False)                                 # ponta arrancada

    # ---- mesa do terminal (nota 4-8-2-1, foto rasgada, papéis) ----------------------------------------------
    box(WD, (1.7, hy - 0.5, 0.72), (1.6, 0.8, 0.05))
    for dx in (-0.7, 0.7):
        box(WD, (1.7 + dx, hy - 0.5, 0.35), (0.06, 0.7, 0.7), col=False)
    box(BLACK, (2.1, hy - 0.55, 0.95), (0.5, 0.45, 0.4), col=False)                           # monitor
    box(SCR, (2.1, hy - 0.79, 0.97), (0.42, 0.02, 0.32), col=False)
    panel(NOTE, (2.28, hy - 0.8, 1.18), (0.12, 0.02, 0.12), "-y")                              # nota colada
    flat(PIC, (1.35, hy - 0.45, 0.753), (0.22, 0.16, 0.006), rz=0.5)                            # foto rasgada
    flat(PP, (1.0, hy - 0.5, 0.753), (0.18, 0.24, 0.006), rz=-0.2)

    # ---- armário de Boris (leste) e gaveta trancada -----------------------------------------------------------
    box(MT, (hx - 0.3, 0.2, 1.0), (0.5, 0.6, 2.0))
    box(BLACK, (hx - 0.56, 0.2, 1.0), (0.01, 0.02, 1.8), col=False)
    cyl(mat(None, emit=(0.1, 0.35, 0.18), strength=0.4, color=(0.1, 0.3, 0.15)), (hx - 0.3, 0.2, 2.1), 0.035, 0.2, n=8)
    box(MT, (hx - 0.3, -1.3, 0.5), (0.5, 0.6, 1.0))
    for z in (0.2, 0.5, 0.8):
        box(BLACK, (hx - 0.56, -1.3, z), (0.01, 0.4, 0.02), col=False)
    box(mat("brass"), (hx - 0.57, -1.3, 0.8), (0.02, 0.06, 0.04), col=False)                   # fechadura

    # ---- detalhes de vida: rodapé, extintor, avisos, canos, caixotes, cabos, lixeira, relógio -----------------------------------------
    props.baseboard(MT, hx, hy, 0.12, gaps=[("S", -0.45, 0.45)])
    props.extinguisher("E", hx, -2.6)
    props.notice_board("S", -1.5, -hy, 1.7, seed=5)
    props.switch("S", 0.8, -hy)
    props.outlet("W", -hx, 2.75, 0.4)
    props.vent("S", -1.9, -hy, 2.4)
    props.pipe_x(MT, 0.0, 2.7, -2.9, 2.9, 0.05)
    props.pipe_x(MT, 1.0, 2.6, -2.9, 2.9, 0.04)
    props.crate(-2.3, -2.75, 0.0, 0.5)
    props.crate(-1.8, -2.7, 0.0, 0.45, rz=0.2)
    props.papers(1.0, 2.45, 0.75, n=4, seed=2)
    props.mug(2.5, 2.3, 0.75)
    props.bin_(0.6, 2.6)
    props.wall_clock("N", 0.8, hy, 2.4)
    props.cable(BLACK, [(-0.5, 2.1, 0.02), (0.2, 1.2, 0.02), (1.2, 0.5, 0.02)], 0.02)
    # ---- autenticidade: cartaz desbotado, aviso, passe do Kosmos, jornal, chá, cinzeiro, porta com fechaduras --------------------------
    props.poster("poster_slogan", "S", 1.6, -hy, 2.0, 1.3, 0.85)
    props.poster("poster_safety", "E", hx, 1.6, 1.8, 0.7, 0.9)
    props.poster("sign_nosmoke", "S", -0.9, -hy, 1.9, 0.3, 0.3)
    props.flat_tex("pass_card", 1.3, 2.3, 0.752, 0.10, 0.065, rz=0.3)
    props.flat_tex("newspaper_pravda", 0.9, 2.3, 0.752, 0.24, 0.30, rz=-0.2)
    props.podstakannik(2.4, 2.4, 0.745)
    props.ashtray(1.4, 2.7, 0.745)
    props.door("S", 0.0, -hy, 0.9, 2.05, angle=0.55)
    kit.export("arquivos")


if __name__ == "__main__":
    kit.reset()
    arquivos()
