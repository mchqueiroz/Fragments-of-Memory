class_name Room
extends Node3D
## Base das cenas: carrega modelos com textura "nearest", cria objetos examináveis (grupo "clue"), luzes que tremem,
## poeira, ambiente e o pós-processo retrô. Cada cena herda esta classe e só descreve o seu conteúdo.
## Eixos: Blender (x, y, z) -> Godot (x, z, -y).

var player: PlayerCtl
var cinema: Cinema
var post: ShaderMaterial
var _env: Environment
var _lamps: Array[Light3D] = []
var _t := 0.0
var _glints: Array = []   # [corpo, brilho]: um ponto pulsa perto de toda pista ainda não examinada
var _glint_quad := QuadMesh.new()
var question := ""        # a pergunta que esta cena ajuda a responder no quadro de evidências (Story.LEDGER)
var _clock := -1.0        # relógio da cena (-1 = sem relógio): estourado, a cena recomeça
var _clock_cfg := {}
var _clock_index := -1
var _warned := {}
var _beat := 0.0
var _caught_now := false
var _hud: Label


func _process(delta: float) -> void:
	_t += delta
	_update_glints()
	_tick_clock(delta)
	_hud_refresh()
	for i in _lamps.size():
		var l := _lamps[i]
		var base: float = l.get_meta("e")
		var dip := 0.2 if bool(l.get_meta("flicker")) and fmod(_t * 0.9 + i * 2.3, 6.3) < 0.14 else 1.0
		l.light_energy = base * (0.94 + 0.06 * sin(_t * 17.0 + i * 2.0)) * dip


## Carrega um .glb e força textura "nearest" (pixel nítido) nos materiais.
func model(name: String) -> Node3D:
	var n: Node3D = (load("res://art/models/%s.glb" % name) as PackedScene).instantiate()
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		for s in (mi as MeshInstance3D).mesh.get_surface_count():
			var m := (mi as MeshInstance3D).get_active_material(s)
			if m is StandardMaterial3D:
				m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	return n


## Objeto examinável solto no espaço (caixa de colisão no grupo "clue"). `enabled=false` o deixa inativo até liberar.
func clue(id: String, prompt: String, pos: Vector3, size: Vector3, enabled := true) -> StaticBody3D:
	var b := StaticBody3D.new()
	b.position = pos
	add_child(b)
	clue_on(b, id, prompt, Vector3.ZERO, size, enabled)
	return b


func clue_on(node: Node3D, id: String, prompt: String, offset: Vector3, size: Vector3, enabled := true) -> void:
	var body: StaticBody3D = node if node is StaticBody3D else StaticBody3D.new()
	if body != node:
		node.add_child(body)
	body.set_meta("id", id)
	_add_glint(body)
	body.set_meta("prompt", prompt)
	if enabled:
		body.add_to_group("clue")
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = size
	cs.shape = bs
	cs.position = offset
	body.add_child(cs)


func _add_glint(body: Node3D) -> void:
	_glint_quad.size = Vector2(0.07, 0.07)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.no_depth_test = true
	m.albedo_color = Color(1.0, 0.9, 0.6, 0.0)
	var mi := MeshInstance3D.new()
	mi.mesh = _glint_quad
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	body.add_child(mi)
	_glints.append([body, mi])


func _update_glints() -> void:
	if player == null:
		return
	for i in _glints.size():
		if not is_instance_valid(_glints[i][0]) or not is_instance_valid(_glints[i][1]):
			continue
		var body: Node3D = _glints[i][0]
		var near := clampf((2.8 - player.global_position.distance_to(body.global_position)) / 1.2, 0.0, 1.0)
		var live := body.is_in_group("clue") and not body.has_meta("seen") and not Story.busy
		((_glints[i][1] as MeshInstance3D).material_override as StandardMaterial3D).albedo_color.a = near * (0.35 + 0.3 * sin(_t * 3.0 + i)) if live else 0.0


## Relógio: {seconds, warns [[segundos_restantes, texto]], fail}. Conversas o pausam; mudar de cena o cancela.
func start_clock(cfg: Dictionary) -> void:
	_clock_cfg = cfg
	_clock = float(cfg["seconds"])
	_clock_index = Story.index


func _tick_clock(delta: float) -> void:
	if _clock <= 0.0 or _caught_now or Story.busy or player == null:
		return
	if Story.index != _clock_index:
		_clock = -1.0
		return
	_clock -= delta
	for w in _clock_cfg.get("warns", []):
		if _clock <= float(w[0]) and not _warned.has(w[0]):
			_warned[w[0]] = true
			Story.say(str(w[1]), 4.0)
	if _clock < 25.0:
		_beat -= delta
		if _beat <= 0.0:
			_beat = 1.1
			Sound.play("heartbeat", "Sfx", -12.0)
	if _clock <= 0.0:
		_caught(str(_clock_cfg.get("fail", "Passos. Preciso sair daqui, agora.")))


## Flagrado: a cena recomeça (sem repetir notas já escritas); não há punição além de refazer com cuidado.
func _caught(msg: String) -> void:
	_caught_now = true
	Story.busy = true
	Story.say(msg, 3.0)
	await Story.fade_to(1.0, 1.0)
	Story.rollback()
	Story.busy = false                                                                # as cenas antigas não liberam o jogador sozinhas
	get_tree().reload_current_scene()


## Canto da tela: contador da cena (cada cena pode sobrescrever _hud_counter), relógio e a pergunta do quadro.
func _make_hud() -> void:
	var cl := CanvasLayer.new()
	cl.layer = 12
	_hud = Label.new()
	_hud.position = Vector2(8, 6)
	_hud.add_theme_font_size_override("font_size", 9)
	_hud.add_theme_constant_override("outline_size", 3)
	_hud.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	cl.add_child(_hud)
	add_child(cl)


func _hud_counter() -> String:
	return ""


func _hud_refresh() -> void:
	if _hud == null:
		return
	var lines: Array = []
	var top := _hud_counter()
	if _clock > 0.0:
		top += ("   " if top != "" else "") + "⧗ %d:%02d" % [int(_clock) / 60, int(_clock) % 60]
	if top != "":
		lines.append(top)
	if question != "":
		lines.append("? " + question)
	_hud.text = "\n".join(lines)
	_hud.modulate = Color(1.0, 0.55, 0.5, 0.9) if _clock > 0.0 and _clock < 25.0 else Color(1, 1, 1, 0.75)


func lamp(pos: Vector3, color: Color, energy: float, rng: float, flicker := true) -> OmniLight3D:
	var l := OmniLight3D.new()
	l.position = pos
	l.light_color = color
	l.light_energy = energy
	l.omni_range = rng
	l.shadow_enabled = true
	l.set_meta("e", energy)
	l.set_meta("flicker", flicker)
	add_child(l)
	_lamps.append(l)
	return l


func environment(ambient: Color, fog: Color, density := 0.02) -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color.BLACK
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = ambient
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.ssao_enabled = true
	env.ssao_radius = 0.9
	env.ssao_intensity = 2.5
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = density
	env.volumetric_fog_albedo = fog
	env.glow_enabled = true
	env.glow_intensity = 0.7
	env.glow_bloom = 0.08
	_env = env
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)


## O Kosmos brutalista (modelo do usuário) visto pela janela, ao longe: silhueta de concreto contra um céu de amanhecer.
## `dist` = distância da janela norte (z negativo) até a colunata; chamar depois de environment().
func backdrop_kosmos(dist := 60.0, sky_top := Color(0.30, 0.32, 0.45), sky_horizon := Color(1.0, 0.72, 0.52)) -> void:
	var k := model("kosmos")
	k.rotation.y = PI
	k.position = Vector3(0, -0.2, -dist - 3.0)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(0.30, 0.24, 0.28)
	for mi in k.find_children("*", "MeshInstance3D", true, false):
		(mi as MeshInstance3D).material_override = m
		(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(k)
	var g := MeshInstance3D.new()                                     # chão de fora, escuro
	var pm := PlaneMesh.new()
	pm.size = Vector2(900, 900)
	var gm := StandardMaterial3D.new()
	gm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	gm.albedo_color = Color(0.22, 0.18, 0.19)
	pm.material = gm
	g.mesh = pm
	g.position.y = -0.3
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(g)
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = sky_top
	sky_mat.sky_horizon_color = sky_horizon
	sky_mat.ground_horizon_color = sky_horizon * 0.6
	var sky := Sky.new()
	sky.sky_material = sky_mat
	_env.background_mode = Environment.BG_SKY
	_env.sky = sky


## Vida sonora da sala (ver Dressing.life): ex. life([["pipes_knock", 14, 40, -14.0, Vector3(-3, 1.5, 0), Vector3(1, 1, 3)]]).
func life(events: Array) -> void:
	Dressing.life(self, events)


## Atalhos para Dressing (ver game/dressing.gd).
func decal(tex: String, pos: Vector3, normal: Vector3, w: float, h: float, roll := 0.0, alpha := 1.0, depth := 0.5) -> Decal:
	return Dressing.decal(self, tex, pos, normal, w, h, roll, alpha, depth)


func dress(hx: float, hz: float, h: float, seed := 1, density := 1.0, papers := true) -> void:
	Dressing.dress(self, hx, hz, h, seed, density, papers)


func dust(extents: Vector3, at: Vector3) -> void:
	var p := GPUParticles3D.new()
	p.amount = 140
	p.lifetime = 12.0
	p.preprocess = 12.0
	p.visibility_aabb = AABB(at - extents - Vector3.ONE, (extents + Vector3.ONE) * 2.0)
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = extents
	pm.direction = Vector3(0, 1, 0)
	pm.spread = 180.0
	pm.initial_velocity_min = 0.01
	pm.initial_velocity_max = 0.05
	pm.gravity = Vector3(0, -0.01, 0)
	p.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.012, 0.012)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.albedo_color = Color(1.0, 0.92, 0.75, 0.45)
	q.material = m
	p.draw_pass_1 = q
	p.position = at
	add_child(p)


## Jogador + câmera de cinema + pós-processo retrô. `tint` esquenta (linha F) ou esfria (linha A) a imagem.
func setup_player(pos: Vector3, yaw: float, fov: float, tint: Vector3) -> void:
	player = PlayerCtl.new()
	player.position = pos
	add_child(player)
	player.interacted.connect(func(t: Node3D): t.set_meta("seen", true))
	if Story.cp_scene != scene_file_path:
		Story.checkpoint(scene_file_path)
	Sound.music_for(scene_file_path)
	_make_hud()
	player.rotation.y = yaw
	cinema = Cinema.new()
	add_child(cinema)
	cinema.setup(player.cam)
	cinema.fov_target = fov
	var layer := CanvasLayer.new()
	layer.layer = 10
	var r := ColorRect.new()
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	post = ShaderMaterial.new()
	post.shader = load("res://shaders/retro.gdshader")
	post.set_shader_parameter("tint", tint)
	post.set_shader_parameter("forget", 0.0)
	r.material = post
	layer.add_child(r)
	add_child(layer)
	player.target_changed.connect(func(t: Node3D, d: float):
		if t:
			cinema.focus(d)
		else:
			cinema.unfocus())
