extends Room
## Cena 2 — A Cozinha dos Volkov (jun/1991, linha F, quente). Misha, o irmão, e Boris, que o esperou com o jantar.
## Veja docs/superpowers/specs/2026-10-22-ato1-objetos-design.md. Técnicas: luz de janela ao pôr do sol; a melodia
## G-D-E-D assobiada sem perceber (a primeira vez que o jogador a ouve); Boris só fala depois de o jogador explorar,
## como em Gone Home: o jogador descobre o que a cozinha diz antes de a conversa começar.

const NEEDED := ["mesa", "radio", "farda", "fosforos", "foto", "calendario", "tabuleiro"]

var _boris: Actor
var _done := {}
var _ending := false


func _ready() -> void:
	add_child(model("cozinha"))
	environment(Color(0.22, 0.15, 0.10), Color(0.85, 0.65, 0.45), 0.03)
	lamp(Vector3(-0.1, 1.5, -1.5), Color(1.0, 0.55, 0.25), 3.2, 4.5, false)   # pôr do sol pela janela
	lamp(Vector3(0.0, 2.2, 0.0), Color(1.0, 0.82, 0.55), 1.9, 5.0)            # lâmpada nua
	lamp(Vector3(1.45, 1.1, -0.2), Color(1.0, 0.5, 0.2), 0.5, 1.6, false)    # brilho do fogão
	dress(1.8, 1.5, 2.6, 11, 0.9)
	Sound.emitter(self, "neighbor_music", Vector3(-1.8, 1.6, 0.0), -24.0, 2.0, 1800.0)             # vizinho com bayan atrás da parede
	life([["pipes_knock", 20.0, 50.0, -12.0, Vector3(1.8, 1.0, 0.0), Vector3(0, 0.5, 1.4)],
		["tram_pass", 40.0, 80.0, -13.0, Vector3(0, 1.5, 4.0), Vector3(2, 1, 1)],
		["upstairs_steps", 25.0, 60.0, -14.0, Vector3(0, 2.7, 0), Vector3(1, 0, 1)]])
	dust(Vector3(1.6, 1.2, 1.3), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "theme_sergei", -30.0, "lino", 0.25, 0.1)
	Sound.emitter(self, "kettle", Vector3(1.45, 1.15, -0.2), -9.0, 1.5)       # chaleira no fogo
	Sound.emitter(self, "radio_real", Vector3(-0.35, 1.04, -1.3), -10.0, 1.5)  # Spidola: notícias (leitura real em russo)

	setup_player(Vector3(0.95, 0.05, 1.05), 0.0, 62.0, Vector3(1.12, 0.98, 0.82))
	player.interacted.connect(_on_interacted)

	_boris = Actor.new()
	_boris.position = Vector3(0.95, 0, -0.35)   # junto ao fogão, de pé, de frente para a mesa
	add_child(_boris)
	_boris.setup("boris", "face_boris", player)
	_boris.voice_pitch = 0.85
	clue_on(_boris, "boris", "Falar com Boris", Vector3(0, 0.9, 0), Vector3(0.7, 1.8, 0.5))

	clue("mesa", "Olhar a mesa", Vector3(-1.15, 0.8, -0.4), Vector3(0.8, 0.15, 0.8))
	clue("radio", "Ouvir o rádio", Vector3(-0.35, 1.04, -1.3), Vector3(0.36, 0.2, 0.2))
	clue("farda", "Olhar o quepe e a jaqueta", Vector3(-0.5, 1.25, 1.38), Vector3(0.45, 0.85, 0.3))
	clue("fosforos", "Pegar a caixa de fósforos", Vector3(-1.35, 0.82, 0.15), Vector3(0.2, 0.12, 0.16))
	clue("foto", "Olhar a foto dos pais", Vector3(-1.77, 1.75, -0.2), Vector3(0.1, 0.6, 0.78))
	clue("calendario", "Olhar o calendário", Vector3(1.77, 1.5, 0.55), Vector3(0.1, 0.5, 0.4))
	var chess := model("chess")
	chess.position = Vector3(0.2, 0.95, -1.32)                                  # assentado no peitoril (topo 0,94)
	chess.scale = Vector3.ONE * 0.6
	add_child(chess)
	var tab := clue("tabuleiro", "Examinar o tabuleiro", chess.position, Vector3(0.3, 0.1, 0.3))
	tab.set_meta("visual", chess.get_path())
	tab.set_meta("text", "O tabuleiro do pai. Falta um peão branco.")
	_intro()


func _intro() -> void:
	question = "Quem é esse homem à mesa?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("JUN / 1991", "A COZINHA DOS VOLKOV", 3.5)
	await get_tree().create_timer(1.8).timeout
	Sound.play("whistle_motif", "Sfx", -7.0)   # Misha assobia G-D-E-D sem perceber
	Story.say("Eu lavava a louça. E assobiava, sem perceber.", 5.0)
	await get_tree().create_timer(5.5).timeout
	Story.say("[E] examinar     [Tab] diário     [Shift] correr     [Esc] pausa", 5.0)
	cinema.letterbox(false, 1.5)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "boris":
		_talk_boris()
		return
	if id == "tabuleiro":
		if not _done.has(id):
			_note(id, "O tabuleiro do pai, na janela. Falta um peão branco.", "Um tabuleiro velho. Nada de especial.")
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"mesa":
			_note(id, "Mesa da cozinha: um prato coberto por outro prato, ainda frio. Boris esperou o jantar até esfriar.",
				"Mesa da cozinha: comida fria. Boris sempre se faz de vítima.")
			Story.say("Um prato coberto por outro prato. Ele me esperou.", 4.5)
		"radio":
			_note(id, "Spidola: notícias de Moscou. Fala-se em 'medidas excepcionais'. Todo mundo sussurra a palavra golpe.")
			Story.say("O locutor fala em medidas excepcionais. Ninguém na rua acredita.", 5.0)
		"farda":
			_note(id, "Quepe e jaqueta de milícia no gancho. Boris é policial. Orgulhoso e cansado.")
			Story.say("Ele trabalha dobrado para eu estudar. E eu nunca disse obrigado.", 5.0)
		"fosforos":
			_note(id, "No bolso do meu paletó: uma caixa de fósforos com um número rabiscado. Não é da cozinha.",
				"Fósforos. Nada de importante.")
			Story.say("Eu não deveria ter isto aqui. Se Boris vir...", 4.5)
		"foto":
			_note(id, "Foto dos pais. O canto queimado, no dia em que o pai morreu.")
			Story.say("Mamãe sorri. O canto queimou no dia em que o pai morreu.", 4.5)
		"calendario":
			_note(id, "Calendário de junho. O dia 19 está marcado com um círculo: aniversário de Boris. Eu quase esqueci.")
			Story.say("Dia 19. Aniversário dele. Eu quase esqueci de novo.", 4.5)


func _note(id: String, text: String, alt := "") -> void:
	_done[id] = true
	Story.add_note(text, alt)
	_check()


func _check() -> void:
	if not _ending and _all_done():
		Story.say("Boris me observa da mesa. Acho que posso conversar com ele agora.", 4.5)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _talk_boris() -> void:
	if _ending:
		return
	if not _all_done():
		Story.say("BORIS: Senta, come alguma coisa. Depois a gente conversa.", 4.0)
		return
	_ending = true
	_boris.speak(90.0)
	await Story.talk([
		"BORIS: Você chegou tarde. A comida esfriou. Eu esperei.",
		"MISHA: Foi o trabalho, Boris.",
		"BORIS: Trabalho. Faz duas semanas que só existe 'trabalho'. Sai de manhã com a pasta, volta de noite com outro cheiro.",
		{"q": "Boris olha para o bolso do seu paletó, onde está a caixa de fósforos. O que você diz?",
		 "opts": ["A verdade: 'Estou conversando com a KGB.'", "Mentir: 'É só um projeto do instituto.'"], "truth": [1, -1], "trust": {"boris": [1, -1]},
		 "reply": [["BORIS: ...Então é verdade. Misha, essa gente não devolve ninguém inteiro."],
				   ["BORIS: Projeto. Tá bom. Come, antes que esfrie de vez."]]},
		"BORIS: Escuta. O papai dizia que um peão que chega ao fim do tabuleiro vira o que quiser.",
		"BORIS: Toma. Para o seu primeiro grande lance. Não esquece de onde você veio.",
	])
	_boris.speak(0.05)
	Story.add_note("Boris me deu o peão branco do papai. 'Não esquece de onde você veio.'",
		"Boris me deu um peão velho. Sentimental. Mas pode ser útil.", "cozinha:peao")
	Sound.play("pickup", "Sfx", -2.0)
	Story.say("O peão é pequeno. Pesa mais do que devia.", 3.5)
	await get_tree().create_timer(3.0).timeout
	Story.next_scene()
