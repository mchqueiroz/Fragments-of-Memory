extends Room
## Cena 7 — O Quarto de Lena (T−6h, linha A, fria). A cena mais lenta do Ato I: silêncio quase total, só a fita de Lena.
## Aleksey descobre que Lena lembrava de Misha e esqueceu o próprio marido. Escolha de peso: levar o caderno (truth +1)
## ou deixá-lo (truth −1); `Story.flags["caderno"]` guarda a decisão para a cena 10. Veja ato1-objetos-design.md, cena 7.

const NEEDED := ["cama", "chinelos", "gravador", "remedios", "fotos", "janela", "icone", "cartao"]

var _tape: AudioStreamPlayer3D
var _notebook: StaticBody3D
var _exit: StaticBody3D
var _done := {}
var _decided := false


func _ready() -> void:
	add_child(model("quarto"))
	environment(Color(0.07, 0.08, 0.11), Color(0.60, 0.70, 0.85), 0.02)
	lamp(Vector3(-0.5, 1.8, 1.4), Color(0.55, 0.70, 1.0), 1.6, 4.0, false)           # gelo e luz fria da janela
	lamp(Vector3(1.88, 1.7, -0.8), Color(1.0, 0.62, 0.25), 0.9, 2.6)                 # vela do ícone: tremula
	lamp(Vector3(-0.55, 1.0, -1.4), Color(1.0, 0.75, 0.45), 0.5, 1.8, false)         # brilho do gravador
	dress(2.0, 1.8, 2.7, 71, 0.8)
	Sound.emitter(self, "neighbor_music", Vector3(2.0, 1.5, 0.0), -32.0, 2.0, 1500.0)
	life([["pipes_knock", 40.0, 90.0, -16.0, Vector3(2.0, 1.0, 0), Vector3(0, 0.5, 1.5)],
		["upstairs_steps", 60.0, 120.0, -18.0, Vector3(0, 2.7, 0), Vector3(1, 0, 1)]])
	dust(Vector3(1.8, 1.0, 1.6), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "tinnitus", -80.0, "parquet", 0.3, 0.12)
	Sound._amb.volume_db = -38.0                                                     # silêncio quase total: só a fita
	Sound._amb.set_meta("db", -38.0)
	_tape = Sound.emitter(self, "lena_tape", Vector3(-0.55, 0.65, -1.5), -4.0, 1.8)
	setup_player(Vector3(1.2, 0.05, 1.2), 0.0, 60.0, Vector3(0.92, 1.0, 1.1))
	player.interacted.connect(_on_interacted)

	clue("cama", "Olhar a cama", Vector3(-1.3, 0.6, 0.6), Vector3(0.8, 0.2, 0.5))
	clue("chinelos", "Olhar os chinelos e a bengala", Vector3(-0.6, 0.3, 0.3), Vector3(0.4, 0.6, 0.45))
	clue("gravador", "Olhar o gravador", Vector3(-0.55, 0.64, -1.5), Vector3(0.3, 0.14, 0.2))
	clue("remedios", "Olhar o frasco de remédios", Vector3(-0.08, 0.66, -1.6), Vector3(0.1, 0.14, 0.1))
	clue("fotos", "Olhar as fotos", Vector3(-1.97, 1.6, -0.2), Vector3(0.1, 0.6, 1.1))
	clue("janela", "Olhar a janela", Vector3(-0.5, 1.45, -1.72), Vector3(1.1, 1.0, 0.2))
	clue("icone", "Olhar o ícone e a vela", Vector3(1.9, 1.65, -0.8), Vector3(0.2, 0.6, 0.4))
	clue("cartao", "Ler o cartão", Vector3(-1.3, 0.66, -0.95), Vector3(0.2, 0.06, 0.15))
	_notebook = clue("caderno", "Pegar o caderno de Lena", Vector3(-0.25, 0.57, -1.45), Vector3(0.16, 0.05, 0.22), false)
	_exit = clue("saida", "Sair do quarto", Vector3(1.2, 1.05, 1.76), Vector3(0.9, 2.1, 0.2), false)
	_intro()


func _intro() -> void:
	question = "Quem é Lena para Sergei?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(1.2).timeout
	Story.fade_to(0.0, 3.0)
	Story.card("T − 6 H", "O QUARTO DE LENA", 4.0)
	await get_tree().create_timer(4.0).timeout
	Story.say("Não há pressa aqui. É o único lugar onde não há.", 5.0)
	cinema.letterbox(false, 2.0)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	match id:
		"caderno":
			_decide()
			return
		"saida":
			Story.next_scene()
			return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"cama":
			Story.add_note("Cama feita, a manta dobrada com cuidado ao pé. Alguém arrumou o leito para quem não volta.")
			Story.say("Tudo dobrado, alinhado. Como se ela fosse voltar.", 5.0)
		"chinelos":
			Story.add_note("Chinelos lado a lado e uma bengala encostada. Lena andava devagar, mas sozinha.")
			Story.say("A bengala ainda tem o desgaste da mão dela.", 4.5)
		"gravador":
			Story.add_note("Gravador com uma pilha de fitas 'ЛЕНА'. A fita que toca é a voz de uma mulher lendo, a mesma que veio por trás da porta.",
				"Um gravador velho. Toca uma fita qualquer.")
			Story.say("É a voz que ouvi atrás da porta. Ela ainda lê para ninguém.", 6.0)
		"remedios":
			Story.add_note("Frasco de remédios quase vazio. Receita de 1992. Para o quê? A doença não é só do corpo.",
				"Remédios. Ela estava doente. Só isso.")
			Story.say("Um frasco sem rótulo. A receita é de março.", 4.0)
		"fotos":
			Story.add_note("Fotos de Lena jovem e da equipe do Kosmos. Sergei aparece em todas, atrás, olhando para ela.")
			Story.say("Ela sorri em todas. Ele olha para ela em todas.", 5.0)
		"janela":
			Story.add_note("Janela com gelo nos vidros. Lá fora o pátio sem luz. Aqui, o frio de quem ficou.")
			Story.say("O gelo desenha folhas. Ninguém limpou este vidro.", 4.5)
		"icone":
			Story.add_note("Ícone com a vela acesa há pouco. Alguém vem aqui acender, todos os dias.",
				"Uma vela. Sergei é supersticioso.")
			Story.say("A vela está acesa. Quem a acendeu?", 4.0)
		"cartao":
			Story.add_note("Cartão na letra dela: 'Serioja, lembre de mim.' Ela esqueceu o marido e tentou deixar um lembrete.",
				"Um bilhete de Lena para Sergei. Coisa de gente doente.", "quarto:cartao")
			Story.say("'Serioja, lembre de mim.' Ela escreveu isto ao esquecê-lo.", 6.0)
	_check()


func _check() -> void:
	if not _decided and _all_done() and not _notebook.is_in_group("clue"):
		_notebook.add_to_group("clue")
		Story.say("Na mesinha, o caderno de Lena. Há um nome escrito em todas as folhas.", 5.0)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _decide() -> void:
	if _decided:
		return
	_decided = true
	await get_tree().process_frame   # o E que abriu a escolha não conta como resposta
	var c := await Story.ask("O caderno de Lena: o nome 'Миша' escrito dezenas de vezes. O que você faz?",
		PackedStringArray(["Levar o caderno", "Deixá-lo onde está"]))
	Story.flags["caderno"] = c == 0
	Story.truth += 1 if c == 0 else -1
	_notebook.remove_from_group("clue")
	_notebook.queue_free()
	if c == 0:
		Sound.play("paper", "Sfx", -3.0)
		Story.add_note("Levei o caderno de Lena: 'Миша' escrito dezenas de vezes. Ela esqueceu Sergei, mas lembrava de Misha.",
			"Peguei um caderno. Rabiscos de uma mulher doente.")
		Story.say("Ela lembrava de Misha. Por quê, se esqueceu o marido?", 5.0)
	else:
		Story.add_note("Deixei o caderno de Lena onde estava. Há um nome nele que eu não deveria ter lido.",
			"Deixei o caderno. Nada a ver comigo.")
		Story.say("Fica melhor assim. Ou fica pior.", 4.0)
	await get_tree().create_timer(4.0).timeout
	_exit.add_to_group("clue")
	Story.say("Posso sair agora.", 3.0)
