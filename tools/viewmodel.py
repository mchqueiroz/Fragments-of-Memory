"""Gera os modelos de primeira pessoa (mãos, isqueiro, pistola, diário) como GLBs separados: art/models/vm_*.glb.

Uso: blender -b -P tools/viewmodel.py
Cada peça tem a origem no ponto onde o Godot a prende (punho, centro do caderno). Eixos do Blender: +Y = à frente da câmera
(vira -Z no Godot), +X = direita, +Z = cima. Os braços vêm de baixo e de trás (-Y) até o punho na origem.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402, F401
from mathutils import Vector  # noqa: E402

import kit  # noqa: E402
from kit import box, mat  # noqa: E402


def tube(m, p0, p1, r0, r1, n=8):
    """Tronco de cone entre dois pontos quaisquer (braços, dedos, empunhadura)."""
    a0, a1 = Vector(p0), Vector(p1)
    ax = (a1 - a0).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(ref).normalized()
    v = ax.cross(u).normalized()
    g = kit.G(m, False)
    ang = [2 * math.pi * i / n for i in range(n)]
    ring0 = [tuple(a0 + u * r0 * math.cos(a) + v * r0 * math.sin(a)) for a in ang]
    ring1 = [tuple(a1 + u * r1 * math.cos(a) + v * r1 * math.sin(a)) for a in ang]
    for i in range(n):
        j = (i + 1) % n
        q = [kit.W(ring0[i]), kit.W(ring0[j]), kit.W(ring1[j]), kit.W(ring1[i])]
        kit._quad(g, q, kit._auto_uv(m, q, (0.0, 0.0)))
    for ring, order in ((ring1, 1), (ring0, -1)):
        q = [kit.W(p) for p in ring][::order]
        kit._quad(g, q, kit._auto_uv(m, q, (0.0, 0.0)))


SLEEVE = None


def _mats():
    global SLEEVE
    SLEEVE = mat("trousers")
    return {
        "cuff": mat(None, color=(0.78, 0.76, 0.68)),
        "skin": mat(None, color=(0.70, 0.55, 0.45)),
        "scar": mat(None, color=(0.82, 0.70, 0.64)),
        "metal": mat("metal"),
        "black": mat(None, color=(0.05, 0.05, 0.06)),
        "cloth": mat("black_cloth"),
        "paper": mat("paper"),
        "red": mat(None, color=(0.45, 0.05, 0.05)),
    }


def arm(side, closed_hand):
    """Antebraço com manga de casaco, punho de camisa e mão. side=+1 direita, -1 esquerda."""
    M = _mats()
    s = side
    tube(SLEEVE, (s * 0.15, -0.50, -0.22), (s * 0.015, -0.04, -0.004), 0.058, 0.046)
    tube(M["cuff"], (s * 0.015, -0.045, -0.004), (0, 0.0, 0), 0.047, 0.044)
    box(M["skin"], (0, 0.05, 0), (0.082, 0.07, 0.03), col=False)                    # dorso/palma
    if closed_hand:  # punho fechado em volta do isqueiro/empunhadura
        for i in range(4):
            x = (i - 1.5) * 0.02
            tube(M["skin"], (x, 0.085, 0.004), (x, 0.13, -0.026), 0.011, 0.010)
            tube(M["skin"], (x, 0.13, -0.026), (x, 0.108, -0.064), 0.010, 0.009)
        tube(M["skin"], (-s * 0.04, 0.05, 0.0), (-s * 0.02, 0.12, 0.022), 0.013, 0.010)    # polegar por cima
    else:            # mão aberta, palma para cima, segurando o caderno
        for i in range(4):
            x = (i - 1.5) * 0.02
            tube(M["skin"], (x, 0.085, 0.0), (x, 0.17 - abs(i - 1.5) * 0.008, 0.004), 0.011, 0.009)
        tube(M["skin"], (-s * 0.04, 0.05, 0.0), (-s * 0.07, 0.11, 0.012), 0.013, 0.010)
        box(M["scar"], (0.0, 0.06, 0.0165), (0.055, 0.007, 0.003), col=False, rz=0.5)    # cicatriz no dorso
    kit.export("vm_arm_r" if side > 0 else "vm_arm_l")


def lighter():
    M = _mats()
    box(M["metal"], (0, 0, 0), (0.026, 0.014, 0.05), col=False)
    box(M["metal"], (0, 0, 0.034), (0.026, 0.016, 0.016), col=False)               # tampa
    box(M["black"], (0, 0, 0.044), (0.008, 0.008, 0.006), col=False)                # bocal da chama
    kit.export("vm_lighter")


def pistol():
    M = _mats()
    box(M["black"], (0, 0.075, 0.03), (0.024, 0.15, 0.03), col=False)               # carcaça e ferrolho
    box(M["metal"], (0, 0.145, 0.034), (0.012, 0.03, 0.012), col=False)             # boca do cano
    tube(M["black"], (0, 0.02, 0.012), (0, -0.025, -0.07), 0.016, 0.018)            # empunhadura inclinada
    box(M["black"], (0, 0.045, -0.002), (0.016, 0.04, 0.004), col=False)            # guarda-mato
    kit.export("vm_pistol")


def book_closed():
    M = _mats()
    box(M["paper"], (0, 0, 0), (0.104, 0.144, 0.018), col=False)
    box(M["cloth"], (0, 0, 0.011), (0.11, 0.15, 0.004), col=False)
    box(M["cloth"], (0, 0, -0.011), (0.11, 0.15, 0.004), col=False)
    box(M["cloth"], (-0.054, 0, 0), (0.004, 0.15, 0.026), col=False)
    box(M["red"], (0.03, 0, 0), (0.014, 0.152, 0.027), col=False)                  # elástico
    kit.export("vm_book_closed")


def book_open():
    M = _mats()
    box(M["cloth"], (0, 0, -0.009), (0.226, 0.158, 0.004), col=False)
    for sx in (-1, 1):
        box(M["paper"], (sx * 0.054, 0, 0.0), (0.106, 0.148, 0.012), col=False)
    box(M["cloth"], (0, 0, 0.0), (0.004, 0.15, 0.014), col=False)                  # lombada
    kit.export("vm_book_open")


if __name__ == "__main__":
    for fn, args in ((arm, (1, True)), (arm, (-1, False)), (lighter, ()), (pistol, ()), (book_closed, ()), (book_open, ())):
        kit.reset()
        fn(*args)
