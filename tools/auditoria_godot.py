"""Roda tools/auditoria.py sobre as primitivas criadas no Godot (exteriores e adereços de código).
Uso: DUMP=x.json godot --headless --path . --script res://tools/teste_posicoes.gd; python3 tools/auditoria_godot.py x.json <pasta>"""
import json
import sys

import auditoria

d = json.load(open(sys.argv[1]))
for key, prims in d.items():
    if not key.startswith("prims:"):
        continue
    a = auditoria.Audit(sys.argv[2])
    a.pairs = False
    for i, (label, pts) in enumerate(prims):
        k = "g%d" % i
        a.groups[k] = label
        a.prims.append([k, [tuple(p) for p in pts]])
    a.report("godot_" + key[6:].replace(".tscn", ""))
