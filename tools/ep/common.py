"""Atalhos compartilhados pelas especificações de episódios (sons, luzes, tintas por linha do tempo)."""

# Linha F (flashback, quente) e linha A (presente, fria): tinta do pós-processo
TINT_F = [1.10, 0.98, 0.84]
TINT_A = [0.92, 1.0, 1.10]

COLD = [0.80, 0.92, 1.0]
WARM = [1.0, 0.72, 0.42]
GREENISH = [0.85, 0.95, 0.90]


def snd(ground="parquet", size=0.4, wet=0.2, amb_db=-30.0, emitters=None, life=None, music="tinnitus", music_db=-50.0):
    return {"amb": "amb_room", "music": music, "music_db": music_db, "amb_db": amb_db, "ground": ground, "size": size, "wet": wet,
            "emitters": emitters or [], "life": life or []}


def life_building(x=0.0, y=0.0, z=2.8, spread=3.0):
    """Eventos de prédio soviético: cano batendo, passos no andar de cima, bonde na rua, sirene longe."""
    return [["pipes_knock", 25.0, 60.0, -13.0, [x + 2, y, 1.0], [0.0, spread, 0.5]],
            ["upstairs_steps", 25.0, 60.0, -14.0, [x, y, z], [1.0, 1.0, 0.0]],
            ["tram_pass", 45.0, 90.0, -14.0, [x, y + 6, 1.5], [2.0, 1.0, 1.0]],
            ["siren_far", 70.0, 130.0, -16.0, [x, y + 8, 2.0], [3.0, 1.0, 1.0]]]


def lamps_room(W, D, H, warm=True, flicker=True):
    """Duas luzes de teto (fria ou quente); boa base para qualquer sala."""
    c = WARM if warm else COLD
    return [[-W / 4, 0, H - 0.4, c, 1.8, max(W, D) * 0.9, flicker],
            [W / 4, 0, H - 0.4, c, 1.6, max(W, D) * 0.9, False]]
