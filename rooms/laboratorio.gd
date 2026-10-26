extends Node3D
## Cena 1 — O Laboratório (T+0, linha A, fria). Aleksey acorda com a pistola na mão ao lado do corpo de Sergei.
## Eixos: Blender (x, y, z) -> Godot (x, z, -y). Veja docs/superpowers/specs/2026-10-22-ato1-objetos-design.md.
## Técnicas: zumbido no ouvido que baixa conforme o jogador investiga (a mente "volta"); mão que treme;
## escolha de peso no corpo; o peão (raccord) só aparece depois das pistas.

const NEEDED := ["corpo", "console", "painel", "diario"]

var _player: PlayerCtl
var _cinema: Cinema
var _post: ShaderMaterial
var _t := 0.0
var _stress := 0.30          # 0 = lúcido, 0.3 = zumbido alto e som abafado
var _done := {}
var _lamps: Array[Light3D] = []
var _alarms: Array[Light3D] = []
var _pawn: StaticBody3D
var _beat := 1.2


func _ready() -> void:
	add_child(_model("laboratorio"))
	_environment()
	_lights()
	Dressing.dress(self, 5.0, 6.0, 5.0, 93, 1.4)
	Sound.emitter(self, "fluorescent_buzz", Vector3(0, 4.8, 0), -20.0, 4.0)
	Dressing.life(self, [["pipes_knock", 18.0, 45.0, -10.0, Vector3(-4.5, 3.0, -2.0), Vector3(0, 1, 3)],
		["siren_far", 45.0, 90.0, -14.0, Vector3(0, 3.0, 8.0), Vector3(3, 1, 0)],
		["upstairs_steps", 30.0, 70.0, -13.0, Vector3(0, 5.0, 0), Vector3(3, 0, 4)]])
	_dust()
	Sound.scene("amb_room", "theme_sergei", -26.0, "concrete", 0.85, 0.3)
	Sound.music_for(scene_file_path)

	_player = PlayerCtl.new()
	_player.position = Vector3(0, 0.05, 4.8)
	add_child(_player)
	_player.held = "pistol"
	_player.tremble = 0.9
	_player.dropped.connect(_on_dropped)
	_player.interacted.connect(_on_interacted)
	_player.target_changed.connect(func(t: Node3D, d: float):
		if t:
			_cinema.focus(d)
		else:
			_cinema.unfocus())

	_body()
	_clue("corpo", "Olhar o corpo", Vector3(-0.9, 0.2, -0.05), Vector3(0.8, 0.4, 2.0))
	_clue("console", "Ler o console do pulso", Vector3(-2.0, 1.05, -4.7), Vector3(3.2, 0.9, 0.8))
	_clue("painel", "Ler o painel do míssil", Vector3(1.2, 1.2, -2.1), Vector3(1.0, 0.7, 0.3))
	_pawn = _clue("peao", "Pegar o peão", Vector3(-1.5, 0.08, -1.15), Vector3(0.25, 0.3, 0.25), false)
	var pm := MeshInstance3D.new() # o peão: um cilindro claro e uma esfera, de madeira
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.03
	cyl.bottom_radius = 0.05
	cyl.height = 0.13
	pm.mesh = cyl
	var wood := StandardMaterial3D.new()
	wood.albedo_color = Color(0.85, 0.80, 0.65)
	wood.emission_enabled = true
	wood.emission = Color(0.85, 0.78, 0.55)
	wood.emission_energy_multiplier = 0.6
	pm.material_override = wood
	_pawn.add_child(pm)
	pm.position.y = -0.03

	_cinema = Cinema.new()
	add_child(_cinema)
	_cinema.setup(_player.cam)
	_cinema.fov_target = 78.0

	var post := CanvasLayer.new()
	post.layer = 10
	var r := ColorRect.new()
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_post = ShaderMaterial.new()
	_post.shader = load("res://shaders/retro.gdshader")
	_post.set_shader_parameter("tint", Vector3(0.86, 0.96, 1.12)) # linha A: fria
	_post.set_shader_parameter("forget", 0.0)
	r.material = _post
	post.add_child(r)
	add_child(post)

	Story.reset()
	Story.add_note("Caderno: letra minha que não reconheço. 'Não confie em Boris.'", "Caderno: um aviso meu. Boris é o culpado.", "laboratorio:caderno")
	_intro()


func _intro() -> void:
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(1.2).timeout
	Story.fade_to(0.0, 2.5)
	Story.card("T + 0", "O LABORATÓRIO", 4.0)
	await get_tree().create_timer(1.5).timeout
	Story.say("Quem sou eu? Por que minha mão cheira a pólvora?", 5.5)
	await get_tree().create_timer(5.5).timeout
	Story.say("[Q] largar a arma     [Tab] ler o caderno     [E] examinar", 6.0)
	_cinema.letterbox(false, 1.5)


func _on_dropped(item: String) -> void:
	_player.tremble = 0.4
	Story.flags["largou_arma"] = true
	Sound.play("chess_click", "Sfx", -2.0, 0.6)
	var fwd := -_player.global_basis.z
	fwd.y = 0.0
	var gun := _model("vm_pistol")
	gun.position = _player.global_position + fwd.normalized() * 0.7
	gun.position.y = 0.04
	gun.rotation = Vector3(deg_to_rad(90.0), _player.rotation.y + 0.6, 0.0)
	add_child(gun)
	_clue_on(gun, "pistola", "Examinar a pistola", Vector3.ZERO, Vector3(0.18, 0.1, 0.2))


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if _done.has(id) and id != "peao":
		return
	match id:
		"corpo":
			_done[id] = true
			Story.add_note("No jaleco, um crachá: «МОРОЗОВ С. И.». Um único tiro no peito. Os olhos abertos, calmos, sem medo.",
				"Morozov, caído. Um único tiro, limpo. Ele sabia o que merecia.")
			await Story.talk([
				"No jaleco, um crachá: MOROZOV. Um único tiro, bem no peito. E os olhos... abertos, calmos. Sem medo.",
				"Ele não parece assustado. Parece com pena de mim.",
				{"q": "A pólvora na minha mão. Um homem morto aos meus pés. O que eu digo a mim mesmo?",
				 "opts": ["Não pode ter sido eu. Eu me lembraria.", "Fui eu. A pólvora na mão não mente."], "truth": [-1, 1],
				 "reply": [["Eu não faria isso. Alguém quer que eu pense que fui eu."], ["Fui eu. Não sei por quê, mas fui eu."]]}])
		"console":
			_done[id] = true
			Story.add_note("Console «ЛЕТА»: no visor, OPERADOR — e um traço. CICLO: RESFRIAMENTO. Não sei o que isso faz.",
				"Console do Lethe: sabotado por Boris.")
			Story.say("O visor diz OPERADOR, e um traço. Como se ninguém tivesse apertado nada.", 5.0)
		"painel":
			_done[id] = true
			Story.add_note("Painel do míssil: 'ЛЕТА — ДАННЫЕ: СБОЙ'. Dados corrompidos, de dentro.",
				"Painel do míssil: sabotagem. Foi Boris.")
			Story.say("Dados corrompidos. Defeito, ou alguém fez isto. Por que eu estou aqui?", 5.0)
		"pistola":
			_done[id] = true
			Story.add_note("Pistola. Cano morno. Uma bala a menos no tambor.")
			Story.say("Ainda quente. Não há mais ninguém aqui.", 4.0)
		"peao":
			_end()
	_after_clue()


func _after_clue() -> void:
	_stress = maxf(0.0, _stress - 0.06)
	_player.tremble = maxf(0.15, _player.tremble - 0.08)
	if _done.has("corpo") and _done.has("console") and _done.has("painel") and _done.has("diario") and not _pawn.is_in_group("clue"):
		_pawn.add_to_group("clue")
		Story.say("Há uma coisa pequena no chão, perto dele...", 4.0)


func _end() -> void:
	_player.set_physics_process(false)
	Story.add_note("Peão branco de madeira. Gasto de tanto uso.")
	Story.say("Eu conheço este peão. De onde?", 3.5)
	Sound.play("pickup", "Sfx", -2.0)
	await get_tree().create_timer(2.5).timeout
	Story.next_scene()


func _process(delta: float) -> void:
	_t += delta
	if _player.reading and not _done.has("diario"):
		_done["diario"] = true
		_after_clue()
	_stress = lerpf(_stress, _stress, 0.0)
	Sound.attention(_stress)
	for i in _lamps.size():
		var l := _lamps[i]
		var base: float = l.get_meta("e")
		var dead := 0.1 if fmod(_t * 0.9 + i * 2.3, 6.3) < 0.18 else 1.0 # fluorescente falhando
		l.light_energy = base * (0.9 + 0.1 * sin(_t * 19.0 + i)) * dead
	for l in _alarms:
		l.light_energy = float(l.get_meta("e")) * (0.5 + 0.5 * sin(_t * 3.2))
	_beat -= delta
	if _beat <= 0.0: # batimento cardíaco, mais baixo conforme a mente clareia
		_beat = 1.2
		Sound.play("heartbeat", "Sfx", lerpf(-26.0, -10.0, clampf(_stress / 0.3, 0.0, 1.0)))


## Cria um objeto examinável (corpo estático no grupo "clue"); `enabled=false` o deixa inativo até ser liberado.
func _clue(id: String, prompt: String, pos: Vector3, size: Vector3, enabled := true) -> StaticBody3D:
	var b := StaticBody3D.new()
	b.position = pos
	add_child(b)
	_clue_on(b, id, prompt, Vector3.ZERO, size, enabled)
	return b


func _clue_on(node: Node3D, id: String, prompt: String, offset: Vector3, size: Vector3, enabled := true) -> void:
	var body: StaticBody3D = node if node is StaticBody3D else StaticBody3D.new()
	if body != node:
		node.add_child(body)
	body.set_meta("id", id)
	body.set_meta("prompt", prompt)
	if enabled:
		body.add_to_group("clue")
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = size
	cs.shape = bs
	cs.position = offset
	body.add_child(cs)


## Sergei, deitado de costas (modelo animado parado), olhos abertos.
func _body() -> void:
	var m := _model("sergei")
	m.position = Vector3(-0.9, 0.13, 0.95)
	m.rotation = Vector3(-PI / 2.0, 0.35, 0.0)
	var ap := m.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if ap:
		ap.stop()
	add_child(m)


func _vec3(a: float, b: float, c: float) -> Vector3:
	return Vector3(a, b, c)


## Carrega um .glb e força textura "nearest".
func _model(name: String) -> Node3D:
	var n: Node3D = (load("res://art/models/%s.glb" % name) as PackedScene).instantiate()
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		for s in (mi as MeshInstance3D).mesh.get_surface_count():
			var m := (mi as MeshInstance3D).get_active_material(s)
			if m is StandardMaterial3D:
				m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return n


func _environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.BLACK
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.10, 0.12, 0.16)
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	env.ssao_radius = 1.0
	env.ssao_intensity = 2.5
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.02
	env.volumetric_fog_albedo = Color(0.7, 0.75, 0.85)
	env.glow_enabled = true
	env.glow_intensity = 0.7
	env.glow_bloom = 0.08
	if OS.has_environment("FOM_NOSSAO"): # dev: isolar o que causa artefatos nas bordas
		env.ssao_enabled = false
	if OS.has_environment("FOM_NOFOG"):
		env.volumetric_fog_enabled = false
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)


func _lights() -> void:
	for p in [Vector3(-2.4, 4.2, 1.6), Vector3(-2.4, 4.2, -4.0), Vector3(2.4, 4.2, -1.2)]: # fluorescentes vivas
		_lamp(p, Color(0.72, 0.90, 1.0), 2.2, 8.0, _lamps)
	_lamp(Vector3(-4.7, 4.3, 5.0), Color(1.0, 0.1, 0.05), 3.5, 9.0, _alarms)   # emergência pulsando
	_lamp(Vector3(4.7, 4.3, -5.0), Color(1.0, 0.1, 0.05), 3.5, 9.0, _alarms)
	_lamp(Vector3(-2.0, 1.2, -4.5), Color(0.4, 1.0, 0.6), 1.6, 3.5, [])          # brilho do console
	for z in [3.5, -0.5, -3.5]:                                                   # luar pelas janelas altas
		_lamp(Vector3(4.6, 3.9, z), Color(0.35, 0.5, 1.0), 1.3, 5.5, [])


func _lamp(pos: Vector3, color: Color, energy: float, rng: float, into: Array) -> void:
	var l := OmniLight3D.new()
	l.position = pos
	l.light_color = color
	l.light_energy = energy
	l.omni_range = rng
	l.shadow_enabled = true
	l.set_meta("e", energy)
	add_child(l)
	if into != null:
		into.append(l)


func _dust() -> void:
	var p := GPUParticles3D.new()
	p.amount = 300
	p.lifetime = 14.0
	p.preprocess = 14.0
	p.visibility_aabb = AABB(Vector3(-6, -1, -7), Vector3(12, 7, 14))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(4.5, 2.2, 5.5)
	pm.direction = Vector3(0, 1, 0)
	pm.spread = 180.0
	pm.initial_velocity_min = 0.01
	pm.initial_velocity_max = 0.05
	pm.gravity = Vector3(0, -0.01, 0)
	p.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.014, 0.014)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.albedo_color = Color(0.9, 0.95, 1.0, 0.8)
	q.material = m
	p.draw_pass_1 = q
	p.position = Vector3(0, 2.0, 0)
	add_child(p)
