extends Room
## Cena 3 — Os Arquivos (T-30 min, linha A, fria). Aleksey, sem memória, segue o rastro que ele mesmo apagou:
## o log acusa Boris, mas a pasta "ВОЛКОВ М. И." foi retirada e a gaveta guarda o disquete do Lethe (ЛЕТА).
## Escolha de peso: acreditar no log (truth -1) ou duvidar dele (truth +1).
## Veja docs/superpowers/specs/2026-10-22-ato1-objetos-design.md, cena 3.

const CODE := "4-8-2-1"

var _done := {}
var _open := false
var _taken := false


func _ready() -> void:
	add_child(model("arquivos"))
	environment(Color(0.10, 0.13, 0.17), Color(0.55, 0.65, 0.75), 0.02)
	lamp(Vector3(-1.4, 2.7, 0.0), Color(0.8, 0.92, 1.0), 2.4, 6.5)
	lamp(Vector3(1.4, 2.7, 0.0), Color(0.8, 0.92, 1.0), 2.0, 6.5)
	lamp(Vector3(0.0, 2.7, -1.8), Color(0.7, 0.85, 1.0), 1.6, 5.5)
	dress(3.0, 3.0, 3.0, 31, 1.2)
	Sound.emitter(self, "fluorescent_buzz", Vector3(0, 2.8, 0), -22.0, 3.0)
	life([["pipes_knock", 15.0, 40.0, -12.0, Vector3(0, 2.0, -3.0), Vector3(2, 0.5, 0)],
		["upstairs_steps", 20.0, 50.0, -14.0, Vector3(0, 3.0, 0), Vector3(2, 0, 2)],
		["siren_far", 60.0, 110.0, -16.0, Vector3(0, 2.0, 6.0), Vector3(2, 1, 0)]])
	dust(Vector3(2.5, 1.2, 2.5), Vector3(0, 1.4, 0))
	Sound.scene("amb_room", "tinnitus", -34.0, "concrete", 0.6, 0.25)
	setup_player(Vector3(0.0, 0.05, 2.3), 0.0, 62.0, Vector3(0.92, 1.0, 1.1))
	player.interacted.connect(_on_interacted)

	clue("terminal", "Ler o terminal", Vector3(2.1, 0.97, -2.45), Vector3(0.5, 0.4, 0.4))
	clue("foto", "Olhar a foto rasgada", Vector3(1.35, 0.78, -2.55), Vector3(0.3, 0.12, 0.25))
	clue("cabo", "Olhar o cabo arrancado", Vector3(-0.3, 0.1, -1.9), Vector3(0.7, 0.15, 0.7))
	clue("armario", "Abrir o armário", Vector3(2.4, 1.0, -0.2), Vector3(0.12, 1.6, 0.5))
	clue("pasta", "Olhar o buraco na estante", Vector3(-2.5, 1.0, -1.04), Vector3(0.15, 0.5, 0.4))
	clue("gaveta", "Abrir a gaveta trancada", Vector3(2.4, 0.6, 1.3), Vector3(0.12, 0.9, 0.5))
	_intro()


func _intro() -> void:
	question = "Quem apagou o log?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("T − 30 MIN", "OS ARQUIVOS", 3.5)
	await get_tree().create_timer(2.5).timeout
	Story.say("Eu escrevi isto no meu próprio corpo: apague o rastro. Mas qual?", 5.0)
	cinema.letterbox(false, 1.5)
	start_clock({"seconds": 200, "warns": [[120, "Passos no corredor de cima. Alguém desce."], [50, "A porta do arquivo rangeu. Preciso sair."]], "fail": "Alguém entrou nos arquivos. Saio e recomeço, com mais calma."})


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "disquete":
		_clock = -1.0
		_take_floppy(t)
		return
	if id == "gaveta":
		await _gaveta(t)
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"terminal":
			Story.say("A nota colada diz 4-8-2-1. Elimine o rastro.", 4.0)
			Story.add_note("Terminal: nota colada '4-8-2-1. Elimine o rastro.' e o log: às 23h15, o usuário B.V. apagou os dados.", "", "arquivos:log")
			await get_tree().create_timer(2.5).timeout
			var c := await Story.ask("O log acusa Boris Volkov. Em quem você acredita?",
				PackedStringArray(["No log: foi Boris.", "No log, não. Alguém quer que eu pense isso."]))
			Story.truth += -1 if c == 0 else 1
			Story.add_note("Boris apagou os dados às 23h15, diz o log." if c == 0 else "O log acusa Boris. Fácil demais: duvidar.",
				"Boris apagou os dados. O log não mente.")
		"foto":
			Story.add_note("Foto rasgada: eu e Sergei brindando. Alguém cortou um terceiro rosto fora do quadro.",
				"Foto rasgada de Sergei e eu. Não importa.")
			Story.say("Havia um terceiro homem. Alguém o cortou fora.", 4.5)
		"cabo":
			Story.add_note("O cabo da câmera foi arrancado, com marcas fundas. Quem fez isso tinha pressa e força.")
			Story.say("Arrancado à mão. Não foi falha.", 4.0)
		"armario":
			Story.add_note("Armário de Boris: vodca e um caderno de técnico, folhas arrancadas. Ele bebia aqui, sozinho.",
				"Armário de Boris: só vodca. Ele é fraco.")
			Story.say("Uma garrafa meio vazia e um caderno com folhas arrancadas.", 4.5)
		"pasta":
			Story.add_note("Etiqueta 'ВОЛКОВ М. И. — изъято': retirada. Volkov... como Boris. Quem é M. I.?")
			Story.say("A etiqueta existe, a pasta não. Volkov. Como Boris.", 5.0)


func _gaveta(t: Node3D) -> void:
	if _open:
		return
	await get_tree().process_frame   # o E que abriu a gaveta não conta como escolha
	var c := await Story.ask("Gaveta trancada. Quatro dígitos.", PackedStringArray(["1-2-4-8", CODE, "8-4-1-2"]))
	if c != 1:
		Sound.play("pen", "Sfx", -6.0)
		Story.say("Não abre.", 2.5)
		return
	_open = true
	Sound.play("pickup", "Sfx", -2.0)
	t.remove_from_group("clue")
	Story.add_note("Gaveta aberta: a pasta 'ЛЕТА' e um disquete rotulado à mão: 'копия 1'.")
	Story.say("A pasta ЛЕТА. E um disquete com a minha letra.", 4.5)
	var f := clue("disquete", "Pegar o disquete", Vector3(2.4, 0.7, 1.3), Vector3(0.15, 0.2, 0.3))
	var m := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.09, 0.012, 0.09)
	m.mesh = bm
	f.add_child(m)


func _take_floppy(t: Node3D) -> void:
	if _taken:
		return
	_taken = true
	t.remove_from_group("clue")
	t.queue_free()
	Story.add_note("Peguei o disquete 'ЛЕТА копия 1'. Preciso de um lugar para ler.", "Peguei um disquete. Provavelmente nada.")
	Sound.play("pickup", "Sfx", -2.0)
	Story.say("Pesa pouco. Mas é tudo o que sobrou.", 3.5)
	await get_tree().create_timer(3.0).timeout
	Story.next_scene()
