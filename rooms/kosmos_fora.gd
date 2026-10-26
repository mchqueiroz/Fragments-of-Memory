extends Room
## Abertura do Ato II — O Kosmos por fora (3/out/1993, fim de tarde). Usa o modelo brutalista feito à mão pelo usuário
## (tools/kosmos_import.py -> art/models/kosmos.glb): um bloco de concreto de 240 x 100 m com colunata. O jogador anda
## até a entrada, com o rumor dos tanques ao longe; é o primeiro olhar de Aleksey, sem memória, para o lugar onde tudo aconteceu.
## Eixos: Blender (x, y, z) -> Godot (x, z, -y); o prédio fica em z = +17..+117, a colunata em z = +3.

const START := Vector3(7.4, 0.05, -60.0)

var _stage := 0


func _ready() -> void:
	var concrete := StandardMaterial3D.new()
	concrete.albedo_texture = load("res://art/tex/concrete.png")
	concrete.uv1_triplanar = true
	concrete.uv1_scale = Vector3.ONE * 0.12
	concrete.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	concrete.roughness = 0.85
	concrete.albedo_color = Color(1.25, 1.2, 1.15)   # concreto claro: lê melhor contra o céu escuro
	var kosmos := model("kosmos")
	add_child(kosmos)
	for mi in kosmos.find_children("*", "MeshInstance3D", true, false):
		(mi as MeshInstance3D).material_override = concrete
		(mi as MeshInstance3D).create_trimesh_collision()

	var ground := MeshInstance3D.new()                                                # praça de concreto
	var pm := PlaneMesh.new()
	pm.size = Vector2(700, 700)
	ground.mesh = pm
	ground.material_override = concrete
	add_child(ground)
	var gb := StaticBody3D.new()
	var gc := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(700, 1, 700)
	gc.shape = bs
	gc.position.y = -0.5
	gb.add_child(gc)
	add_child(gb)

	var sky_mat := ProceduralSkyMaterial.new()                                        # fim de tarde, fumaça ao fundo
	sky_mat.sky_top_color = Color(0.20, 0.22, 0.32)
	sky_mat.sky_horizon_color = Color(0.85, 0.52, 0.38)
	sky_mat.ground_horizon_color = Color(0.45, 0.32, 0.30)
	sky_mat.ground_bottom_color = Color(0.12, 0.10, 0.12)
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 1.1
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.78, 0.55, 0.45)
	env.fog_density = 0.0012
	env.fog_sky_affect = 0.4
	env.glow_enabled = true
	env.glow_intensity = 0.6
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()                                              # sol baixo e laranja: sombras longas
	sun.rotation_degrees = Vector3(-14.0, 160.0, 0.0)
	sun.light_color = Color(1.0, 0.65, 0.40)
	sun.light_energy = 2.4
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 220.0
	add_child(sun)

	Sound.scene("amb_room", "tinnitus", -50.0, "concrete", 0.9, 0.3)
	Sound._amb.volume_db = -30.0
	Sound._amb.set_meta("db", -30.0)
	Sound.emitter(self, "tanks", Vector3(-70.0, 3.0, -90.0), -5.0, 30.0)              # a cidade em crise, ao longe
	setup_player(START, PI, 70.0, Vector3(0.95, 1.0, 1.08))

	var sign_post := MeshInstance3D.new()                                             # a placa do instituto
	var sb := BoxMesh.new()
	sb.size = Vector3(1.4, 1.4, 0.08)
	var smat := StandardMaterial3D.new()
	smat.albedo_texture = load("res://art/tex/emblem.png")
	smat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	sb.material = smat
	sign_post.mesh = sb
	sign_post.position = Vector3(10.0, 1.3, -10.0)
	sign_post.rotation.y = PI
	add_child(sign_post)
	var leg := MeshInstance3D.new()
	var lb := BoxMesh.new()
	lb.size = Vector3(0.12, 1.3, 0.12)
	lb.material = concrete
	leg.mesh = lb
	leg.position = Vector3(10.0, 0.65, -10.0)
	add_child(leg)
	_flagpole(Vector3(16.0, 0, -12.0))                                                # bandeira tricolor russa, 1993
	for x in [-25.0, 40.0, 75.0]:
		_streetlamp(Vector3(x, 0, -22.0))
	_car(Vector3(32.0, 0, -30.0), 0.2, Color(0.45, 0.12, 0.10))                       # Ladas estacionados
	_car(Vector3(-18.0, 0, -35.0), -0.1, Color(0.35, 0.40, 0.42))
	_car(Vector3(55.0, 0, -45.0), 0.6, Color(0.10, 0.09, 0.09))
	clue("placa", "Ler a placa", Vector3(10.0, 1.3, -10.0), Vector3(1.4, 1.4, 0.3))
	player.interacted.connect(_on_interacted)
	_intro()


func _intro() -> void:
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(1.0).timeout
	Story.fade_to(0.0, 3.0)
	Story.card("ATO II · O DISFARCE", "KOSMOS · 3 OUT 1993", 4.5)
	await get_tree().create_timer(4.0).timeout
	Story.say("O Kosmos. Um bloco de concreto feito para esquecer quem passa por ele.", 6.0)
	cinema.letterbox(false, 2.0)


func _process(delta: float) -> void:
	super._process(delta)
	if _stage == 0 and player.position.z > -40.0:
		_stage = 1
		Story.say("Cada pilar parece um dia que passou. Eu nunca contei nenhum.", 5.0)
	elif _stage == 1 and player.position.z > -6.0:
		_stage = 2
		Story.say("Ao longe, tanques. Aqui dentro, ninguém sai.", 5.0)
	elif _stage == 2 and player.position.z > 12.0:
		_stage = 3
		Story.next_scene()


func _on_interacted(t: Node3D) -> void:
	if str(t.get_meta("id", "")) == "placa" and not Story.flags.has("placa"):
		Story.flags["placa"] = true
		Story.add_note("Placa do instituto: КОСМОС. Um bloco de concreto bruto de 240 metros. Aqui nasceu o Lethe.",
			"Placa de um instituto qualquer.")
		Story.say("КОСМОС. O brasão é de ouro e vermelho, o prédio é de cinza.", 5.0)


func _box(pos: Vector3, size: Vector3, color: Color, rot_y := 0.0, glow := false) -> MeshInstance3D:
	var m := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	var mt := StandardMaterial3D.new()
	mt.albedo_color = color
	mt.roughness = 0.8
	if glow:
		mt.emission_enabled = true
		mt.emission = color
		mt.emission_energy_multiplier = 2.0
	b.material = mt
	m.mesh = b
	m.position = pos
	m.rotation.y = rot_y
	add_child(m)
	return m


func _flagpole(at: Vector3) -> void:
	_box(at + Vector3(0, 4.0, 0), Vector3(0.12, 8.0, 0.12), Color(0.55, 0.55, 0.57))
	for i in 3:                                                                       # branco, azul, vermelho
		_box(at + Vector3(0.9, 7.4 - i * 0.35, 0), Vector3(1.8, 0.35, 0.04), [Color(0.9, 0.9, 0.9), Color(0.1, 0.2, 0.6), Color(0.7, 0.1, 0.1)][i])


func _streetlamp(at: Vector3) -> void:
	_box(at + Vector3(0, 3.0, 0), Vector3(0.14, 6.0, 0.14), Color(0.25, 0.25, 0.27))
	_box(at + Vector3(0.6, 6.0, 0), Vector3(1.3, 0.1, 0.1), Color(0.25, 0.25, 0.27))
	_box(at + Vector3(1.2, 5.92, 0), Vector3(0.5, 0.12, 0.3), Color(1.0, 0.85, 0.55), 0.0, true)


func _car(at: Vector3, rot: float, color: Color) -> void:
	var c := Node3D.new()
	c.position = at
	c.rotation.y = rot
	add_child(c)
	for part in [[Vector3(0, 0.55, 0), Vector3(4.0, 0.7, 1.6), color], [Vector3(-0.2, 1.1, 0), Vector3(2.0, 0.5, 1.5), color],
			[Vector3(-0.2, 1.1, 0), Vector3(2.02, 0.35, 1.52), Color(0.2, 0.25, 0.3)]]:
		var m := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = part[1]
		var mt := StandardMaterial3D.new()
		mt.albedo_color = part[2]
		mt.roughness = 0.7
		b.material = mt
		m.mesh = b
		m.position = part[0]
		c.add_child(m)
	for wx in [-1.2, 1.2]:
		for wz in [-0.85, 0.85]:
			var w := MeshInstance3D.new()
			var cy := CylinderMesh.new()
			cy.top_radius = 0.3
			cy.bottom_radius = 0.3
			cy.height = 0.2
			var wm := StandardMaterial3D.new()
			wm.albedo_color = Color(0.05, 0.05, 0.06)
			cy.material = wm
			w.mesh = cy
			w.rotation.x = PI / 2
			w.position = Vector3(wx, 0.3, wz)
			c.add_child(w)
