extends Room
## Cena 6 — O Golpe (19/ago/1991, linha F, quente). Porão do Kosmos na noite do golpe: balé em todos os canais, rádio do
## Comitê de Emergência, tanques na rua fazendo a taça vibrar. Irina chega (as luzes piscam), chama Misha de "Mishenka"
## e compra as plantas do Lethe com uma maleta. Misha vende em qualquer caso; a escolha muda a culpa (truth ±1).
## Técnica: contraste balé x blindados; câmera lenta e foco seletivo em Irina. Veja ato1-objetos-design.md, cena 6.

const NEEDED := ["tv", "radio", "plantas", "champanhe", "casaco"]

var _irina: Actor
var _irina_body: StaticBody3D
var _case_body: StaticBody3D
var _glass: MeshInstance3D
var _done := {}
var _arrived := false
var _sold := false
var _taken := false
var _rumble := 0.0


func _ready() -> void:
	add_child(model("porao"))
	environment(Color(0.07, 0.08, 0.11), Color(0.55, 0.60, 0.70), 0.03)
	lamp(Vector3(0, 2.3, 0), Color(1.0, 0.78, 0.45), 2.0, 6.5)                       # lâmpada nua
	lamp(Vector3(2.6, 1.0, 0.3), Color(0.65, 0.78, 1.0), 1.3, 3.2, false)            # luz da TV
	lamp(Vector3(0.0, 1.0, -1.2), Color(0.75, 0.85, 1.0), 0.9, 2.5, false)           # mesa de luz
	lamp(Vector3(-0.8, 2.0, 0.9), Color(1.0, 0.82, 0.62), 1.1, 2.6, false)             # contraluz fraco: Irina não vira silhueta
	dress(3.5, 2.5, 2.8, 61, 1.5)
	life([["upstairs_steps", 12.0, 30.0, -10.0, Vector3(1.0, 2.8, -2.0), Vector3(2, 0, 0.5)],
		["pipes_knock", 18.0, 45.0, -11.0, Vector3(0, 2.2, 0), Vector3(3, 0, 2)],
		["siren_far", 25.0, 60.0, -14.0, Vector3(0, 2.5, -3.0), Vector3(3, 0, 0)]])
	dust(Vector3(3.0, 1.2, 2.2), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "tinnitus", -50.0, "concrete", 0.7, 0.25)
	Sound.emitter(self, "swan_lake", Vector3(3.0, 0.9, 0.3), -9.0, 2.2)
	Sound.emitter(self, "radio_1993", Vector3(-3.2, 0.95, -0.8), -9.0, 2.0)
	Sound.emitter(self, "tanks", Vector3(1.5, 2.0, -2.6), -8.0, 6.0)
	setup_player(Vector3(0.0, 0.05, 2.0), 0.0, 62.0, Vector3(1.12, 0.98, 0.82))
	player.interacted.connect(_on_interacted)

	_irina = Actor.new()
	_irina.position = Vector3(-0.8, 0, 0.3)
	_irina.visible = false
	add_child(_irina)
	_irina.setup("irina", "face_irina", player)
	_irina.voice_tag = "high"
	_irina.voice_pitch = 0.92
	clue_on(_irina, "irina", "Falar com Irina", Vector3(0, 0.9, 0), Vector3(0.6, 1.8, 0.5), false)
	_irina_body = _irina.get_child(_irina.get_child_count() - 1)

	clue("tv", "Olhar a TV", Vector3(3.0, 0.85, 0.3), Vector3(0.5, 0.5, 0.6))
	clue("radio", "Ouvir o rádio", Vector3(-3.2, 0.95, -0.8), Vector3(0.3, 0.25, 0.4))
	clue("plantas", "Olhar a mesa de luz", Vector3(0.0, 0.8, -1.2), Vector3(0.6, 0.08, 0.45))
	clue("champanhe", "Olhar o champanhe", Vector3(-0.5, 0.95, -1.3), Vector3(0.14, 0.34, 0.14))
	clue("casaco", "Olhar o casaco", Vector3(-2.4, 1.3, -2.3), Vector3(0.5, 1.0, 0.2))
	_glass = MeshInstance3D.new()                                                    # taça que vibra com os tanques
	var cm := CylinderMesh.new()
	cm.top_radius = 0.028
	cm.bottom_radius = 0.022
	cm.height = 0.07
	_glass.mesh = cm
	_glass.position = Vector3(0.8, 0.80, -1.35)                                   # apoiada no tampo (0,765)
	add_child(_glass)

	var cs := BoxMesh.new()                                                          # a maleta de Irina (entra depois)
	cs.size = Vector3(0.55, 0.16, 0.38)
	var cmat := StandardMaterial3D.new()
	cmat.albedo_color = Color(0.32, 0.20, 0.12)
	cmat.roughness = 0.6
	cs.material = cmat
	_case_body = clue("maleta", "Pegar a maleta", Vector3(0.9, 0.1, -0.3), Vector3(0.55, 0.16, 0.38), false)
	var mesh := MeshInstance3D.new()
	mesh.mesh = cs
	_case_body.add_child(mesh)
	_case_body.visible = false
	_intro()


func _process(delta: float) -> void:
	super._process(delta)
	_rumble = lerpf(_rumble, 0.0025 if _arrived else 0.0012, 1.0 - exp(-0.8 * delta))
	if _glass:
		_glass.position.x = 0.8 + sin(_t * 61.0) * _rumble
		_glass.position.z = -1.35 + sin(_t * 53.0 + 1.0) * _rumble


func _intro() -> void:
	question = "O que eu vendi, e a quem?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("19 / AGO / 1991", "O GOLPE", 3.5)
	await get_tree().create_timer(2.5).timeout
	Story.say("Lá fora, tanques. Aqui embaixo, cisnes.", 5.0)
	cinema.letterbox(false, 1.5)
	start_clock({"seconds": 240, "warns": [[140, "Os tanques se aproximam. O chão estremece."], [60, "Passos na escada. Eles estão perto."]], "fail": "A porta do porão cedeu. Recomeço, mais depressa."})


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	match id:
		"irina":
			_talk_irina()
			return
		"maleta":
			_take_case(t)
			return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"tv":
			Story.add_note("TV velha: o balé 'O Lago dos Cisnes' em todos os canais. Quando só passam cisnes, algo grave aconteceu.")
			Story.say("Todos os canais com o mesmo balé. Assim começam os golpes.", 5.0)
		"radio":
			Story.add_note("Rádio: o 'Comitê de Emergência' assume o poder. Fala em ordem, calma, estado de emergência.")
			Story.say("Comitê de Emergência. Ordem e calma. Eles sempre pedem calma.", 5.0)
		"plantas":
			Story.add_note("Mesa de luz: as plantas do Lethe, desenho 4. O único jogo completo.",
				"Mesa de luz com plantas. Papéis.")
			Story.say("Todo o Lethe numa folha de papel vegetal.", 4.0)
		"champanhe":
			Story.add_note("Champanhe soviético, sem abrir. Eu ia comemorar o quê? O fim de alguma coisa?",
				"Uma garrafa de champanhe. Esperava comemorar.")
			Story.say("Eu comprei para festejar. Esqueci o motivo.", 4.0)
		"casaco":
			Story.add_note("Casaco escuro de mulher com um broche dourado da KGB. É de Irina.",
				"Casaco comum. Nada de importante.")
			Story.say("Um broche da KGB. Então ela já esteve aqui.", 4.5)
	_check()


func _check() -> void:
	if not _arrived and _all_done():
		_arrive()


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


## As luzes piscam e Irina está na sala: ninguém ouviu a porta.
func _arrive() -> void:
	_arrived = true
	Story.say("Ouvi a porta? Ou foi o chão tremendo?", 3.0)
	await get_tree().create_timer(1.5).timeout
	for l in _lamps:
		l.visible = false
	Sound.play("door_creak", "Sfx", -6.0)
	await get_tree().create_timer(0.7).timeout
	_irina.visible = true
	_irina_body.add_to_group("clue")
	for l in _lamps:
		l.visible = true
	Story.say("Irina está parada junto à mesa. As luzes voltaram, ela não se mexeu.", 4.5)


func _talk_irina() -> void:
	_clock = -1.0
	if _sold:
		return
	_sold = true
	cinema.letterbox(true, 0.8)
	cinema.focus(player.cam.global_position.distance_to(_irina.global_position + Vector3(0, 1.6, 0)))
	Sound.duck(true)
	_irina.speak(100.0)
	await Story.talk([
		"IRINA: Mishenka. Passam balé em todos os canais. Quando a televisão só mostra cisnes, alguém está morrendo.",
		"MISHA: Há tanques na rua, Irina.",
		"IRINA: Por isso vim. De quem são as plantas amanhã? De quem vencer. Eu sei quem vai vencer.",
		"IRINA: Uma maleta. Três anos de salário do instituto. Em troca, o Lethe.",
		{"q": "Irina estende a mão por cima da mesa de luz. O que você diz?",
		 "opts": ["Vender: 'Leve as plantas.'", "Recusar: 'Não são minhas para vender.'"], "truth": [-1, 1], "trust": {"irina": [1, -1]},
		 "reply": [["IRINA: Bom menino. Você nunca soube o preço das coisas."],
				   ["IRINA: Ninguém recusa duas vezes, Mishenka.", "MISHA: ...Leve."]]},
		"IRINA: Respira. Você vendeu, Mishenka. Todo mundo vende. A diferença é quem consegue dormir depois.",
	])
	_irina.speak(0.05)
	Sound.duck(false)
	cinema.unfocus()
	Engine.time_scale = 0.35                                                         # câmera lenta no momento da venda
	_case_body.visible = true
	_case_body.add_to_group("clue")
	Sound.play("pickup", "Sfx", -2.0)
	Story.add_note("Vendi as plantas do Lethe a Irina por uma maleta. Ela me chama de Mishenka: amor ou controle?",
		"Irina me pagou pelas plantas. Negócio justo.", "porao:venda")
	Story.say("A maleta ficou ao lado da mesa. Pesa mais que o salário de três anos.", 4.5)
	await get_tree().create_timer(1.8, true, false, true).timeout
	Engine.time_scale = 1.0
	cinema.letterbox(false, 1.2)


func _take_case(t: Node3D) -> void:
	if _taken:
		return
	_taken = true
	t.remove_from_group("clue")
	Sound.play("pickup", "Sfx", -2.0)
	Story.say("Eu fiquei com a maleta. E ela com o Lethe.", 4.0)
	await get_tree().create_timer(3.0).timeout
	Story.next_scene()
