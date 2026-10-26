"""Laboratório do instituto Kosmos (Cena 1, T+0): o hangar onde o míssil "Lethe" repousa.

Uso: blender -b -P tools/lab.py        -> art/models/laboratorio.glb
Dramaturgia: concreto manchado e pintura verde de instituto; o míssil é uma casca (por dentro é um pulso); o console
mostra "ОПЕРАТОР: —" (o operador esquece primeiro); luzes fluorescentes mortas e uma de emergência; papéis no chão,
uma cadeira tombada, cabos soltos. Eixos: X leste, Y norte (frente do jogador), Z cima.
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


def lab():
    random.seed(93)
    CON, GRN, PL, MT = mat("concrete"), mat("paint_green"), mat("plaster"), mat("metal")
    HZ, MS, PP = mat("hazard"), mat("missile_skin"), mat("paper")
    BK, WD = mat("black_cloth"), mat("wood_dark")
    SCR = mat("screen_lethe", emit_tex=True, strength=1.6)
    S_EXIT = mat("sign_exit", emit_tex=True, strength=1.4)
    S_WARN, EMB = mat("sign_warn"), mat("emblem")
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    WHITE = mat(None, color=(0.78, 0.76, 0.70))
    TUBE = mat(None, emit=(0.9, 0.95, 1.0), strength=2.2, color=(0.8, 0.85, 0.9))
    DEAD = mat(None, color=(0.35, 0.36, 0.38))
    RED = mat(None, emit=(1.0, 0.08, 0.05), strength=4.0, color=(0.4, 0.02, 0.02))
    NIGHT = mat(None, emit=(0.04, 0.07, 0.15), strength=0.5, color=(0, 0, 0))
    W, D, H = 10.0, 12.0, 5.0
    hx, hy = W / 2, D / 2

    # ---- casca: piso de concreto, teto, paredes (porta de saída no sul, x 3.0..4.2) ------------------
    box(CON, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    box(PL, (-hx - 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (hx + 0.1, 0, H / 2), (0.2, D + 0.4, H))
    box(PL, (0, hy + 0.1, H / 2), (W + 0.4, 0.2, H))
    box(PL, ((-hx - 0.2 + 3.0) / 2, -hy - 0.1, H / 2), (3.0 + hx + 0.2, 0.2, H))
    box(PL, ((4.2 + hx + 0.2) / 2, -hy - 0.1, H / 2), (hx + 0.2 - 4.2, 0.2, H))
    box(PL, (3.6, -hy - 0.1, 2.4 + (H - 2.4) / 2), (1.2, 0.2, H - 2.4))
    for (c, s) in (((-hx + 0.02, 0, 0.7), (0.04, D, 1.4)), ((hx - 0.02, 0, 0.7), (0.04, D, 1.4)),
                   ((0, hy - 0.02, 0.7), (W, 0.04, 1.4))):
        box(GRN, c, s, col=False)
        box(WHITE, (c[0], c[1], 1.43), (max(s[0], 0.06), max(s[1], 0.06), 0.05), col=False)
    for x in (-3.0, 3.0):                                                         # colunas e vigas de aço
        for y in (-2.5, 2.5):
            box(MT, (x, y, H / 2), (0.45, 0.45, H))
    for y in (-4.0, 0.0, 4.0):
        box(MT, (0, y, H - 0.25), (W, 0.3, 0.5), col=False)
    for dx in (-2.0, 0.0, 2.0):                                                   # bandejas de cabos
        box(DEAD, (dx, 0, H - 0.65), (0.5, D - 1, 0.06), col=False)
    for y in (-4.4, -1.6, 1.2, 4.0):                                               # fluorescentes: algumas mortas
        for x in (-2.4, 2.4):
            alive = (x < 0 and y in (-1.6, 4.0)) or (x > 0 and y == 1.2)
            box(TUBE if alive else DEAD, (x, y, H - 0.78), (0.18, 1.5, 0.07), col=False)
    for y in (-3.5, 0.5, 3.5):                                                     # janelas altas (noite)
        box(NIGHT, (hx - 0.01, y, 3.9), (0.02, 1.8, 0.9), col=False)
        box(MT, (hx - 0.03, y, 3.9), (0.04, 1.9, 0.06), col=False)
        box(MT, (hx - 0.03, y, 3.45), (0.04, 1.9, 0.06), col=False)
        box(MT, (hx - 0.03, y, 4.35), (0.04, 1.9, 0.06), col=False)

    # ---- portas e sinais ---------------------------------------------------------------------------
    a = 0.9                                                                         # porta de saída entreaberta
    box(MT, (3.0 + 0.6 * math.cos(a), -hy + 0.6 * math.sin(a), 1.2), (1.2, 0.08, 2.4), rz=a)
    panel(S_EXIT, (3.6, -hy + 0.02, 2.8), (0.96, 0.02, 0.4), "+y")
    for x in (-3.0, 3.0):
        panel(S_WARN, (x, 2.5 - 0.23, 1.8), (0.48, 0.02, 0.32), "-y")
    panel(EMB, (-2.0, hy - 0.02, 3.4), (0.9, 0.02, 0.9), "-y")
    box(RED, (-4.7, -5.0, 4.3), (0.25, 0.25, 0.25), col=False)                      # luz de emergência (a pulsar no Godot)
    box(RED, (4.7, 5.0, 4.3), (0.25, 0.25, 0.25), col=False)

    # ---- o míssil: casca vazia sobre dois berços, com faixa de perigo no piso ----------------------
    cyl(MS, (1.2, 3.0, 1.35), 0.85, 6.2, n=14, axis="x", col=True)
    cyl(MS, (1.2 + 3.1 + 0.7, 3.0, 1.35), 0.85, 1.4, n=14, r2=0.08, axis="x", col=True)   # ogiva
    for x in (-0.4, 2.8):
        box(MT, (x, 3.0, 0.3), (0.35, 1.9, 0.6))
    box(HZ, (1.2, 3.0 - 1.35, 0.012), (7.5, 0.3, 0.02), col=False)
    box(HZ, (1.2, 3.0 + 1.35, 0.012), (7.5, 0.3, 0.02), col=False)
    box(BLACK, (1.2, 3.0 - 0.86, 1.2), (1.1, 0.06, 0.7), col=False)                 # painel de serviço aberto
    panel(SCR, (1.2, 3.0 - 0.9, 1.2), (0.9, 0.02, 0.55), "-y")                      # tela do painel: "ДАННЫЕ: СБОЙ"
    panel(mat("missile_stencil"), (-0.8, 3.0 - 0.868, 1.75), (1.6, 0.02, 0.44), "-y")   # estêncil único "ЛЕТА № 004"

    # ---- console do pulso (norte) ------------------------------------------------------------------
    box(MT, (-2.0, 5.2, 0.45), (3.2, 1.0, 0.9))
    for dx in (-1.0, 0.0, 1.0):                                                      # três monitores
        box(BLACK, (-2.0 + dx, 5.15, 1.2), (0.7, 0.45, 0.55), col=False)
        panel(SCR, (-2.0 + dx, 5.15 - 0.23, 1.2), (0.58, 0.02, 0.43), "-y")
    box(BLACK, (-2.0, 4.75, 0.93), (0.9, 0.3, 0.04), col=False)                      # teclado
    box(MT, (-0.6, 4.8, 0.95), (0.34, 0.34, 0.1), col=False)                         # base do botão do pulso
    cyl(RED, (-0.6, 4.8, 1.03), 0.09, 0.07, n=10, col=False)                          # botão vermelho
    box(DEAD, (-0.6, 4.62, 1.1), (0.34, 0.03, 0.18), col=False, rz=0.0)               # tampa de vidro levantada
    # cadeira tombada
    box(WD, (-2.6, 3.9, 0.04), (0.5, 0.5, 0.08), col=False, rz=0.5)
    box(WD, (-2.9, 3.8, 0.28), (0.08, 0.5, 0.5), col=False, rz=0.5)

    # ---- estantes, osciloscópios, cabos e papéis largados ------------------------------------------
    for y in (-3.0, 0.0, 3.0):
        with kit.xf(-hx + 0.4, y):
            box(MT, (0, 0, 1.0), (0.5, 1.6, 2.0))
            for z in (0.5, 1.1, 1.7):
                box(WD, (0, 0, z), (0.52, 1.62, 0.03), col=False)
                for k in range(3):
                    box(mat(None, color=(random.uniform(0.15, 0.45), random.uniform(0.15, 0.4), random.uniform(0.15, 0.4))),
                        (0, -0.55 + k * 0.55, z + 0.15), (0.32, random.uniform(0.25, 0.45), 0.28), col=False)
    for (x, y) in ((-3.4, 1.8), (-3.2, -1.6)):                                         # carrinhos com osciloscópio
        box(MT, (x, y, 0.45), (0.7, 0.6, 0.9))
        box(BLACK, (x, y, 1.05), (0.5, 0.35, 0.35), col=False)
        panel(SCR, (x + 0.0, y - 0.18, 1.05), (0.4, 0.02, 0.28), "-y")
    for _ in range(26):                                                                # papéis espalhados no chão
        flat(PP, (random.uniform(-3.5, 2.5), random.uniform(-3.0, 3.8), 0.01), (0.3, 0.21, 0.004), rz=random.uniform(0, 6.28))
    for _ in range(7):                                                                 # cabos soltos
        box(BLACK, (random.uniform(-3, 3), random.uniform(-4, 4), 0.02), (random.uniform(1.0, 2.4), 0.05, 0.04),
            col=False, rz=random.uniform(0, 3.1))
    # ---- detalhes de vida: rodapé, extintores, quadro de avisos, canos, caixotes, cabos, tomadas ---------------------------
    props.baseboard(MT, hx, hy, 0.15, gaps=[("S", 3.0, 4.2)])
    props.extinguisher("W", -hx, -3.0)
    props.extinguisher("E", hx, 2.0)
    props.notice_board("W", -hx, 1.5, w=1.0, h=0.7, seed=3)
    props.vent("N", 2.0, hy, 3.8, w=0.6, h=0.35)
    props.pipe_x(MT, hy - 0.3, 4.4, -4.8, 4.8, 0.06)
    props.pipe_x(MT, hy - 0.55, 4.1, -4.8, 4.8, 0.04)
    props.pipe_y(MT, -hx + 0.3, 4.4, -5.5, 5.5, 0.05)
    props.crate(-4.3, -4.8)
    props.crate(-4.3, -4.8, 0.45)
    props.crate(-3.7, -4.9, 0.0, 0.5, rz=0.2)
    props.bucket(-3.0, -5.3)
    props.bin_(2.4, -5.5)
    props.cable(BLACK, [(4.4, -5.0, 0.02), (4.4, 0.0, 0.02), (3.6, 3.0, 0.02), (2.0, 5.0, 0.02)], 0.02)
    props.switch("S", 2.6, -hy)
    props.outlet("W", -hx, -1.0, 0.4)
    props.outlet("E", hx, -2.0, 0.4)
    props.wall_clock("N", -3.0, hy, 3.4)
    # ---- autenticidade: cartazes de instituto, aviso de alta tensão, proibido fumar, painel de incêndio, o quadro de paranoia ----------
    props.poster("poster_slogan", "E", hx, -1.0, 3.0, 1.8, 1.1)
    props.poster("poster_safety", "N", 0.5, hy, 2.6, 0.8, 1.0)
    props.poster("sign_nosmoke", "S", 2.2, -hy, 2.0, 0.3, 0.3)
    props.poster("fire_board", "W", -hx, -1.2, 1.6, 0.5, 0.7)
    props.poster("conspiracy_board", "W", -hx, 3.6, 2.0, 2.0, 1.4)
    props.podstakannik(-3.4, -5.3, 0.45)
    props.ashtray(-3.9, -4.8, 0.9)
    kit.export("laboratorio")


if __name__ == "__main__":
    kit.reset()
    lab()
