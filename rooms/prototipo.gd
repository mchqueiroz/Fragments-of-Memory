extends Room
## Cena 4 — A Sala do Protótipo (jul/1991, linha F, quente). Misha entre os primeiros testes do Lethe; Lena, doente,
## traz chá e pergunta duas vezes quem é Misha: ela é a primeira a esquecer. O peão de Boris vai parar no tabuleiro de Sergei.
## Veja docs/superpowers/specs/2026-10-22-ato1-objetos-design.md, cena 4.

const NEEDED := ["proto", "quadro", "gravador", "caderno", "tabuleiro", "foto"]

var _lena: Actor
var _done := {}
var _ending := false


func _ready() -> void:
	add_child(model("prototipo"))
	environment(Color(0.20, 0.17, 0.12), Color(0.95, 0.85, 0.6), 0.025)
	backdrop_kosmos(130.0)
	lamp(Vector3(0.0, 1.9, 2.0), Color(1.0, 0.9, 0.65), 3.0, 6.5, false)        # sol de julho pela janela
	lamp(Vector3(0.0, 2.7, -0.2), Color(1.0, 0.95, 0.8), 1.4, 6.0)
	lamp(Vector3(2.4, 1.3, 0.0), Color(0.3, 1.0, 0.5), 0.5, 2.0, false)          # brilho dos osciloscópios
	dress(3.0, 2.5, 3.0, 41, 1.0)
	life([["tram_pass", 40.0, 80.0, -13.0, Vector3(0, 1.5, -8.0), Vector3(2, 1, 1)],
		["siren_far", 60.0, 120.0, -15.0, Vector3(0, 2.0, -9.0), Vector3(3, 1, 1)],
		["pipes_knock", 25.0, 60.0, -13.0, Vector3(3.0, 1.0, 0), Vector3(0, 0.5, 2)]])
	dust(Vector3(2.5, 1.2, 2.0), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "theme_sergei", -30.0, "parquet", 0.5, 0.18)
	setup_player(Vector3(0.0, 0.05, 2.0), 0.0, 62.0, Vector3(1.12, 0.98, 0.82))
	player.interacted.connect(_on_interacted)

	_lena = Actor.new()
	_lena.position = Vector3(-0.9, 0, 0.4)
	add_child(_lena)
	_lena.setup("lena", "face_lena", player)
	_lena.voice_tag = "high"
	clue_on(_lena, "lena", "Falar com Lena", Vector3(0, 0.9, 0), Vector3(0.6, 1.8, 0.5))

	clue("proto", "Olhar a caixa de latão", Vector3(0.0, 0.97, -1.45), Vector3(0.5, 0.4, 0.2))
	clue("quadro", "Olhar o quadro-negro", Vector3(-2.9, 1.6, -0.3), Vector3(0.15, 1.3, 2.6))
	clue("gravador", "Ouvir o gravador", Vector3(0.9, 0.88, -1.6), Vector3(0.32, 0.14, 0.24))
	clue("caderno", "Ler o caderno de Lena", Vector3(-0.8, 0.8, -1.5), Vector3(0.2, 0.06, 0.25))
	clue("xicaras", "Olhar as xícaras", Vector3(-0.4, 0.85, -1.8), Vector3(0.3, 0.1, 0.25))
	clue("foto", "Olhar a foto", Vector3(2.95, 1.7, -1.55), Vector3(0.1, 0.6, 0.5))
	var chess := model("chess")
	chess.position = Vector3(2.5, 0.81, 0.6)
	chess.scale = Vector3.ONE * 0.6
	add_child(chess)
	var tab := clue("tabuleiro", "Examinar o tabuleiro de Sergei", chess.position + Vector3(0, 0.05, 0), Vector3(0.3, 0.1, 0.3))
	tab.set_meta("visual", chess.get_path())
	tab.set_meta("text", "O tabuleiro de Sergei. Falta o peão branco: o meu vai ocupar o lugar dele.")
	_intro()


func _intro() -> void:
	question = "O que é essa caixa de latão?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("JUL / 1991", "A SALA DO PROTÓTIPO", 3.5)
	await get_tree().create_timer(2.5).timeout
	Story.say("Aqui o Lethe ainda era só uma caixa e uma ideia boa.", 5.0)
	cinema.letterbox(false, 1.5)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "lena":
		_talk_lena()
		return
	if id == "tabuleiro":
		if not _done.has(id):
			_done[id] = true
			Story.add_note("Tabuleiro de Sergei: partida parada. Falta um peão branco, e o meu está no meu bolso.")
			_check()
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"proto":
			Story.add_note("Caixa de latão com mostrador 'ЛЕТА'. Fita crepe: 'НЕ ТРОГАТЬ'. Não toque.",
				"Uma caixa velha. Sem importância.")
			Story.say("Uma caixa de latão. Parece inofensiva. Não deveria.", 4.5)
		"quadro":
			Story.add_note("Quadro-negro: equações que terminam num círculo riscado, o símbolo do vazio.")
			Story.say("Todas as equações acabam no mesmo lugar: o nada.", 4.5)
		"gravador":
			Story.add_note("Gravador de fita com uma fita 'ЛЕНА 1991'. Ela gravou a própria voz para não esquecer?",
				"Um gravador. Nada de especial.", "prototipo:fita")
			Story.say("A fita diz Lena, 1991. Ela gravou a própria voz.", 4.5)
		"caderno":
			Story.add_note("Caderno de Lena: Борис, Сергей, Ирина, Миша, todos riscados, menos o dela mesma.",
				"Um caderno de nomes. Ela é desorganizada.")
			Story.say("Ela riscou todo mundo. Só o nome dela ficou.", 4.5)
		"xicaras":
			Story.add_note("Xícaras lascadas: chá frio. Lena traz chá todo dia e esquece de beber.")
		"foto":
			Story.add_note("Foto de Lena jovem, rindo. Antes de ficar doente.")
			Story.say("Ela ria assim quando a conheci.", 4.0)
	_check()


func _check() -> void:
	if not _ending and _all_done():
		Story.say("Lena me olha com o chá na mão. Acho que posso conversar com ela agora.", 4.5)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _talk_lena() -> void:
	if _ending:
		return
	if not _all_done():
		Story.say("LENA: Olhe à vontade. O chá ainda está quente.", 4.0)
		return
	_ending = true
	_lena.speak(100.0)
	await Story.talk([
		"LENA: Trouxe chá. Você é novo aqui? Como você se chama?",
		"MISHA: Misha, Lena. Mikhail.",
		"LENA: Misha. Eu escrevi esse nome, não escrevi? Desculpe. ...Quem é Misha?",
		{"q": "Lena pergunta de novo, com medo de ter esquecido. O que você diz?",
		 "opts": ["A verdade: 'Sou eu, Lena. Eu sou o Misha.'", "Poupar: 'Um amigo. Vai passar, não se preocupe.'"], "truth": [1, -1],
		 "reply": [["LENA: Você... sim. Você deixa meu chá esfriar. Eu lembro disso."],
				   ["LENA: Um amigo. Que bom. Então ele deve ser uma boa pessoa."]]},
		"LENA: Sergei disse que você traria um peão. Para o jogo dele.",
		"MISHA: Trouxe. Era do nosso pai. Sergei quer ver.",
		"LENA: Então leve. Mas guarde de onde veio, Misha. Isto aqui esquece tudo.",
	])
	_lena.speak(0.05)
	Story.add_note("Lena perguntou duas vezes quem eu era. Dei o peão ao tabuleiro de Sergei.",
		"Lena está confusa. Entreguei o peão a Sergei.")
	Sound.play("chess_click", "Sfx", -2.0)
	Story.say("O peão branco entrou no tabuleiro. Sergei vai gostar.", 3.5)
	await get_tree().create_timer(3.0).timeout
	Story.next_scene()
