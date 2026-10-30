extends Room
## Cena 9 — As Ruas do Parlamento (3/out/1993, T−10h, linha A, fria). Moscou em crise: barricadas, fogueiras em barris, multidão,
## faixas vermelhas, blindados ao longe e a Casa Branca fumegando. Irina espera sob um poste: "Hoje à noite acabamos."
## Revela a pressão de Karpov. Escolha: perguntar quem ele é (truth +1) ou obedecer (truth −1). Eixos: rua ao longo de z (norte = −z).
## Prédios: fachada de painéis (tools/russian.py: facade, facade_emit); o resto é geometria procedural.

const NEEDED := ["kiosk", "tv", "barricada", "fogueira", "multidao"]
const START := Vector3(0.0, 0.05, 30.0)

var _irina: Actor
var _irina_body: StaticBody3D
var _done := {}
var _talked := false
var _people: Array[Node3D] = []
var _fire_lights: Array[OmniLight3D] = []


func _ready() -> void:
	_sky_and_light()
	_ground()
	for z in [40.0, 8.0, -24.0]:                                         # prédios de painéis, lado oeste e leste
		_building(Vector3(-15.0, 0.0, z), Vector3(14.0, 20.0, 28.0))
		_building(Vector3(15.0, 0.0, z + 10.0), Vector3(14.0, 17.0, 26.0))
	_building(Vector3(-15.0, 0.0, -56.0), Vector3(14.0, 14.0, 24.0))
	_building(Vector3(15.0, 0.0, -56.0), Vector3(14.0, 22.0, 24.0))
	_white_house(Vector3(0.0, 0.0, -130.0))
	_banner(Vector3(0.0, 8.0, -18.0))
	for p in [Vector3(-7.0, 0, 20.0), Vector3(7.0, 0, -4.0), Vector3(-7.0, 0, -30.0)]:
		_streetlamp(p)
	_barricade(Vector3(0.0, 0.0, -52.0))
	for p in [Vector3(4.5, 0, -38.0), Vector3(-4.5, 0, -44.0), Vector3(2.0, 0, -49.0), Vector3(-6.0, 0, -36.0)]:
		_fire_barrel(p)
	_crowd(Vector3(-4.0, 0, -44.0), 11, 3.0)
	_crowd(Vector3(3.0, 0, -45.0), 9, 3.5)
	_crowd(Vector3(-1.0, 0, -30.0), 5, 4.0)
	_tank(Vector3(-4.0, 0, -100.0), 0.3)
	_tank(Vector3(8.0, 0, -112.0), -0.2)
	_kiosk(Vector3(6.5, 0, 12.0))
	_tv_window(Vector3(-7.97, 1.6, 6.0))                                 # encostada na fachada (x = -8)
	dust(Vector3(10.0, 4.0, 40.0), Vector3(0, 4.0, -20.0))               # cinzas e fuligem no ar

	Sound.scene("amb_room", "tinnitus", -50.0, "concrete", 0.9, 0.35)
	Sound._amb.volume_db = -34.0
	Sound._amb.set_meta("db", -34.0)
	Sound.emitter(self, "crowd_murmur", Vector3(0.0, 1.5, -46.0), -4.0, 12.0)
	Sound.emitter(self, "tanks", Vector3(-30.0, 2.0, -120.0), -4.0, 30.0)
	life([["gunshots_far", 10.0, 26.0, -8.0, Vector3(0, 3, -130), Vector3(25, 2, 10)],
		["siren_far", 30.0, 60.0, -13.0, Vector3(0, 2, -100), Vector3(30, 1, 5)]])
	setup_player(START, 0.0, 66.0, Vector3(0.95, 1.0, 1.06))
	player.interacted.connect(_on_interacted)

	_irina = Actor.new()
	_irina.position = Vector3(3.0, 0, -25.0)
	add_child(_irina)
	_irina.setup("irina", "face_irina", player)
	_irina.voice_tag = "high"
	_irina.voice_pitch = 0.92
	clue_on(_irina, "irina", "Falar com Irina", Vector3(0, 0.9, 0), Vector3(0.6, 1.8, 0.5), false)
	_irina_body = _irina.get_child(_irina.get_child_count() - 1)

	clue("kiosk", "Olhar o quiosque", Vector3(5.2, 1.3, 12.0), Vector3(0.4, 1.4, 2.0))
	clue("tv", "Olhar a vitrine de TV", Vector3(-7.4, 1.5, 6.0), Vector3(0.6, 1.3, 1.8))
	clue("barricada", "Olhar a barricada", Vector3(0.0, 1.0, -50.5), Vector3(8.0, 2.0, 0.8))
	clue("fogueira", "Olhar a fogueira", Vector3(4.5, 0.9, -38.0), Vector3(0.9, 1.0, 0.9))
	clue("multidao", "Escutar a multidão", Vector3(-3.0, 1.0, -37.0), Vector3(4.0, 2.0, 2.0))
	var wall := StaticBody3D.new()                                       # parede invisível: a barricada fecha a rua
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(20.0, 6.0, 1.0)
	cs.shape = bs
	wall.position = Vector3(0, 3.0, -52.0)
	wall.add_child(cs)
	add_child(wall)
	_intro()


func _process(delta: float) -> void:
	super._process(delta)
	for i in _people.size():                                              # a multidão balança de leve
		_people[i].rotation.z = sin(_t * 0.9 + i * 1.7) * 0.025
		_people[i].position.y = absf(sin(_t * 1.3 + i)) * 0.015
	for i in _fire_lights.size():
		_fire_lights[i].light_energy = 3.2 * (0.8 + 0.2 * sin(_t * 13.0 + i * 3.0) + 0.1 * sin(_t * 29.0 + i))


func _intro() -> void:
	question = "O que Irina quer de mim?"
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(1.0).timeout
	Story.fade_to(0.0, 3.0)
	Story.card("T − 10 H", "AS RUAS DO PARLAMENTO", 4.0)
	await get_tree().create_timer(3.5).timeout
	Story.say("Moscou, três de outubro. Cheira a pneu queimado e a medo.", 5.5)
	cinema.letterbox(false, 2.0)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if id == "irina":
		_talk_irina()
		return
	if _done.has(id):
		return
	_done[id] = true
	match id:
		"kiosk":
			Story.add_note("Quiosque: Marlboro, Snickers, Pepsi e vodka 'Royal'. Metade da rua vive de contrabando; a outra metade, de rancor.",
				"Um quiosque comum.")
			Story.say("Marlboro e Snickers num país onde ontem não havia pão.", 5.0)
		"tv":
			Story.add_note("Vitrine de TV: 'Vesti — Urgente'. A voz do apresentador treme. Ninguém na calçada olha.")
			Story.say("O apresentador fala de 'ordem'. A rua fala de sangue.", 5.0)
		"barricada":
			Story.add_note("Barricada de pneus, blocos de concreto, arame farpado e um Lada queimado. Bandeiras vermelhas nos postes.",
				"Uma barricada qualquer.")
			Story.say("Pneus, concreto e arame. Todos sabem o que vem depois.", 4.5)
		"fogueira":
			Story.add_note("Fogueira em barril. Homens se aquecem e se calam quando alguém de terno passa.")
			Story.say("Eles se calam quando passo. Parece que me conhecem.", 4.5)
		"multidao":
			Story.add_note("A multidão repete uma palavra de ordem em coro. Um homem me olha e desvia, como se eu fosse um informante.",
				"Gente gritando. Nada comigo.")
			Story.say("O coro para quando me aproximo. Por quê?", 4.0)
	_check()


func _check() -> void:
	if not _talked and _all_done():
		_irina_body.add_to_group("clue")
		Story.say("Irina me observa sob o poste. Acho que ela me espera.", 4.5)


func _all_done() -> bool:
	for id in NEEDED:
		if not _done.has(id):
			return false
	return true


func _talk_irina() -> void:
	if _talked:
		return
	if not _all_done():
		Story.say("IRINA: Olhe a rua primeiro, Aleksey. Depois a gente conversa.", 4.0)
		return
	_talked = true
	cinema.letterbox(true, 0.8)
	Sound.duck(true)
	_irina.speak(100.0)
	await Story.talk([
		"IRINA: Aleksey. Olhe em volta: hoje à noite isto acaba. Karpov quer o Lethe armado antes do amanhecer.",
		"ALEKSEY: Eu sou só um consultor, Irina.",
		"IRINA: Você é o que eu disse que você é. Karpov não gosta de homens que perguntam demais.",
		{"q": "Irina espera. O que você diz?",
		 "opts": ["Perguntar: 'Quem eu sou, Irina?'", "Obedecer: 'O que preciso fazer?'"], "truth": [1, -1], "trust": {"irina": [-1, 1]},
		 "reply": [["IRINA: Você é Aleksey Petrov. É o que basta saber."],
				   ["IRINA: Bom. Entre pelos arquivos. Faça o que Sergei pedir, sem perguntas."]]},
		"IRINA: Quando os tanques abrirem fogo, ninguém vai olhar para um técnico a mais.",
	])
	_irina.speak(0.05)
	Sound.duck(false)
	cinema.letterbox(false, 1.2)
	Story.add_note("Irina disse que hoje à noite acaba, e que Karpov quer o Lethe armado antes do amanhecer.",
		"Irina me deu uma ordem. Eu obedeço.")
	Story.say("Ela some entre a multidão. Eu fico com a ordem.", 4.0)
	await get_tree().create_timer(3.5).timeout
	Story.next_scene()


# ---- construção do cenário -----------------------------------------------------------------------------------------------------

func _mat(color: Color, glow := false, rough := 0.85) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	if glow:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = 0.9
	return m


## Caixa sólida (com colisão se `solid`).
func _solid(pos: Vector3, size: Vector3, m: Material, solid := true, rot_y := 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	b.material = m
	mi.mesh = b
	mi.position = pos
	mi.rotation.y = rot_y
	add_child(mi)
	if solid:
		var body := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var bs := BoxShape3D.new()
		bs.size = size
		cs.shape = bs
		body.add_child(cs)
		mi.add_child(body)
	return mi


func _sky_and_light() -> void:
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.32, 0.33, 0.38)
	sm.sky_horizon_color = Color(0.72, 0.58, 0.48)
	sm.ground_horizon_color = Color(0.40, 0.34, 0.32)
	sm.ground_bottom_color = Color(0.15, 0.13, 0.13)
	var sky := Sky.new()
	sky.sky_material = sm
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.9
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.55, 0.48, 0.43)
	env.fog_density = 0.006
	env.fog_sky_affect = 0.6
	env.glow_enabled = true
	env.glow_intensity = 0.5
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()                                  # sol fraco atrás das nuvens de fumaça
	sun.rotation_degrees = Vector3(-35.0, 20.0, 0.0)
	sun.light_color = Color(1.0, 0.82, 0.65)
	sun.light_energy = 0.9
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0
	add_child(sun)
	_env = env


func _ground() -> void:
	var m := _mat(Color(0.30, 0.29, 0.30))
	m.albedo_texture = load("res://art/tex/concrete.png")
	m.uv1_triplanar = true
	m.uv1_scale = Vector3.ONE * 0.2
	var g := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(500.0, 500.0)
	pm.material = m
	g.mesh = pm
	add_child(g)
	var body := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(500.0, 1.0, 500.0)
	cs.shape = bs
	cs.position.y = -0.5
	body.add_child(cs)
	add_child(body)


func _building(pos: Vector3, size: Vector3) -> void:
	var m := _mat(Color(1, 1, 1))
	m.albedo_texture = load("res://art/tex/facade.png")
	m.uv1_scale = Vector3(size.z / 12.0, size.y / 12.0, 1.0)
	m.emission_enabled = true
	m.emission_texture = load("res://art/tex/facade_emit.png")
	m.emission_energy_multiplier = 1.4
	_solid(pos + Vector3(0, size.y / 2.0, 0), size, m)


func _white_house(pos: Vector3) -> void:
	var m := _mat(Color(0.85, 0.85, 0.82))
	m.albedo_texture = load("res://art/tex/facade.png")
	m.uv1_scale = Vector3(7.0, 3.0, 1.0)
	_solid(pos + Vector3(0, 18.0, 0), Vector3(84.0, 36.0, 28.0), m, false)
	_solid(pos + Vector3(0, 44.0, 0), Vector3(20.0, 16.0, 20.0), m, false)           # torre central
	var smoke := GPUParticles3D.new()                                                   # fumaça sobe do prédio
	smoke.amount = 90
	smoke.lifetime = 14.0
	smoke.preprocess = 14.0
	smoke.visibility_aabb = AABB(Vector3(-40, 0, -40), Vector3(80, 120, 80))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(10.0, 1.0, 6.0)
	pm.direction = Vector3(0.2, 1.0, 0.0)
	pm.spread = 12.0
	pm.initial_velocity_min = 3.0
	pm.initial_velocity_max = 6.0
	pm.scale_min = 6.0
	pm.scale_max = 16.0
	smoke.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(1.0, 1.0)
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.albedo_color = Color(0.08, 0.08, 0.09, 0.45)
	q.material = sm
	smoke.draw_pass_1 = q
	smoke.position = pos + Vector3(0, 52.0, 0)
	add_child(smoke)


func _banner(pos: Vector3) -> void:
	var m := _mat(Color(1, 1, 1))
	m.albedo_texture = load("res://art/tex/banner_soviets.png")
	_solid(pos, Vector3(15.0, 2.5, 0.05), m, false)
	for sx in [-7.8, 7.8]:
		_solid(pos + Vector3(sx, -4.0, 0), Vector3(0.15, 8.0, 0.15), _mat(Color(0.3, 0.3, 0.32)), false)


func _streetlamp(at: Vector3) -> void:
	_solid(at + Vector3(0, 3.5, 0), Vector3(0.18, 7.0, 0.18), _mat(Color(0.22, 0.22, 0.24)))
	_solid(at + Vector3(0.7 * signf(-at.x), 7.0, 0), Vector3(1.6, 0.12, 0.12), _mat(Color(0.22, 0.22, 0.24)), false)
	_solid(at + Vector3(1.4 * signf(-at.x), 6.9, 0), Vector3(0.6, 0.14, 0.34), _mat(Color(0.9, 0.85, 0.7), true), false)


func _barricade(at: Vector3) -> void:
	for i in 14:                                                         # pneus empilhados
		var tire := MeshInstance3D.new()
		var cy := CylinderMesh.new()
		cy.top_radius = 0.45
		cy.bottom_radius = 0.45
		cy.height = 0.3
		cy.material = _mat(Color(0.05, 0.05, 0.06))
		tire.mesh = cy
		tire.position = at + Vector3(-6.0 + int(i / 3.0) * 1.0, 0.15 + (i % 3) * 0.3, 0.05 * (i % 2))   # pilhas de três
		add_child(tire)
	for bx in [-5.0, -2.0, 1.5, 4.5]:                                     # blocos de concreto
		_solid(at + Vector3(bx, 0.6, -0.5), Vector3(1.6, 1.2, 0.8), _mat(Color(0.5, 0.48, 0.45)), false, bx * 0.05)
	for bx in [-5.0, -2.0, 1.5, 4.5]:                                     # arame farpado em cima dos blocos
		for dz in [-0.2, 0.2]:
			_solid(at + Vector3(bx, 1.22, -0.5 + dz), Vector3(1.6, 0.04, 0.04), _mat(Color(0.2, 0.2, 0.2)), false, bx * 0.05)
	_car(at + Vector3(-4.0, 0, 2.5), 0.4, Color(0.10, 0.08, 0.08))       # Lada queimado
	for fx in [-6.5, 6.5]:                                                # bandeiras vermelhas
		_solid(at + Vector3(fx, 3.0, 0), Vector3(0.1, 6.0, 0.1), _mat(Color(0.5, 0.5, 0.5)), false)
		_solid(at + Vector3(fx + 0.9, 5.5, 0), Vector3(1.8, 1.1, 0.04), _mat(Color(0.7, 0.08, 0.08)), false)


func _fire_barrel(at: Vector3) -> void:
	var b := MeshInstance3D.new()
	var cy := CylinderMesh.new()
	cy.top_radius = 0.32
	cy.bottom_radius = 0.32
	cy.height = 0.9
	cy.material = _mat(Color(0.28, 0.12, 0.08))
	b.mesh = cy
	b.position = at + Vector3(0, 0.45, 0)
	add_child(b)
	_solid(at + Vector3(0, 1.1, 0), Vector3(0.45, 0.5, 0.45), _mat(Color(1.0, 0.55, 0.15), true), false)
	var l := lamp(at + Vector3(0, 1.6, 0), Color(1.0, 0.55, 0.2), 3.2, 9.0, false)
	_fire_lights.append(l)
	Sound.emitter(self, "fire_crackle", at + Vector3(0, 1.0, 0), -6.0, 3.0)


func _crowd(center: Vector3, n: int, radius: float) -> void:
	var r := RandomNumberGenerator.new()
	r.seed = int(center.x * 100 + center.z)
	for i in n:
		var p := Node3D.new()
		p.position = center + Vector3(r.randf_range(-radius, radius), 0, r.randf_range(-radius * 0.6, radius * 0.6))
		p.rotation.y = r.randf() * TAU
		var tone := r.randf_range(0.05, 0.2)
		var cm := CapsuleMesh.new()
		cm.radius = 0.24
		cm.height = 1.5
		cm.material = _mat(Color(tone, tone * 0.9, tone * 0.85))
		var body := MeshInstance3D.new()
		body.mesh = cm
		body.position.y = 0.75                                            # cápsula de 1,5 m com os pés no chão
		p.add_child(body)
		var sm := SphereMesh.new()
		sm.radius = 0.14
		sm.height = 0.28
		sm.material = _mat(Color(0.55, 0.42, 0.36))
		var head := MeshInstance3D.new()
		head.mesh = sm
		head.position.y = 1.62                                            # cabeça encostada no corpo
		p.add_child(head)
		if r.randf() < 0.4:                                               # ushanka
			var hat := MeshInstance3D.new()
			var hm := BoxMesh.new()
			hm.size = Vector3(0.32, 0.12, 0.32)
			hm.material = _mat(Color(0.12, 0.10, 0.08))
			hat.mesh = hm
			hat.position.y = 1.76
			p.add_child(hat)
		add_child(p)
		_people.append(p)


func _tank(at: Vector3, rot: float) -> void:
	var c := Node3D.new()
	c.position = at
	c.rotation.y = rot
	add_child(c)
	var olive := _mat(Color(0.18, 0.22, 0.14))
	for part in [[Vector3(0, 1.0, 0), Vector3(7.0, 1.4, 3.4)], [Vector3(-0.3, 2.0, 0), Vector3(3.2, 0.9, 2.6)], [Vector3(2.8, 2.1, 0), Vector3(4.2, 0.22, 0.22)]]:
		var mi := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = part[1]
		b.material = olive
		mi.mesh = b
		mi.position = part[0]
		c.add_child(mi)


func _car(at: Vector3, rot: float, color: Color) -> void:
	var c := Node3D.new()
	c.position = at
	c.rotation.y = rot
	add_child(c)
	for part in [[Vector3(0, 0.55, 0), Vector3(4.0, 0.7, 1.6)], [Vector3(-0.2, 1.1, 0), Vector3(2.0, 0.5, 1.5)]]:
		var mi := MeshInstance3D.new()
		var b := BoxMesh.new()
		b.size = part[1]
		b.material = _mat(color)
		mi.mesh = b
		mi.position = part[0]
		c.add_child(mi)


func _kiosk(at: Vector3) -> void:
	_solid(at + Vector3(0, 1.3, 0), Vector3(2.0, 2.6, 2.6), _mat(Color(0.18, 0.30, 0.45)))
	_solid(at + Vector3(-1.02, 1.5, 0), Vector3(0.05, 0.9, 1.6), _mat(Color(1.0, 0.85, 0.5), true), false)   # janela iluminada
	_solid(at + Vector3(-1.1, 1.0, 0), Vector3(0.4, 0.06, 1.8), _mat(Color(0.5, 0.35, 0.2)), false)           # balcão
	_solid(at + Vector3(0, 2.75, 0), Vector3(2.2, 0.2, 2.8), _mat(Color(0.7, 0.15, 0.12)), false)
	for k in 6:                                                           # maços e barras sobre o balcão
		_solid(at + Vector3(-1.15, 1.08, -0.7 + k * 0.28), Vector3(0.12, 0.1, 0.16), _mat(Color(0.6 + 0.05 * k, 0.2, 0.15)), false)


func _tv_window(at: Vector3) -> void:
	var m := _mat(Color(1, 1, 1))
	m.albedo_texture = load("res://art/tex/tv_news.png")
	m.emission_enabled = true
	m.emission_texture = load("res://art/tex/tv_news.png")
	m.emission_energy_multiplier = 1.6
	_solid(at, Vector3(0.06, 1.3, 1.7), m, false)
	lamp(at + Vector3(1.0, 0.0, 0.0), Color(0.7, 0.8, 1.0), 0.9, 4.0, false)
