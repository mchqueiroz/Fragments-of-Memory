extends Room
## Cena 8 — O Pulso (21/ago/1991, linha F, quente). Fim do Ato I. O golpe fracassou; homens da KGB esperam fora (sombras sob a
## porta). Sergei, com a mão no botão, vai apagar Misha: nada impede o pulso, o jogador vive que o passado não muda.
## Técnica: o pulso vira branco-papel; objetos somem um a um, o som cai a um zumbido (peak-end). Veja ato1-objetos-design.md, cena 8.
## Reaproveita o modelo do laboratório antigo (prototipo.glb) em luz de amanhecer.

const NEEDED := ["proto", "cadeira", "maleta", "peao", "porta"]

var _sergei: Actor
var _props: Array[Node3D] = []      # somem um a um quando o pulso vem
var _shadows: Array[MeshInstance3D] = []
var _done := {}
var _talked := false
var _forget := 0.0
var _white: ColorRect
var _end_label: Label
var _room: Node3D


func _ready() -> void:
	_room = model("prototipo")
	add_child(_room)
	environment(Color(0.16, 0.14, 0.15), Color(0.95, 0.75, 0.60), 0.03)
	backdrop_kosmos(130.0, Color(0.38, 0.34, 0.46), Color(1.0, 0.70, 0.52))
	lamp(Vector3(0.0, 1.8, -2.0), Color(1.0, 0.72, 0.55), 3.0, 6.5, false)           # amanhecer pela janela
	lamp(Vector3(0.0, 2.7, 0.0), Color(1.0, 0.92, 0.80), 0.8, 6.0)
	lamp(Vector3(0.0, 0.15, 2.6), Color(0.75, 0.82, 1.0), 0.7, 2.0, false)           # luz fria fora da porta
	dress(3.0, 2.5, 3.0, 42, 1.3)
	life([["tram_pass", 40.0, 80.0, -13.0, Vector3(0, 1.5, -8.0), Vector3(2, 1, 1)],
		["siren_far", 12.0, 30.0, -15.0, Vector3(0, 2.0, -9.0), Vector3(3, 1, 1)],
		["pipes_knock", 25.0, 60.0, -13.0, Vector3(3.0, 1.0, 0), Vector3(0, 0.5, 2)]])
	dust(Vector3(2.5, 1.2, 2.0), Vector3(0, 1.3, 0))
	Sound.scene("amb_room", "tinnitus", -50.0, "parquet", 0.5, 0.18)
	setup_player(Vector3(1.5, 0.05, 1.7), 0.0, 62.0, Vector3(1.12, 0.98, 0.82))
	player.interacted.connect(_on_interacted)

	_sergei = Actor.new()
	_sergei.position = Vector3(0.9, 0, -0.9)
	add_child(_sergei)
	_sergei.setup("sergei", "face_sergei", player)
	clue_on(_sergei, "sergei", "Falar com Sergei", Vector3(0, 0.9, 0), Vector3(0.7, 1.8, 0.5), false)

	# cadeira de eletrodos ligada ao protótipo por um cabo
	var chair := Node3D.new()
	chair.position = Vector3(-1.2, 0, 0.2)
	chair.rotation.y = -0.4
	add_child(chair)
	_part(chair, Vector3(0, 0.45, 0), Vector3(0.5, 0.05, 0.5), Color(0.22, 0.16, 0.12))
	_part(chair, Vector3(0, 0.85, -0.23), Vector3(0.5, 0.8, 0.05), Color(0.22, 0.16, 0.12))
	for dx in [-0.22, 0.22]:
		for dz in [-0.2, 0.2]:
			_part(chair, Vector3(dx, 0.22, dz), Vector3(0.04, 0.44, 0.04), Color(0.15, 0.11, 0.08))
	for dx in [-0.12, 0.0, 0.12]:                                                     # eletrodos na cabeceira
		_part(chair, Vector3(dx, 1.12, -0.19), Vector3(0.05, 0.05, 0.05), Color(0.7, 0.7, 0.72))
	_props.append(chair)
	var cable := _part(self, Vector3(-0.55, 0.5, -0.6), Vector3(0.02, 0.02, 1.7), Color(0.04, 0.04, 0.05))
	cable.rotation.y = 0.65
	_props.append(cable)
	clue("cadeira", "Olhar a cadeira de eletrodos", Vector3(-1.2, 0.85, 0.2), Vector3(0.6, 1.3, 0.6))

	# a maleta aberta: a prova
	var bag := Node3D.new()
	bag.position = Vector3(-0.6, 0.0, 1.0)
	add_child(bag)
	_part(bag, Vector3(0, 0.08, 0), Vector3(0.55, 0.16, 0.38), Color(0.32, 0.20, 0.12))
	_part(bag, Vector3(0, 0.15, 0), Vector3(0.5, 0.04, 0.34), Color(0.30, 0.45, 0.28))      # maços de dinheiro
	var lid := _part(bag, Vector3(0, 0.34, -0.2), Vector3(0.55, 0.38, 0.03), Color(0.30, 0.18, 0.10))
	lid.rotation.x = -0.25
	_props.append(bag)
	clue("maleta", "Olhar a maleta aberta", Vector3(-0.6, 0.15, 1.0), Vector3(0.6, 0.3, 0.45))

	# o peão branco devolvido por Misha, ao lado do protótipo
	var pawn := Node3D.new()
	pawn.position = Vector3(0.35, 0.79, -1.3)
	add_child(pawn)
	_part(pawn, Vector3(0, 0.015, 0), Vector3(0.05, 0.03, 0.05), Color(0.9, 0.88, 0.8))
	_part(pawn, Vector3(0, 0.055, 0), Vector3(0.03, 0.05, 0.03), Color(0.9, 0.88, 0.8))
	_part(pawn, Vector3(0, 0.1, 0), Vector3(0.04, 0.04, 0.04), Color(0.9, 0.88, 0.8))
	_props.append(pawn)
	clue("peao", "Olhar o peão branco", Vector3(0.35, 0.85, -1.3), Vector3(0.12, 0.14, 0.12))
	clue("proto", "Olhar o protótipo ligado", Vector3(0.0, 0.97, -1.45), Vector3(0.5, 0.4, 0.2))

	# a porta, com a luz fria por baixo e sombras de homens do lado de fora
	var door := _part(self, Vector3(0, 1.05, 2.48), Vector3(0.9, 2.1, 0.04), Color(0.2, 0.14, 0.1))
	_props.append(door)
	_part(self, Vector3(0, 0.01, 2.46), Vector3(0.88, 0.012, 0.03), Color(0.85, 0.9, 1.0), true)
	for i in 3:
		var sh := _part(self, Vector3(-0.3 + i * 0.3, 0.012, 2.455), Vector3(0.11, 0.014, 0.034), Color.BLACK)
		_shadows.append(sh)
	clue("porta", "Escutar a porta", Vector3(0.0, 1.05, 2.45), Vector3(0.95, 2.1, 0.2))

	_white = ColorRect.new()                                                          # o branco-papel do pulso
	_white.color = Color(0.96, 0.94, 0.90)
	_white.set_anchors_preset(Control.PRESET_FULL_RECT)
	_white.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_white.modulate.a = 0.0
	_end_label = Label.new()
	_end_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_end_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_end_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_end_label.add_theme_font_size_override("font_size", 14)
	_end_label.add_theme_color_override("font_color", Color(0.12, 0.10, 0.10))
	_white.add_child(_end_label)
	var cl := CanvasLayer.new()
	cl.layer = 14
	cl.add_child(_white)
	add_child(cl)
	_intro()


## Caixa colorida sem textura (adereço procedural); `glow` a deixa luminosa.
func _part(parent: Node3D, pos: Vector3, size: Vector3, color: Color, glow := false) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	var mt := StandardMaterial3D.new()
	mt.albedo_color = color
	mt.roughness = 0.8
	if glow:
		mt.emission_enabled = true
		mt.emission = color
		mt.emission_energy_multiplier = 2.5
	b.material = mt
	m.mesh = b
	m.position = pos
	parent.add_child(m)
	return m


func _process(delta: float) -> void:
	super._process(delta)
	for i in _shadows.size():                       # sombras de homens que passam sob a porta
		_shadows[i].position.x = -0.35 + fmod(_t * (0.05 + 0.02 * i) + i * 0.3, 0.7)
		_shadows[i].visible = int(_t * 0.7 + i) % 3 != 0
	post.set_shader_parameter("forget", _forget)
	Sound.attention(_forget)


func _intro() -> void:
	question = "Quem vai apertar o botão?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.8).timeout
	Story.fade_to(0.0, 2.0)
	Story.card("21 / AGO / 1991", "O PULSO", 3.5)
	await get_tree().create_timer(2.5).timeout
	Story.say("O golpe fracassou. Do outro lado da porta, eles esperam.", 5.0)
	cinema.letterbox(false, 1.5)
	start_clock({"seconds": 240, "warns": [[140, "Alguém tenta a maçaneta, do outro lado."], [60, "As sombras sob a porta se juntam. Pouco tempo."]], "fail": "A porta cedeu. Recomeço, mais depressa."})


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "sergei":
		_talk_sergei()
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"proto":
			Story.add_note("O protótipo do Lethe, ligado. A luz de ciclo pisca no ritmo de um coração que não é meu.", "", "pulso:proto")
			Story.say("Ele já está ligado. Quem o ligou?", 4.0)
		"cadeira":
			Story.add_note("Cadeira com eletrodos na cabeceira, cabo preto até o protótipo. É para uma pessoa só.")
			Story.say("Uma cadeira para quem vai esquecer. Eu sei quem.", 4.5)
		"maleta":
			Story.add_note("A maleta aberta com o dinheiro de Irina. A prova de que eu vendi.",
				"Uma maleta com dinheiro. Pagamento justo.")
			Story.say("A maleta está aberta. Não adianta fechar.", 4.0)
		"peao":
			Story.add_note("O peão branco, devolvido por mim a Sergei, ao lado do protótipo. 'Não esquece de onde você veio.'",
				"Um peão de xadrez. Esqueci por que estou com ele.")
			Story.say("O peão do pai. Eu o devolvi. Para quê?", 4.0)
		"porta":
			Story.add_note("Sombras de homens sob a porta. A KGB espera. A porta está trancada por fora.")
			Story.say("Passos. Pelo menos três homens. Ninguém bate.", 4.5)
	_check()


func _check() -> void:
	if not _talked and _all_done():
		_sergei.get_child(_sergei.get_child_count() - 1).add_to_group("clue")
		Story.say("Sergei está com a mão no botão. Acho que preciso falar com ele.", 4.5)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _talk_sergei() -> void:
	_clock = -1.0
	if _talked:
		return
	_talked = true
	cinema.letterbox(true, 0.8)
	Sound.duck(true)
	_sergei.speak(100.0)
	await Story.talk([
		"SERGEI: Eles estão aí fora, Misha. Esperam você. Você vendeu o que não era seu.",
		"MISHA: Eu devolvi o peão, Sergei. Sou o mesmo.",
		"SERGEI: O Lethe só faz uma coisa bem: tira o homem do que ele fez. Eu quero te salvar. Do que eu fiz também.",
		{"q": "A mão de Sergei está sobre o botão. O que você faz?",
		 "opts": ["Pedir que ele pare: 'Não, Sergei, por favor.'", "Aceitar calado.", "Tentar fugir pela porta."], "truth": [1, 0, -1], "trust": {"sergei": [1, 0, -1]},
		 "reply": [["SERGEI: Peço perdão, meu filho. É tarde."],
				   ["SERGEI: Obrigado, Misha. Pela última vez."],
				   ["SERGEI: A porta está trancada por fora. Eu sei. Fui eu."]]},
		"SERGEI: Feche os olhos. Quando abrir, você não será mais ninguém.",
	])
	_sergei.speak(0.05)
	cinema.letterbox(false, 0.4)
	Sound.duck(false)
	await _pulse()


## O pulso: a imagem esquece (pixels morrem), os objetos somem um a um, o som cai a um zumbido, tudo vira branco-papel.
func _pulse() -> void:
	Sound.play("transition", "Sfx", 0.0)
	var tw := create_tween()
	tw.tween_property(self, "_forget", 1.0, 5.0)
	tw.parallel().tween_property(cinema, "fov_target", 48.0, 5.0)
	_props.append(_sergei)
	for p in _props:
		await get_tree().create_timer(0.7).timeout
		p.visible = false
	await get_tree().create_timer(0.8).timeout
	create_tween().tween_property(_white, "modulate:a", 1.0, 2.5)
	await get_tree().create_timer(3.0).timeout
	_end_label.text = "FIM DO ATO I\n\nMisha esqueceu tudo.\nQuem é Aleksey?"
	await get_tree().create_timer(6.5).timeout
	Story.next_scene()
