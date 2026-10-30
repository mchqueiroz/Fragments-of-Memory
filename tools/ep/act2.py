"""Ato II — O disfarce (cenas 11–16). Coordenadas das salas em Blender (x leste, y norte, z cima); exteriores em Godot (x, y cima, z)."""
from ep.common import COLD, TINT_A, TINT_F, life_building, snd

SPECS = {}

# ======================================================================================================================
# 11 · A6 · A Sala de Controle · T−1 dia
# ======================================================================================================================
SPECS["sala_controle"] = {
    "size": [7.0, 6.0, 3.4], "theme": "verde",
    "title": ["A6 · T − 1 DIA", "A SALA DE CONTROLE"], "tint": TINT_A,
    "openings": [("S", 2.4, 0.9, 0.0, 2.1), ("E", 0.5, 3.2, 0.9, 2.5)], "sky": [0.15, 0.25, 0.30],
    "things": [
        ("c1", "console", -1.2, 1.0, 0.0, {"w": 2.4}), ("c2", "console", 1.6, 1.0, 0.0, {"w": 2.4}),
        ("d1", "desk", -2.6, -1.4, 1.5708, {"w": 1.4}), ("ch1", "chair", -1.75, -1.4, 1.5708),
        ("f1", "filing", 3.2, -2.2, -1.5708), ("l1", "locker", -3.2, 2.0, 1.5708),
        ("sh", "bookshelf", 0.5, 2.78, 3.1416, {"w": 1.2}),
    ],
    "decor": [
        ("props", "poster", "poster_safety", "W", -3.5, -2.0, 1.8, 0.7, 0.9), ("props", "poster", "sign_nosmoke", "S", 1.0, -3.0, 1.9, 0.3, 0.3),
        ("props", "poster", "fire_board", "N", 2.8, 3.0, 1.6, 0.5, 0.7), ("props", "wall_clock", "N", -1.5, 3.0, 2.5),
        ("props", "notice_board", "W", -3.5, 0.5, 1.7, {"seed": 2}), ("props", "vent", "N", 1.0, 3.0, 3.0),
        ("props", "switch", "S", 1.6, -3.0), ("props", "outlet", "E", 3.5, -1.5), ("props", "bin_", -3.0, -2.6),
        ("props", "extinguisher", "E", 3.5, -2.5),
        ("furniture", "computer", -2.5, -1.4, 0.765, 0.2), ("props", "mug", -2.75, -0.85, 0.765), ("props", "ashtray", -2.45, -0.85, 0.765),
        ("props", "podstakannik", -2.45, -1.95, 0.765), ("props", "papers", -2.75, -1.9, 0.765, {"n": 3, "seed": 6}),
        ("props", "bottle", 3.1, -2.2, 1.4, {"color": [0.3, 0.15, 0.05]}),
    ],
    "lamps": [[0, 0, 3.0, COLD, 2.0, 8, True], [-2.6, -1.2, 1.4, [0.6, 1.0, 0.7], 1.0, 3, False], [3.3, 0.5, 1.5, [0.2, 0.5, 0.6], 1.2, 4, False]],
    "env": {"ambient": [0.10, 0.12, 0.12], "fog": [0.6, 0.7, 0.7], "density": 0.02},
    "start": [2.0, -2.4, 0], "dress": [101, 1.0, True],
    "sound": snd("lino", 0.5, 0.25, emitters=[["fluorescent_buzz", [0, 0, 3.0], -22.0, 3.0]], life=life_building()),
    "npcs": [{"id": "boris", "model": "boris", "face": "face_boris", "at": [-1.75, -1.4], "pose": "sleep", "look": [-2.6, -1.4], "always": True, "size": [0.5, 1.0, 0.5]}],
    "intro": [["Dois andares acima do hangar: a sala de onde se vê tudo e se controla tudo.", 5.0]],
    "clues": [
        {"id": "terminal", "prompt": "Usar o terminal", "at": [-1.2, 0.5, 1.3], "size": [1.2, 0.6, 0.5],
         "ask": {"q": "O terminal exige a credencial de Boris. Você a copia do crachá dele?",
                 "opts": ["Copiar a credencial dele", "Deixar como está"], "truth": [-1, 1], "flag": "forjou", "correct": 0,
                 "reply": [["ALEKSEY: Pronto. Amanhã todo rastro vai ter o nome dele."], ["ALEKSEY: Não. Ainda não."]]},
         "note": "Terminal de controle do pulso. Pede credencial; a de Boris está no crachá dele, sobre a mesa.",
         "alt": "Terminal comum. Faço o que preciso fazer.", "say": "Daqui se dispara tudo. Daqui se culpa qualquer um."},
        {"id": "cracha", "prompt": "Olhar o crachá", "on": "d1", "at": [0.1, 0.3], "item": ["flat", "pass_card", 0.10, 0.065],
         "note": "Crachá de Boris: 'Волков Б. И.' Ele dorme com a credencial no pescoço. Só confia em si mesmo.",
         "say": "A credencial dele, ao alcance de uma mão que não é a dele."},
        {"id": "foto", "prompt": "Olhar a foto", "on": "d1", "at": [-0.2, -0.15], "item": ["flat", "pic_brothers", 0.14, 0.11, 0.1],
         "note": "Foto desbotada de dois garotos na neve: o mais velho tem a mão no ombro do menor. Boris dorme com a cabeça ao lado dela.",
         "alt": "Uma foto velha. Crianças, neve.", "say": "Dois irmãos na neve. Boris olha para ela mesmo dormindo."},
        {"id": "camlog", "prompt": "Ler o log das câmeras", "at": [1.6, 0.5, 1.3], "size": [1.2, 0.6, 0.5],
         "note": "Log das câmeras do corredor: 23h15, apagado por 'B.V.'. O mesmo horário do log dos arquivos. Alguém ensaia a mesma culpa.",
         "alt": "Log de câmeras. Tudo certo.", "say": "As horas batem demais. Alguém preparou isto."},
        {"id": "janela", "prompt": "Olhar o hangar", "at": [3.4, 0.5, 1.7], "size": [0.3, 3.0, 1.2],
         "note": "Pela janela: o hangar, o míssil Lethe sob uma lona. Amanhã à noite ele será 'sabotado'.",
         "say": "A lona esconde o que ninguém devia ver."},
        {"id": "garrafa", "prompt": "Olhar a garrafa e o copo", "on": "d1", "at": [0.4, 0.2],
         "note": "Garrafa e copo na mesa de Boris. Ele bebe sozinho aqui, entre turnos.", "alt": "Boris bebe no trabalho. Fraco.",
         "say": "Vodka de turno. Ninguém o vigia.", "optional": True},
        {"id": "boris_dorme", "prompt": "Olhar Boris dormindo", "at": [-1.95, -1.4, 1.0], "size": [0.6, 0.6, 1.4],
         "note": "Boris dorme sobre a mesa, a mão sobre uma foto. Faz dois dias que não vai para casa.",
         "say": "Ele dorme com a boca aberta, como um garoto.", "optional": True},
    ],
    "needed": ["terminal", "cracha", "foto", "camlog", "janela"],
    "outro": [["Boris vai acordar sem saber que eu estive aqui.", 4.0]],
}

# ======================================================================================================================
# 12 · F6 · O Treinador · 1992
# ======================================================================================================================
SPECS["treinador"] = {
    "size": [5.0, 4.4, 3.0], "theme": "gesso",
    "title": ["1992", "O TREINADOR"], "tint": TINT_F,
    "openings": [("S", -1.4, 0.9, 0.0, 2.1), ("N", 0.6, 1.5, 0.9, 2.2)], "sky": [0.8, 0.82, 0.78],
    "things": [
        ("mesa", "table", 0.9, 0.3, 0.0, {"w": 1.1, "d": 1.1}), ("c1", "chair", 0.9, -0.55, 0.0), ("c2", "chair", 0.9, 1.15, 3.1416),
        ("desk", "desk", -1.7, 1.8, 3.1416, {"w": 1.5}), ("sh", "bookshelf", 2.28, 0.9, 1.5708, {"w": 1.4}),
        ("sofa", "sofa", -2.03, -0.5, 1.5708, {"w": 1.6}),
    ],
    "decor": [
        ("props", "poster", "blackboard", "W", -2.5, 1.0, 1.6, 1.8, 1.1), ("props", "poster", "calendar_1991", "N", -1.6, 2.2, 1.9, 0.5, 0.6),
        ("props", "poster", "sign_nosmoke", "S", 0.4, -2.2, 1.9, 0.3, 0.3), ("props", "wall_clock", "E", 2.5, -1.2, 2.2),
        ("props", "radiator", "N", 0.6, 2.2, {"w": 1.2}), ("props", "switch", "S", -0.6, -2.2),
        ("props", "podstakannik", 0.55, 0.1, 0.75), ("props", "podstakannik", 1.3, 0.4, 0.75),
        ("props", "papers", -1.3, 1.8, 0.77, {"n": 4, "seed": 2}), ("props", "ashtray", -2.0, 1.7, 0.77),
        ("furniture", "lamp_table", -2.0, 2.0, 0.765),
    ],
    "models": [{"model": "chess", "at": [0.9, 0.3, 0.76], "scale": 0.75}],
    "lamps": [[0, 0, 2.6, [1.0, 0.85, 0.6], 1.6, 6, True], [0.6, 2.0, 1.4, [1.0, 0.9, 0.7], 2.0, 4, False], [-2.0, 2.0, 1.2, [1.0, 0.7, 0.4], 0.9, 2.5, False]],
    "env": {"ambient": [0.2, 0.17, 0.13], "fog": [0.9, 0.8, 0.65], "density": 0.02},
    "start": [-1.4, -1.8, 0], "dress": [112, 0.7, True],
    "sound": snd("parquet", 0.35, 0.15, emitters=[["clock_loop", [2.4, -1.2, 2.2], -14.0, 2.0]], life=life_building()),
    "npcs": [{"id": "treinador", "model": "treinador", "face": "face_trainer", "at": [0.9, 1.15], "pose": "sit", "look": [0.9, 0.3], "voice": "low", "pitch": 0.9,
              "prompt": "Falar com o treinador", "size": [0.7, 1.8, 0.5]}],
    "intro": [["Dois anos. Aprendi a ser outra pessoa, lance a lance.", 5.0]],
    "clues": [
        {"id": "tabuleiro", "prompt": "Jogar o tabuleiro", "at": [0.9, 0.3, 0.95], "size": [0.7, 0.7, 0.3],
         "ask": {"q": "O treinador deixa uma abertura no tabuleiro. Qual lance você faz?",
                 "opts": ["1. e4: peão do rei", "1. d4: peão da dama", "1. Cf3: cavalo"], "truth": [0, 0, 0], "flag": "abertura_do_pai", "correct": 0,
                 "reply": [["TREINADOR: e4... Quem lhe ensinou isso, Aleksey?", "ALEKSEY: Não sei. Minhas mãos sabem."],
                           ["TREINADOR: d4. Seguro. Pouco seu."], ["TREINADOR: Cavalo. Prudente, mas esconde medo."]]},
         "note": "Tabuleiro: o treinador deixou uma abertura. Minhas mãos jogam como quem já jogou a vida inteira.",
         "alt": "Um jogo de xadrez. Sou bom nisso.", "say": "Jogo sem pensar. Isso devia me assustar."},
        {"id": "cartilha", "prompt": "Ler a cartilha", "on": "desk", "at": [0.2, 0.0], "item": ["flat", "paper", 0.2, 0.28],
         "note": "Cartilha: 'Aleksey Ivanovich Petrov, nascido em 1958, filho de professores, técnico em eletrônica.' Decoro a vida que não tive.",
         "alt": "Minha biografia. Está tudo certo.", "say": "Decoro uma vida que me deram pronta."},
        {"id": "caderno", "prompt": "Pegar o caderno novo", "on": "desk", "at": [-0.4, 0.2], "item": ["flat", "notebook_misha", 0.14, 0.2],
         "note": "Caderno novo de capa preta. O treinador mandou: 'Escreva tudo. Quem escreve, existe.' É daqui que nasce o diário.",
         "say": "Primeira página: a data, o nome que me deram."},
        {"id": "quadro", "prompt": "Olhar o quadro-negro", "at": [-2.4, 1.0, 1.6], "size": [0.3, 1.9, 1.2],
         "note": "Quadro-negro cheio de aberturas e de datas: o treinador testa minha memória como quem testa um relógio.",
         "say": "Datas, nomes, lances. Tudo para eu não esquecer o que nunca vivi."},
        {"id": "calendario", "prompt": "Olhar o calendário", "at": [-1.6, 2.2, 1.9], "size": [0.6, 0.3, 0.7],
         "note": "Calendário de 1992 riscado dia a dia. Dois anos de treino se contam em riscos.", "optional": True,
         "say": "Cada risco é um dia que repeti."},
    ],
    "needed": ["tabuleiro", "cartilha", "caderno", "quadro"],
    "talk": {"npc": "treinador", "hint": "O treinador espera, as mãos sobre o tabuleiro. Acho que posso falar com ele.",
             "lines": ["TREINADOR: Dois anos, Aleksey. Você aprende mais rápido do que devia.",
                       "ALEKSEY: Rápido demais para quem não sabe nada.",
                       "TREINADOR: Quem não sabe nada não joga e4 sem olhar. Você sabe alguma coisa. O corpo lembra, mesmo que a cabeça não.",
                       {"q": "O treinador estende o caderno novo. O que você faz?",
                        "opts": ["Escrever tudo, como ele mandou", "Confiar na memória"], "truth": [1, -1], "flag": "diario",
                        "reply": [["TREINADOR: Bom. Quem escreve, existe."], ["TREINADOR: Hm. Memória é o que mais falha quem mais confia nela."]]},
                       "TREINADOR: Quando estiver pronto, Irina vai buscá-lo. Não conte a ninguém que você joga assim."],
             "note": "O treinador: 'O corpo lembra, mesmo que a cabeça não.' Preciso escrever tudo.",
             "alt": "O treinador gosta de mim. Fico tranquilo."},
}

# ======================================================================================================================
# 13 · A7 · O Telhado · T−2 dias (exterior)
# ======================================================================================================================
def _rooftop_prims():
    p = []
    for x in range(-14, 15, 2):                                                         # parapeito em volta do terraço
        p.append({"t": "box", "p": [x, 0.5, -15], "s": [2.0, 1.0, 0.4], "c": [0.35, 0.34, 0.33]})
        p.append({"t": "box", "p": [x, 0.5, 15], "s": [2.0, 1.0, 0.4], "c": [0.35, 0.34, 0.33]})
        p.append({"t": "box", "p": [-15, 0.5, x], "s": [0.4, 1.0, 2.0], "c": [0.35, 0.34, 0.33]})
        p.append({"t": "box", "p": [15, 0.5, x], "s": [0.4, 1.0, 2.0], "c": [0.35, 0.34, 0.33]})
    p += [{"t": "cyl", "p": [-8, 1.6, -6], "r": 1.6, "h": 3.2, "c": [0.30, 0.28, 0.26]},
          {"t": "cyl", "p": [-8, 3.3, -6], "r": 1.7, "h": 0.2, "c": [0.2, 0.2, 0.22]},
          {"t": "cyl", "p": [8, 3.5, -3], "r": 0.06, "h": 7.0, "c": [0.5, 0.5, 0.5]},
          {"t": "box", "p": [8, 5.5, -3], "s": [2.0, 0.06, 0.06], "c": [0.5, 0.5, 0.5]},
          {"t": "box", "p": [8, 4.6, -3], "s": [1.4, 0.06, 0.06], "c": [0.5, 0.5, 0.5]},
          {"t": "box", "p": [-12, 1.25, 8], "s": [3.0, 2.5, 3.0], "c": [0.28, 0.26, 0.25], "solid": True},
          {"t": "box", "p": [-10.48, 1.0, 8], "s": [0.1, 2.0, 1.0], "c": [0.12, 0.08, 0.06]},
          {"t": "box", "p": [10, 1.0, 9], "s": [1.2, 2.0, 1.2], "c": [0.30, 0.28, 0.26], "solid": True},
          {"t": "box", "p": [0, 7.0, -28], "s": [5.0, 1.2, 0.3], "c": [1.0, 0.1, 0.08], "glow": True},          # letreiro vermelho da rua
          {"t": "light", "p": [0, 7.0, -26], "c": [1.0, 0.2, 0.1], "e": 2.0, "r": 12},
          {"t": "light", "p": [0, 5.0, 4], "c": [0.5, 0.6, 1.0], "e": 1.0, "r": 22}]
    for i, (x, z, h) in enumerate([(-30, -40, 22), (-12, -50, 30), (14, -48, 18), (36, -44, 26), (-48, -20, 20), (52, -18, 24), (-40, 30, 16), (44, 34, 20)]):
        p.append({"t": "bldg", "p": [x, z], "s": [14, h, 22], "emit": 1.6})
    p.append({"t": "box", "p": [0, 12.0, -130], "s": [70, 24, 28], "c": [0.18, 0.16, 0.17]})                    # o Kosmos, ao longe
    for k in range(-3, 4):
        p.append({"t": "box", "p": [k * 9, 12.0, -115.8], "s": [1.2, 24.0, 1.2], "c": [0.12, 0.11, 0.12]})
    return p


SPECS["telhado"] = {
    "kind": "outdoor", "title": ["A7 · T − 2 DIAS", "O TELHADO"], "tint": TINT_A,
    "sky": {"top": [0.03, 0.04, 0.09], "horizon": [0.35, 0.22, 0.20]}, "sun": {"rot": [-40, 200], "color": [0.4, 0.5, 0.8], "energy": 0.3},
    "ambient": 0.5, "env": {"fog": [0.15, 0.15, 0.2], "density": 0.004}, "ground": {"color": [0.25, 0.25, 0.27], "tex": "concrete"},
    "start": {"pos": [0, 0.05, 10], "yaw": 0}, "primitives": _rooftop_prims(),
    "sound": snd("concrete", 0.9, 0.35, amb_db=-34.0, life=[["siren_far", 25.0, 55.0, -12.0, [0, 8, -60], [30, 2, 10]],
                                                              ["tram_pass", 30.0, 60.0, -12.0, [0, 0, -40], [20, 1, 5]],
                                                              ["gunshots_far", 40.0, 90.0, -16.0, [0, 5, -90], [30, 2, 10]]]),
    "npcs": [{"id": "inter", "model": "intermediario", "face": "face_inter", "pos": [6.0, -2.5], "voice": "low", "pitch": 0.85,
              "prompt": "Falar com o intermediário", "size": [0.7, 1.8, 0.5]}],
    "intro": [["Um terraço de concreto, o vento, a cidade acesa. Marcamos aqui porque ninguém olha para cima.", 5.5]],
    "clues": [
        {"id": "antena", "prompt": "Olhar a antena", "at": [8.0, 1.5, -3.0], "size": [1.4, 3.0, 1.4],
         "note": "Antena de TV com um cabo preto cortado e emendado: alguém escuta daqui, ou deixa que escutem.",
         "alt": "Uma antena velha.", "say": "Cabos emendados à mão. Esta antena escuta mais do que mostra."},
        {"id": "tanque", "prompt": "Olhar a caixa d'água", "at": [-8.0, 1.6, -6.0], "size": [3.4, 3.2, 3.4],
         "note": "Atrás da caixa d'água, uma pasta de plástico preso com fita. Dentro, rublos e um papel com um horário.",
         "say": "Dinheiro escondido num lugar onde só cabe quem sabe."},
        {"id": "cidade", "prompt": "Olhar a cidade", "at": [0.0, 1.0, -14.0], "size": [10.0, 1.2, 0.8],
         "note": "A cidade a meus pés: fumaça no horizonte, o bloco de concreto do Kosmos de pé, escuro. É para lá que tudo converge.",
         "say": "Moscou queimando devagar. E o Kosmos, intacto, no meio."},
        {"id": "cigarros", "prompt": "Olhar as bitucas", "at": [5.0, 0.15, 2.0], "size": [1.5, 0.3, 1.5],
         "note": "Dezenas de bitucas de Belomor ao pé da antena. Alguém esperou aqui muitas noites.", "optional": True,
         "say": "Belomor. Quem espera aqui espera há muito tempo."},
        {"id": "porta", "prompt": "Olhar a porta da escada", "at": [-10.6, 1.0, 8.0], "size": [0.5, 2.0, 1.2],
         "note": "A porta da escada tem a fechadura arrancada. Qualquer um sobe; ninguém deveria saber que estou aqui.",
         "say": "A fechadura não foi arrombada hoje. Esta porta nunca esteve fechada."},
    ],
    "needed": ["antena", "tanque", "cidade", "porta"],
    "talk": {"npc": "inter", "hint": "O intermediário acende um cigarro junto à antena. Acho que é a minha vez de falar.",
             "lines": ["INTERMEDIÁRIO: Pontual, Petrov. A cidade está pior do que ontem.",
                       "INTERMEDIÁRIO: Irina manda dizer: o Lethe tem de estar armado em dois dias. Karpov não espera mais.",
                       "ALEKSEY: E Boris?",
                       "INTERMEDIÁRIO: Boris é o homem de quem todos vão duvidar. Você sabe o que fazer.",
                       {"q": "O intermediário estende um envelope grosso. O que você faz?",
                        "opts": ["Aceitar o pacto e o envelope", "Recusar: 'Eu decido o que faço'"], "truth": [-1, 1], "flag": "pacto",
                        "reply": [["INTERMEDIÁRIO: Sensato. Quem aceita sobrevive até o fim da semana."],
                                  ["INTERMEDIÁRIO: Todo mundo diz isso, Petrov. Até o primeiro tiro."]]},
                       "INTERMEDIÁRIO: Dois dias. Depois disso, ninguém mais lembra deste telhado."],
             "note": "No telhado, selei um pacto com o intermediário de Irina: em dois dias o Lethe sai armado do Kosmos.",
             "alt": "Conversei com um conhecido no telhado."},
}

# ======================================================================================================================
# 14 · F7 · O Cemitério · mar/1992 (exterior)
# ======================================================================================================================
def _cemetery_prims():
    p = [{"t": "snow", "p": [0, 8, -8], "s": [30, 8, 30]}]
    import random
    r = random.Random(1992)
    for gx in range(-16, 17, 4):
        for gz in range(-24, -2, 3):
            if abs(gx) < 6 and gz > -15:
                continue
            p.append({"t": "grave", "p": [gx + r.uniform(-0.4, 0.4), gz + r.uniform(-0.4, 0.4)], "rot": r.uniform(-12, 12)})
    for i in range(14):
        p.append({"t": "tree", "p": [r.uniform(-24, 24), r.uniform(-34, -4)], "h": r.uniform(5, 8), "leaf": [0.30, 0.27, 0.24]})
    p += [{"t": "box", "p": [0, 0.04, -12], "s": [1.6, 0.1, 2.6], "c": [0.03, 0.03, 0.04]},                            # a cova
          {"t": "box", "p": [0, 0.3, -12], "s": [1.0, 0.5, 2.2], "c": [0.38, 0.26, 0.15]},                                # o caixão
          {"t": "box", "p": [0, 0.58, -12], "s": [0.8, 0.06, 1.0], "c": [0.7, 0.1, 0.1]},                                 # flores
          {"t": "box", "p": [3.0, 0.4, -10.0], "s": [0.2, 0.8, 0.5], "c": [0.55, 0.55, 0.55]},                            # lápide provisória
          {"t": "people", "p": [-4, -12], "n": 7, "r": 2.5}, {"t": "people", "p": [4, -14], "n": 6, "r": 2.5},
          {"t": "light", "p": [0, 6, -8], "c": [0.8, 0.85, 1.0], "e": 0.8, "r": 25}]
    for x in range(-26, 27, 2):                                                                                       # cerca de ferro
        p.append({"t": "box", "p": [x, 0.8, 8], "s": [0.1, 1.6, 0.1], "c": [0.1, 0.1, 0.1]})
    p.append({"t": "box", "p": [0, 1.4, 8], "s": [52, 0.08, 0.08], "c": [0.1, 0.1, 0.1]})
    return p


SPECS["cemiterio"] = {
    "kind": "outdoor", "title": ["MAR / 1992", "O CEMITÉRIO"], "tint": [1.0, 1.0, 1.05],
    "sky": {"top": [0.38, 0.41, 0.48], "horizon": [0.66, 0.68, 0.72]}, "sun": {"rot": [-35, 40], "color": [0.9, 0.92, 1.0], "energy": 0.5},
    "ambient": 0.75, "env": {"fog": [0.62, 0.64, 0.70], "density": 0.012}, "ground": {"color": [0.60, 0.63, 0.70]},
    "start": {"pos": [0, 0.05, 6], "yaw": 0}, "primitives": _cemetery_prims(),
    "sound": snd("concrete", 0.9, 0.3, amb_db=-36.0, life=[["siren_far", 50.0, 110.0, -18.0, [0, 3, -40], [20, 1, 5]]]),
    "npcs": [{"id": "sergei_npc", "model": "sergei", "face": "face_sergei", "pos": [-2.5, -9.5], "voice": "low", "pitch": 1.0, "size": [0.7, 1.8, 0.5],
              "prompt": "Olhar Sergei"},
             {"id": "boris", "model": "boris", "face": "face_boris", "pos": [9.0, -17.0], "voice": "low", "pitch": 0.85, "prompt": "Falar com Boris",
              "size": [0.7, 1.8, 0.5]}],
    "intro": [["Neve fina. Não sou convidado: eu observo de longe, como me treinaram.", 5.0]],
    "clues": [
        {"id": "caixao", "prompt": "Olhar o caixão", "at": [0.0, 0.5, -12.0], "size": [1.2, 1.0, 2.4],
         "note": "Caixão de pinho sobre a cova aberta. Lena, 34 anos. A tampa fechada esconde o rosto que eu não me lembro de ter amado.",
         "alt": "Um funeral. Gente que não conheço.", "say": "Quem é ela para mim? A neve não responde."},
        {"id": "coroa", "prompt": "Ler a coroa de flores", "at": [-1.6, 0.6, -10.0], "size": [1.0, 1.2, 0.5],
         "note": "Coroa de cravos vermelhos: 'Лена — коллеги из «Космоса»'. Um laço preto com outra frase menor: 'Нам тебя не хватает, Миша' escondida embaixo.",
         "say": "Cravos vermelhos. E um nome pequeno demais, escrito por baixo: Misha."},
        {"id": "lapide", "prompt": "Ler a lápide provisória", "at": [3.0, 0.4, -10.0], "size": [0.6, 0.9, 0.6],
         "note": "Lápide provisória de madeira: 'Елена Морозова, 1958–1992'. Morozova: o sobrenome de Sergei. Ela era a esposa.",
         "say": "Morozova. Era a esposa de Sergei. E ele não derramou uma lágrima."},
        {"id": "sergei", "prompt": "Olhar Sergei", "at": [-2.5, 0.9, -9.5], "size": [0.8, 1.8, 0.8],
         "note": "Sergei ao lado da cova, sem lágrimas e sem chapéu, a mão fechada num lenço. Ele não olha para ninguém.",
         "say": "Sergei não chora. Chora quem ainda tem o que perder."},
    ],
    "needed": ["caixao", "coroa", "lapide", "sergei"],
    "talk": {"npc": "boris", "hint": "Do outro lado da cova, Boris me olha fixamente. Acho que ele quer falar.",
             "lines": ["BORIS: Eu conheço você?",
                       "ALEKSEY: Não creio.",
                       "BORIS: Você anda como meu irmão. O mesmo jeito de arrastar o pé esquerdo.",
                       {"q": "Boris não desvia o olhar. O que você faz?",
                        "opts": ["Aproximar-se: 'Meus pêsames pela perda.'", "Virar as costas e ir embora"], "truth": [1, -1], "flag": "encarou_boris",
                        "reply": [["BORIS: ...Obrigado. Não, perdão. Você me lembrou alguém."], ["BORIS: Espere! ...Esquece. Esqueça."]]},
                       "BORIS: Meu irmão sumiu em agosto. Se um dia o vir, diga que o procuro."],
             "note": "No cemitério, Boris me olhou e disse que eu ando como o irmão dele. Ele procura o irmão desde agosto de 1991.",
             "alt": "Um policial me confundiu com alguém. Besteira."},
}

# ======================================================================================================================
# 15 · A8 · A Noite da Chave · T−3 dias
# ======================================================================================================================
SPECS["chave"] = {
    "size": [8.0, 6.0, 3.6], "theme": "concreto",
    "title": ["A8 · T − 3 DIAS", "A NOITE DA CHAVE"], "tint": TINT_A,
    "openings": [("S", 3.0, 1.0, 0.0, 2.2)],
    "things": [
        ("m", "missile", 0.0, 0.3, 1.5708, {"length": 4.6, "r": 0.5}), ("c1", "console", -2.8, 2.3, 0.0, {"w": 2.0}),
        ("d1", "desk", 2.6, 2.3, 0.0, {"w": 1.5}), ("f1", "filing", -3.6, -1.0, 1.5708), ("l1", "locker", 3.6, -1.0, -1.5708),
        ("cr", "crates", -3.0, -2.2, 0.0, {"n": 3, "seed": 5}),
    ],
    "decor": [
        ("props", "poster", "poster_safety", "S", -1.0, -3.0, 2.0, 0.7, 0.9), ("props", "poster", "sign_nosmoke", "N", -0.5, 3.0, 2.0, 0.3, 0.3),
        ("props", "poster", "fire_board", "W", -4.0, 1.5, 1.6, 0.5, 0.7), ("props", "extinguisher", "E", 4.0, 0.8),
        ("props", "wall_clock", "N", 1.0, 3.0, 2.8), ("props", "vent", "S", 1.5, -3.0, 2.8, {"w": 0.6, "h": 0.35}),
        ("props", "switch", "S", 2.2, -3.0), ("props", "outlet", "W", -4.0, -1.5), ("props", "bin_", 3.65, 2.6),
        ("props", "papers", 2.4, 2.3, 0.77, {"n": 3, "seed": 3}), ("props", "mug", 2.9, 2.2, 0.77), ("props", "ashtray", 2.1, 2.5, 0.77),
        ("props", "podstakannik", 2.0, 2.0, 0.77),
    ],
    "lamps": [[0, 0, 3.4, [1.0, 0.25, 0.2], 1.6, 9, True], [-2.8, 2.3, 1.6, [0.4, 1.0, 0.6], 1.2, 4, False], [2.6, 2.3, 1.4, [1.0, 0.8, 0.5], 1.2, 4, False]],
    "env": {"ambient": [0.07, 0.06, 0.07], "fog": [0.7, 0.4, 0.4], "density": 0.025},
    "start": [3.0, -2.4, 0], "dress": [153, 1.3, True],
    "sound": snd("concrete", 0.85, 0.3, emitters=[["fluorescent_buzz", [0, 0, 3.4], -22.0, 3.0]], life=life_building()),
    "npcs": [{"id": "sergei", "model": "sergei", "face": "face_sergei", "at": [1.5, 1.4], "voice": "low", "pitch": 1.0, "prompt": "Falar com Sergei",
              "size": [0.7, 1.8, 0.5]}],
    "intro": [["Madrugada no hangar. Sergei me chamou para me mostrar a chave do que construímos.", 5.5]],
    "clues": [
        {"id": "missil", "prompt": "Olhar o míssil Lethe", "at": [0.0, 0.3, 1.2], "size": [4.8, 1.2, 1.4],
         "note": "O Lethe aberto: dentro, nenhuma ogiva. Só uma cavidade de latão com bobinas. Um pulso, não uma bomba.",
         "alt": "Um míssil enorme, pintado de cinza.", "say": "Por dentro é oco. Por dentro, é uma lembrança vazia."},
        {"id": "chave", "prompt": "Pegar a chave", "at": [-2.8, 2.0, 1.2], "size": [0.4, 0.4, 0.4],
         "note": "Chave de aço numa corrente, presa ao console: abre o painel do pulso. Sergei a deixou à vista de propósito.",
         "say": "Uma chave pequena para um pulso enorme."},
        {"id": "painel", "prompt": "Olhar o painel do pulso", "at": [-2.8, 2.8, 1.5], "size": [2.0, 0.6, 1.0],
         "note": "Painel do pulso: o visor mostra 'ОПЕРАТОР: —' (operador: nenhum). O operador esquece primeiro; não há operador porque ele já esqueceu.",
         "say": "Operador: nenhum. Quem opera o Lethe esquece que o operou."},
        {"id": "pasta", "prompt": "Ler a pasta ЛЕТА", "at": [2.5, 2.3, 0.85], "size": [0.4, 0.4, 0.2], "item": ["flat", "folder_secret", 0.3, 0.22],
         "note": "Pasta 'ЛЕТА': protocolos de teste. Há um nome riscado na primeira linha da lista de cobaias; embaixo, a letra de Sergei: 'foi o primeiro'.",
         "alt": "Uma pasta de protocolos, nada demais.", "say": "Há um nome riscado na lista de cobaias. Não consigo lê-lo."},
        {"id": "gravacao", "prompt": "Ouvir o gravador", "at": [3.6, 2.8, 1.3], "size": [0.4, 0.4, 0.4],
         "note": "Gravador de fita: a voz de Lena, 'Serioja, lembre de mim', repetida. Sergei a ouve todas as noites aqui.", "optional": True,
         "say": "A mesma frase, em loop. Ele não consegue desligar."},
    ],
    "needed": ["missil", "chave", "painel", "pasta"],
    "talk": {"npc": "sergei", "hint": "Sergei me espera junto ao míssil. Acho que é hora de ouvi-lo.",
             "lines": ["SERGEI: Veja bem, Aleksey. Foi para isto que passei a vida. Não destrói cidades: devolve o descanso.",
                       "ALEKSEY: Devolve? Ele apaga quem o opera.",
                       "SERGEI: O primeiro que o operou escolheu esquecer. Eu fui quem apertou o botão. Eu sei quem você é.",
                       {"q": "Sergei não desvia os olhos de você. O que você faz?",
                        "opts": ["Negar: 'Não sei do que o senhor está falando.'", "Perguntar: 'Quem eu sou, Sergei?'"], "truth": [-1, 1], "flag": "sergei_sabe",
                        "reply": [["SERGEI: Como queira. Nós dois sabemos mentir muito bem."],
                                  ["SERGEI: Ainda não, meu filho. A verdade, dita agora, o mataria."]]},
                       "SERGEI: Leve a chave. Quando chegar a hora, você vai precisar dela."],
             "note": "Sergei disse: 'Eu sei quem você é.' E entregou a chave do painel do pulso.",
             "alt": "Sergei me deu uma chave. Confia em mim."},
}

# ======================================================================================================================
# 16 · F8 · O Parque Gorky · ago/1993 (exterior)
# ======================================================================================================================
def _park_prims():
    import math
    import random
    r = random.Random(93)
    p = [{"t": "light", "p": [0, 8, -10], "c": [1.0, 0.95, 0.8], "e": 0.6, "r": 40}]
    for i in range(34):
        p.append({"t": "tree", "p": [r.uniform(-45, 45), r.uniform(-60, 8)], "h": r.uniform(6, 11), "leaf": [0.22 + r.uniform(0, 0.1), 0.36 + r.uniform(0, 0.1), 0.15]})
    p.append({"t": "box", "p": [0, 0.02, -15], "s": [5, 0.04, 90], "c": [0.55, 0.5, 0.42]})                       # alameda central
    p.append({"t": "box", "p": [20, 0.03, -30], "s": [24, 0.06, 16], "c": [0.18, 0.28, 0.42], "glow": True})       # lago
    for k, (x, z, rot) in enumerate([(5.5, -12, 90), (-5.5, -22, -90), (5.5, -34, 90), (-5.5, -6, -90)]):
        p.append({"t": "bench", "p": [x, z], "rot": rot})
    for x in (-3.5, 3.5):
        for z in (0, -20, -40):
            p.append({"t": "lamp", "p": [x, z]})
    p += [{"t": "ring", "p": [-35, 12, -55.3], "r": 10.0, "w": 0.35, "rx": 90, "c": [0.6, 0.6, 0.62]},                    # roda-gigante: aro,
          {"t": "ring", "p": [-35, 12, -55.7], "r": 9.4, "w": 0.2, "rx": 90, "c": [0.7, 0.2, 0.2]},
          {"t": "cyl", "p": [-35, 12, -55.5], "r": 0.7, "h": 1.0, "rx": 90, "c": [0.45, 0.45, 0.48]},                     # cubo
          {"t": "box", "p": [-35, 6, -55.5], "s": [0.6, 12, 0.6], "c": [0.45, 0.45, 0.48]}]
    for k in range(10):                                                                                          # e raios até cada cabine
        a = k * 360 / 10
        p.append({"t": "box", "p": [-35 + 5 * math.cos(math.radians(a)), 12 + 5 * math.sin(math.radians(a)), -55.3], "s": [10, 0.12, 0.12],
                  "rz": a, "c": [0.6, 0.6, 0.62]})
    for k in range(10):
        a = k * math.tau / 10
        p.append({"t": "box", "p": [-35 + 10 * math.cos(a), 12 + 10 * math.sin(a), -55], "s": [1.4, 1.0, 1.0], "c": [0.8, 0.3 + 0.05 * k, 0.2]})
    p += [{"t": "box", "p": [-8, 1.2, -14], "s": [2.0, 2.4, 2.0], "c": [0.85, 0.85, 0.8], "solid": True},                # quiosque de sorvete
          {"t": "box", "p": [-8, 2.5, -14], "s": [2.4, 0.2, 2.4], "c": [0.8, 0.2, 0.25]},                                 # toldo assentado no quiosque
          {"t": "box", "p": [3.5, 1.3, -4], "s": [0.2, 1.6, 1.4], "c": [0.15, 0.3, 0.2], "solid": True},               # placa de entrada
          {"t": "box", "p": [3.5, 0.25, -4.55], "s": [0.08, 0.5, 0.08], "c": [0.2, 0.2, 0.22]},                        # e seus postes
          {"t": "box", "p": [3.5, 0.25, -3.45], "s": [0.08, 0.5, 0.08], "c": [0.2, 0.2, 0.22]},
          {"t": "people", "p": [-12, -30], "n": 5, "r": 4.0}, {"t": "people", "p": [14, -8], "n": 4, "r": 3.0}]
    return p


SPECS["parque"] = {
    "kind": "outdoor", "title": ["AGO / 1993", "O PARQUE GORKY"], "tint": TINT_F,
    "sky": {"top": [0.42, 0.58, 0.82], "horizon": [0.92, 0.88, 0.78]}, "sun": {"rot": [-45, 30], "color": [1.0, 0.92, 0.75], "energy": 1.4},
    "ambient": 1.1, "env": {"fog": [0.85, 0.85, 0.8], "density": 0.003}, "ground": {"color": [0.30, 0.38, 0.20]},
    "start": {"pos": [0, 0.05, 8], "yaw": 0}, "primitives": _park_prims(),
    "sound": snd("concrete", 0.9, 0.3, amb_db=-30.0, emitters=[["crowd_murmur", [14, 1.5, -8], -18.0, 8.0]],
                 life=[["siren_far", 70.0, 140.0, -18.0, [0, 3, -50], [20, 1, 5]]]),
    "npcs": [{"id": "irina", "model": "irina", "face": "face_irina", "pos": [4.2, -12.0], "voice": "high", "pitch": 0.92, "prompt": "Falar com Irina",
              "size": [0.6, 1.8, 0.5]}],
    "intro": [["Verão no parque. As pessoas passeiam como se nada fosse acontecer.", 4.5]],
    "clues": [
        {"id": "placa", "prompt": "Ler a placa do parque", "at": [3.5, 1.3, -4.0], "size": [0.5, 1.6, 1.4],
         "note": "Placa de entrada: 'Парк культуры и отдыха им. М. Горького'. Parque de cultura e descanso, dizia. Eu vim a trabalho.",
         "alt": "Placa de um parque.", "say": "Parque de descanso. Hoje descanso é palavra suspeita."},
        {"id": "roda", "prompt": "Olhar a roda-gigante", "at": [-12.0, 1.0, -30.0], "size": [2.0, 2.0, 2.0],
         "note": "A roda-gigante gira vazia, rangendo. Crianças fingem que não ouvem. Ao fundo, a sombra do Kosmos no horizonte.",
         "say": "A roda gira sem ninguém. Como a minha cabeça."},
        {"id": "lago", "prompt": "Olhar o lago", "at": [12.0, 0.4, -26.0], "size": [6.0, 0.8, 4.0],
         "note": "Casal de patos no lago. Um senhor lê jornal na margem: 'Совет Министров'. Alguém me vigia mesmo aqui.",
         "alt": "Um lago bonito.", "say": "O senhor do jornal não vira a página. Está me vigiando."},
        {"id": "sorvete", "prompt": "Olhar o quiosque de sorvete", "at": [-8.0, 1.2, -14.0], "size": [2.4, 2.4, 2.4],
         "note": "Quiosque de sorvete: 'Эскимо 28 коп.' O preço está riscado e reescrito três vezes: inflação até no verão.", "optional": True,
         "say": "O preço mudou três vezes neste verão."},
    ],
    "needed": ["placa", "roda", "lago"],
    "talk": {"npc": "irina", "hint": "Irina me espera num banco, os óculos escuros na mão. Acho que é hora de falar.",
             "lines": ["IRINA: Aleksey. Você está bem. Os dois anos fizeram bem.",
                       "ALEKSEY: Fizeram de mim outra pessoa.",
                       "IRINA: Foi para isso. Escute: na segunda você começa no Kosmos, como consultor. Sergei Morozov será seu contato.",
                       "IRINA: Karpov quer o Lethe. Você é meus olhos lá dentro. Quando eu pedir, você age.",
                       {"q": "Irina pousa a mão em seu braço. O que você diz?",
                        "opts": ["Aceitar a missão sem perguntas", "Perguntar: 'O que eu ganho com isso?'"], "truth": [-1, 1], "flag": "missao_aceita",
                        "reply": [["IRINA: Esse é o homem que eu preparei."], ["IRINA: Uma vida. Nada mais. É mais do que a maioria recebe."]]},
                       "IRINA: Hoje é o último dia de sol, Aleksey. Aproveite."],
             "note": "Irina me deu a missão: infiltrar o Kosmos. Sergei Morozov será meu contato. Karpov quer o Lethe.",
             "alt": "Começo a trabalhar no Kosmos na segunda. Bom emprego."},
}
