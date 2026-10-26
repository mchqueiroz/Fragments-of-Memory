extends Room
## Cena 10 — A Clínica (set/1991, linha F, quente). Misha acorda três semanas depois do pulso, com o rosto enfaixado e sem memória.
## Irina entra e lhe dá um nome novo: Aleksey Petrov. "A identidade fica clara para o jogador." Se o jogador levou o caderno de Lena
## na cena 7, ele reaparece no criado-mudo (raccord). Escolha: aceitar o nome (truth −1) ou perguntar pelo de antes (truth +1).
## Técnica: o despertar (a imagem "esquece" e volta a se formar), luz de manhã de outono, gotejar do soro.

const NEEDED := ["prontuario", "espelho", "passaporte", "soro", "janela", "cama"]

var _irina: Actor
var _irina_body: StaticBody3D
var _done := {}
var _arrived := false
var _talked := false
var _forget := 1.0


func _ready() -> void:
	add_child(model("clinica"))
	environment(Color(0.13, 0.15, 0.14), Color(0.70, 0.80, 0.75), 0.015)
	lamp(Vector3(0.0, 2.5, 0.0), Color(0.85, 0.95, 0.90), 2.2, 6.0)                      # lâmpada fria de enfermaria
	lamp(Vector3(-0.7, 1.6, -1.5), Color(1.0, 0.85, 0.55), 1.6, 3.5, false)             # manhã de outono pela janela
	lamp(Vector3(-0.6, 1.5, -0.5), Color(0.95, 0.9, 0.6), 0.4, 1.4, false)              # brilho do frasco de soro
	dress(2.0, 1.8, 2.8, 81, 0.7)
	dust(Vector3(1.8, 1.0, 1.6), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "tinnitus", -50.0, "lino", 0.35, 0.18)
	Sound._amb.volume_db = -30.0
	Sound._amb.set_meta("db", -30.0)
	Sound.emitter(self, "drip", Vector3(-0.6, 1.0, -0.5), -12.0, 2.0)                    # o soro goteja
	Sound.emitter(self, "fluorescent_buzz", Vector3(0.0, 2.6, 0.0), -26.0, 3.0)
	life([["pipes_knock", 30.0, 70.0, -14.0, Vector3(2.0, 1.0, 0.0), Vector3(0, 0.5, 1.5)],
		["upstairs_steps", 25.0, 60.0, -15.0, Vector3(0, 2.8, 0), Vector3(1, 0, 1)]])
	setup_player(Vector3(-0.3, 0.05, 0.2), PI / 2.0, 62.0, Vector3(1.04, 1.0, 0.94))
	player.interacted.connect(_on_interacted)

	_irina = Actor.new()
	_irina.position = Vector3(0.9, 0, -0.6)
	_irina.visible = false
	add_child(_irina)
	_irina.setup("irina", "face_irina", player)
	_irina.voice_tag = "high"
	_irina.voice_pitch = 0.92
	clue_on(_irina, "irina", "Falar com Irina", Vector3(0, 0.9, 0), Vector3(0.6, 1.8, 0.5), false)
	_irina_body = _irina.get_child(_irina.get_child_count() - 1)

	clue("prontuario", "Ler o prontuário", Vector3(1.97, 1.5, 1.3), Vector3(0.1, 0.45, 0.35))
	clue("espelho", "Olhar no espelho", Vector3(1.97, 1.6, -1.3), Vector3(0.1, 0.7, 0.55))
	clue("passaporte", "Olhar o passaporte", Vector3(-0.4, 0.6, -1.5), Vector3(0.25, 0.08, 0.2))
	clue("soro", "Olhar o soro", Vector3(-0.6, 1.4, -0.5), Vector3(0.3, 0.9, 0.3))
	clue("janela", "Olhar pela janela", Vector3(-0.7, 1.5, -1.76), Vector3(1.2, 1.1, 0.2))
	clue("cama", "Olhar a cama", Vector3(-1.2, 0.62, -0.1), Vector3(0.8, 0.1, 1.6))
	if Story.flags.get("caderno", false):                                                # raccord: o caderno de Lena, "Миша"
		var nb := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(0.15, 0.02, 0.21)
		var mt := StandardMaterial3D.new()
		mt.albedo_texture = load("res://art/tex/notebook_misha.png")
		mt.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		bm.material = mt
		nb.mesh = bm
		nb.position = Vector3(-0.2, 0.575, -1.3)
		nb.rotation.y = 0.3
		add_child(nb)
		clue("caderno", "Olhar o caderno", Vector3(-0.2, 0.6, -1.3), Vector3(0.18, 0.08, 0.24))
	_intro()


func _process(delta: float) -> void:
	super._process(delta)
	post.set_shader_parameter("forget", _forget)
	Sound.attention(_forget * 0.6)


## O despertar: a visão se forma aos poucos (pixels voltam) enquanto o jogador ainda não pode se mexer.
func _intro() -> void:
	question = "Quem sou eu sem este rosto?"
	Story.busy = true
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(1.0).timeout
	Story.fade_to(0.0, 3.0)
	Story.card("SET / 1991", "A CLÍNICA", 4.0)
	var tw := create_tween()
	tw.tween_property(self, "_forget", 0.0, 7.0)
	await get_tree().create_timer(3.5).timeout
	Story.say("Luz. Um teto branco. O rosto repuxa sob as faixas.", 4.5)
	await get_tree().create_timer(5.0).timeout
	Story.say("Alguém me chamou por um nome. Não sei qual.", 4.0)
	await get_tree().create_timer(3.0).timeout
	Story.busy = false
	cinema.letterbox(false, 1.5)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "irina":
		_talk_irina()
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"prontuario":
			Story.add_note("Prontuário: 'ПЕТРОВ А. И., 1958 г.р.' Diagnóstico: trauma e amnésia. A letra é de outra pessoa; o nome foi escrito depois.",
				"Prontuário comum: um paciente chamado Petrov.")
			Story.say("Petrov. O nome parece de outro paciente, não meu.", 5.0)
		"espelho":
			Story.add_note("No espelho, o rosto todo enfaixado. Só os olhos aparecem, e eu não os reconheço.")
			Story.say("Só os olhos. E não são os olhos de ninguém que eu conheça.", 5.0)
		"passaporte":
			Story.add_note("Passaporte novo em nome de Aleksey Ivanovich Petrov, com uma foto que ainda não existe: meu rosto sem as faixas.",
				"Meu passaporte. Tudo em ordem.", "clinica:passaporte")
			Story.say("A foto é de um homem que eu nunca vi se barbear.", 4.5)
		"soro":
			Story.add_note("Soro de glicose e um sedativo. O frasco goteja num ritmo que não é o do meu coração.")
			Story.say("Gota a gota, o tempo passa sem eu estar nele.", 4.0)
		"janela":
			Story.add_note("Pela janela: árvores de bordo amarelas, folhas no chão. É setembro. Faltam semanas na minha cabeça.",
				"Árvores lá fora. Outono.")
			Story.say("Setembro. Faltam semanas que eu não vivi.", 4.5)
		"cama":
			Story.add_note("Cama de ferro de enfermaria. Cheira a desinfetante e a lençol lavado demais.")
			Story.say("Dormi nesta cama quanto tempo?", 3.5)
		"caderno":
			Story.add_note("No criado-mudo, o caderno de Lena: 'Миша' escrito dezenas de vezes. Alguém o trouxe até aqui.",
				"Um caderno com rabiscos. Não lembro de quem é.")
			Story.say("Misha. Ela escrevia esse nome o tempo todo. Por quê?", 5.0)
	_check()


func _check() -> void:
	if not _arrived and _all_done():
		_arrive()


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _arrive() -> void:
	_arrived = true
	Story.say("Passos no corredor. A porta de vidro fosco escurece.", 3.0)
	await get_tree().create_timer(1.5).timeout
	Sound.play("door_creak", "Sfx", -6.0)
	await get_tree().create_timer(0.8).timeout
	_irina.visible = true
	_irina_body.add_to_group("clue")
	Story.say("Uma mulher de casaco escuro, de pé junto à banqueta.", 4.0)


func _talk_irina() -> void:
	if _talked:
		return
	_talked = true
	cinema.letterbox(true, 0.8)
	Sound.duck(true)
	_irina.speak(100.0)
	await Story.talk([
		"IRINA: Você acordou. Três semanas. O médico disse que talvez não acordasse.",
		"VOCÊ: Onde estou? Quem é você?",
		"IRINA: Irina. Fui eu que o encontrei. Houve um acidente no instituto. Você não lembra?",
		"IRINA: Não importa. Tenho documentos novos. A partir de hoje, você é Aleksey Petrov. Técnico.",
		{"q": "Irina estende o passaporte. O que você diz?",
		 "opts": ["Aceitar: 'Aleksey Petrov.'", "Perguntar: 'E o meu nome de antes?'"], "truth": [-1, 1], "trust": {"irina": [1, -1]},
		 "reply": [["IRINA: Bom. Aleksey Petrov. Repita até acreditar."],
				   ["IRINA: Antes não existe. Existe o que eu lhe dou."]]},
		"IRINA: Escreva tudo o que aprender, Aleksey. Memória é uma coisa que a gente perde.",
	])
	_irina.speak(0.05)
	Sound.duck(false)
	cinema.letterbox(false, 1.2)
	Story.add_note("Irina me deu um nome: Aleksey Petrov. Mandou escrever tudo. É a minha primeira anotação.",
		"Irina me chamou de Aleksey Petrov. Concordei.")
	Story.say("O passaporte é meu. O nome também. Pelo menos, é o que me dizem.", 4.5)
	await get_tree().create_timer(4.0).timeout
	Story.next_scene()
