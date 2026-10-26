extends Room
## Cena 5 — O Gabinete (T−2h30, linha A, fria). Aleksey sem memória volta ao gabinete de Sergei, que está parado no tempo
## (calendário em março de 1992, dois copos de chá, retrato de Lena virado para a cadeira, espelho coberto, a porta do
## quarto de Lena com luz e voz atrás). Sergei conversa depois de o jogador ler o cômodo; entrega o cartão de acesso.
## Escolha de peso: "sou seu amigo" (truth −1) ou "há coisas que não contei" (truth +1).
## Veja docs/superpowers/specs/2026-10-22-ato1-objetos-design.md, cena 5. Eixos: Blender (x, y, z) -> Godot (x, z, -y).

const NEEDED := ["lenin", "calendario", "copo", "retrato", "espelho", "plantas"]

var _sergei: Actor
var _done := {}
var _talked := false
var _card := false
var _card_body: StaticBody3D
var _exit_body: StaticBody3D


func _ready() -> void:
	add_child(model("gabinete"))
	environment(Color(0.09, 0.075, 0.07), Color(0.85, 0.75, 0.62), 0.022)
	lamp(Vector3(0, 2.15, 0), Color(1.0, 0.70, 0.40), 1.3, 6.0)           # pendente fraco: não ilumina os cantos
	lamp(Vector3(-1.6, 1.7, -2.4), Color(0.30, 0.45, 1.0), 1.5, 4.5, false)  # frio de fora pelas janelas
	lamp(Vector3(1.6, 1.7, -2.4), Color(0.30, 0.45, 1.0), 1.5, 4.5, false)
	lamp(Vector3(2.8, 1.55, -1.6), Color(1.0, 0.58, 0.22), 1.6, 4.0)     # abajur de pé, ao lado do sofá
	lamp(Vector3(3.1, 1.92, -2.15), Color(1.0, 0.12, 0.06), 0.9, 2.2, false)  # lamparina vermelha do ícone
	lamp(Vector3(2.75, 0.12, -2.62), Color(1.0, 0.8, 0.45), 0.8, 1.6, false)  # luz sob a porta do quarto de Lena
	var spot := SpotLight3D.new()                                        # abajur de banqueiro, verde, sobre a mesa
	spot.light_color = Color(0.7, 1.0, 0.75)
	spot.light_energy = 3.2
	spot.spot_range = 3.0
	spot.spot_angle = 55.0
	spot.shadow_enabled = true
	add_child(spot)
	spot.look_at_from_position(Vector3(-0.85, 1.0, -1.55), Vector3(-0.3, 0.7, -1.2))
	dress(3.2, 2.8, 3.3, 1993, 0.8)
	life([["tram_pass", 35.0, 70.0, -13.0, Vector3(0, 1.5, -6.0), Vector3(2, 1, 1)],
		["siren_far", 50.0, 100.0, -16.0, Vector3(0, 2.0, -7.0), Vector3(3, 1, 1)],
		["upstairs_steps", 20.0, 55.0, -14.0, Vector3(0, 3.2, 0), Vector3(2, 0, 2)],
		["pipes_knock", 30.0, 70.0, -13.0, Vector3(-3.0, 1.0, 0), Vector3(0, 0.5, 2)]])
	dust(Vector3(3.0, 1.5, 2.5), Vector3(0, 1.6, 0))
	Sound.scene("amb_room", "theme_sergei", -15.0, "parquet", 0.35, 0.14)
	Sound.emitter(self, "radio_real", Vector3(-2.6, 1.4, 2.3), -11.0, 2.5)         # rádio: leitura real em russo (Mandelstam)
	Sound.emitter(self, "lena_tape", Vector3(2.75, 1.4, -3.0), -9.0, 2.2, 1500.0)  # voz de mulher atrás da porta de Lena
	Sound.emitter(self, "clock_loop", Vector3(-0.45, 2.45, 2.75), -12.0, 2.0)      # relógio de parede
	setup_player(Vector3(1.9, 0.05, 2.2), 0.0, 68.0, Vector3(1.12, 0.98, 0.84))
	player.interacted.connect(_on_interacted)

	_sergei = Actor.new()
	_sergei.position = Vector3(1.25, 0, -1.8)
	add_child(_sergei)
	_sergei.setup("sergei", "face_sergei", player)
	clue_on(_sergei, "sergei", "Falar com Sergei", Vector3(0, 0.9, 0), Vector3(0.7, 1.8, 0.5))

	clue("lenin", "Olhar a mancha na parede", Vector3(0, 2.1, -2.75), Vector3(0.7, 0.9, 0.2))
	clue("calendario", "Olhar o calendário", Vector3(-2.0, 2.0, 2.75), Vector3(0.5, 0.65, 0.2))
	clue("copo", "Olhar os copos de chá", Vector3(-0.15, 0.84, -1.12), Vector3(0.14, 0.16, 0.12))
	clue("retrato", "Olhar o retrato de Lena", Vector3(-0.9, 0.9, -1.92), Vector3(0.2, 0.26, 0.1))
	clue("espelho", "Olhar o espelho coberto", Vector3(-2.72, 1.1, -2.75), Vector3(0.7, 1.9, 0.2))
	clue("izvestia", "Ler o jornal", Vector3(0.55, 0.79, -1.45), Vector3(0.3, 0.06, 0.3))
	clue("porta", "Escutar a porta de Lena", Vector3(2.75, 1.05, -2.74), Vector3(0.9, 2.1, 0.2))
	clue("icone", "Olhar o ícone", Vector3(3.15, 2.07, -2.15), Vector3(0.1, 0.45, 0.35))
	clue("samovar", "Olhar o samovar", Vector3(-2.15, 0.62, 1.15), Vector3(0.3, 0.5, 0.3))
	clue("fitas", "Olhar as fitas de Lena", Vector3(2.6, 0.7, -1.05), Vector3(0.4, 0.15, 0.3))
	var chess := model("chess")
	chess.position = Vector3(1.15, 0.475, 0.6)
	add_child(chess)
	var tab := clue("tabuleiro", "Examinar o tabuleiro", chess.position, Vector3(0.46, 0.1, 0.46))
	tab.set_meta("visual", chess.get_path())
	tab.set_meta("text", "Uma partida inacabada. Falta um peão branco, sacrificado no lance 14.")
	var plans := model("plans")
	plans.position = Vector3(-0.15, 0.78, -1.35)
	plans.rotation.y = 0.4
	add_child(plans)
	var pl := clue("plantas", "Ler as plantas", plans.position + Vector3(-0.2, 0, -0.15), Vector3(0.4, 0.08, 0.3))
	pl.set_meta("visual", plans.get_path())
	pl.set_meta("text", "LETHE. Não é um míssil: é um pulso que apaga a memória. O operador será o primeiro a esquecer.")
	_card_body = clue("cartao", "Pegar o cartão no casaco", Vector3(0.95, 1.35, 2.45), Vector3(0.45, 0.9, 0.3), false)
	_exit_body = clue("saida", "Sair do gabinete", Vector3(2.1, 1.05, 2.76), Vector3(0.98, 2.1, 0.2), false)
	_intro()


func _intro() -> void:
	question = "Por que Sergei me espera?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("T − 2H30", "O GABINETE DE SERGEI", 3.5)
	await get_tree().create_timer(2.5).timeout
	Story.say("Tudo aqui parou. Menos o homem sentado.", 4.5)
	cinema.letterbox(false, 1.5)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	match id:
		"sergei":
			_talk_sergei()
			return
		"cartao":
			_take_card(t)
			return
		"saida":
			Story.next_scene()
			return
		"tabuleiro":
			if not _done.has(id):
				_done[id] = true
				Story.add_note("Tabuleiro de Sergei: partida inacabada. Falta um peão branco, sacrificado no lance 14.")
			return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"lenin":
			Story.add_note("Mancha clara na parede: aqui estava o retrato de Lenin. Alguém o tirou em 1991 e ninguém pintou.")
			Story.say("O retângulo limpo onde havia um retrato. O país também mudou de parede.", 5.0)
		"calendario":
			Story.add_note("Calendário parado em março de 1992. Sergei parou o tempo no dia em que Lena morreu.",
				"Calendário velho. Sergei é desleixado.")
			Story.say("Março de 1992. Faz mais de um ano.", 4.0)
		"copo":
			Story.add_note("Dois copos de chá. Um usado. O outro, cheio e frio, intocado: ele serve chá para quem não vem.",
				"Dois copos. Um esqueceu de lavar.")
			Story.say("Um copo cheio, intocado. Para quem?", 4.0)
		"retrato":
			Story.add_note("O retrato de Lena, virado para a cadeira dele. Ele a vê quando trabalha.")
			Story.say("Ela fica olhando a cadeira. Ou ele fica olhando para ela.", 4.5)
		"espelho":
			Story.add_note("Espelho coberto com pano preto, como se cobre em casa onde alguém morreu.")
			Story.say("Cobrem os espelhos quando alguém morre.", 4.0)
		"izvestia":
			Story.add_note("Izvestia de 3 de outubro de 1993: 'Tanques na ponte'. É hoje.")
			Story.say("Três de outubro. É hoje. Tudo isto é hoje.", 4.5)
		"porta":
			Story.add_note("Atrás da porta do quarto de Lena há luz e uma voz de mulher lendo Pushkin. Lena morreu em 1992.")
			Story.say("Uma voz de mulher lendo Pushkin. Ela morreu em 1992.", 5.0)
		"icone":
			Story.add_note("Ícone com uma lamparina vermelha acesa. Sergei não é crente, mas não deixa a chama apagar.")
		"samovar":
			Story.add_note("Samovar quente. Alguém ferve água todo dia nesta casa.")
		"fitas":
			Story.add_note("Fitas etiquetadas 'ЛЕНА' ao lado do gravador. A voz atrás da porta sai daqui?",
				"Fitas velhas de Lena.")
			Story.say("Todas com o nome dela.", 3.5)
		"plantas":
			Story.add_note("Plantas do LETHE: um pulso que apaga a memória. O operador será o primeiro a esquecer.",
				"Plantas do Lethe. Parece só um míssil.", "gabinete:plantas")
	_check()


func _check() -> void:
	if not _talked and _all_done():
		Story.say("Sergei me observa da cadeira. Acho que posso conversar com ele agora.", 4.5)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _talk_sergei() -> void:
	if _talked:
		return
	if not _all_done():
		Story.say("SERGEI: Olhe à vontade, Aleksey. Nada aqui mudou. Esse é o problema.", 4.0)
		return
	_talked = true
	cinema.letterbox(true, 0.8)
	Sound.duck(true)
	_sergei.speak(100.0)
	await Story.talk([
		"SERGEI: Você voltou. Senta. O chá é seu. O outro... deixa.",
		"ALEKSEY: Sergei, eu preciso saber o que eu fiz.",
		"SERGEI: Você leu as plantas. O Lethe não destrói cidades, destrói quem o opera. E ele escolheu você.",
		{"q": "Sergei espera. O que você diz?",
		 "opts": ["'Sou seu amigo, Sergei. Pode me dizer.'", "'Há coisas que eu não contei a você.'"], "truth": [-1, 1], "trust": {"sergei": [-1, 1]},
		 "reply": [["SERGEI: Amigo. Você era como um filho. Por isso dói."],
				   ["SERGEI: Eu sei. Há semanas."]]},
		"SERGEI: Pega o cartão no meu casaco. Abre o que você escondeu.",
		"SERGEI: E, Aleksey: não confie em tudo o que o seu corpo diz sobre mim.",
	])
	_sergei.speak(0.05)
	cinema.letterbox(false, 1.2)
	Sound.duck(false)
	Story.add_note("Sergei me mandou pegar o cartão de acesso no casaco dele. 'Não confie no que o seu corpo diz sobre mim.'",
		"Sergei me deu um cartão. Ele sabe mais do que diz.")
	_card_body.add_to_group("clue")


func _take_card(t: Node3D) -> void:
	if _card:
		return
	_card = true
	t.remove_from_group("clue")
	Sound.play("pickup", "Sfx", -2.0)
	Story.give("cartao")
	Story.add_note("Cartão de acesso do Kosmos, com um número: o código que eu gravei na pele. Hora de sair.",
		"Um cartão de acesso. Sergei confia em mim.")
	Story.say("O cartão abre a porta que eu mesmo escondi.", 4.0)
	_exit_body.add_to_group("clue")
