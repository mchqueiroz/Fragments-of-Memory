class_name PlayerCtl
extends CharacterBody3D
## Controlador em primeira pessoa no padrão de jogos narrativos (Gone Home, Firewatch, Amnesia):
##  * movimento com aceleração/desaceleração (nada de parar seco), andar/correr/agachar, controle (gamepad);
##  * balanço de cabeça sutil (vertical + lateral, SEM rolar a câmera no balanço) com opção de desligar;
##  * passos sincronizados ao ponto mais baixo do balanço; leve "tranco" de câmera no passo e na aterrissagem;
##  * mira mínima, objetos examináveis que se abrem num anel (nada de ícones flutuando), modo "examinar";
##  * isqueiro (F): a chama segue a câmera com atraso, como a lanterna de Amnesia.
## Convenção de objeto examinável: StaticBody3D no grupo "clue" com meta "prompt" (verbo curto) e, opcional,
## "visual" (NodePath do modelo a girar no examinar) e "text" (legenda).

signal target_changed(target: Node3D, distance: float)
signal interacted(target: Node3D)
signal inspected(target: Node3D)
signal dropped(item: String)

const WALK := 1.7
const RUN := 3.1
const CROUCH := 0.85
const REACH := 2.2
const EYE_STAND := 1.6
const EYE_CROUCH := 1.05
const H_STAND := 1.75
const H_CROUCH := 1.15
const MOUSE := 0.0022

var head: Node3D  # posição do olho + inclinação (olhar para cima/baixo)
var rig: Node3D   # tranco e inclinação lateral por cima do olhar
var cam: Camera3D
var target: Node3D
var examining := false
var reading := false # diário aberto
var held := "none"  # item na mão (só lógica): "pistol" ao acordar na cena 1
var tremble := 0.0  # 0..1: tremor leve da câmera (mão trêmula)
var _diary: DiaryUI
var _menu: PauseMenu

var _cap := CapsuleShape3D.new()
var _col := CollisionShape3D.new()
var _eye := EYE_STAND
var _bob_t := 0.0
var _bob_amp := 0.0
var _last_step := -999
var _kick := 0.0
var _roll := 0.0
var _air := false
var _fall := 0.0
var _t := 0.0
var _crouching := false
var _running := false
var _ray: RayCast3D
var _sc: ShapeCast3D
var _cross := Crosshair.new()
var _prompt := Label.new()
var _hand: Node3D
var _flame := OmniLight3D.new()
var _flame_mesh := MeshInstance3D.new()
var _flame_on := false


func _ready() -> void:
	_ensure_input()
	Input.use_accumulated_input = false # menor latência do mouse
	_cap.radius = 0.3
	_cap.height = H_STAND
	_col.shape = _cap
	_col.position.y = H_STAND / 2.0
	add_child(_col)
	floor_snap_length = 0.35
	head = Node3D.new()
	head.position.y = EYE_STAND
	add_child(head)
	rig = Node3D.new()
	head.add_child(rig)
	cam = Camera3D.new()
	cam.fov = Settings.fov
	cam.current = true
	rig.add_child(cam)
	_diary = DiaryUI.new()
	add_child(_diary)
	_menu = PauseMenu.new()
	add_child(_menu)
	_ray = RayCast3D.new()
	_ray.target_position = Vector3(0, 0, -REACH)
	_ray.add_exception(self)
	cam.add_child(_ray)
	var sphere := SphereShape3D.new()
	sphere.radius = 0.14 # tolerância: não exige pontaria de cirurgião
	_sc = ShapeCast3D.new()
	_sc.shape = sphere
	_sc.target_position = Vector3(0, 0, -REACH)
	_sc.add_exception(self)
	cam.add_child(_sc)

	var ui := CanvasLayer.new()
	ui.layer = 12
	add_child(ui)
	_cross.custom_minimum_size = Vector2(32, 32)
	_cross.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	ui.add_child(_cross)
	_prompt.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_prompt.offset_top = -52
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.add_theme_font_size_override("font_size", 10)
	_prompt.modulate.a = 0.0
	ui.add_child(_prompt)

	_hand = Node3D.new()
	_hand.top_level = true
	add_child(_hand)
	_flame.light_color = Color(1.0, 0.66, 0.32)
	_flame.light_energy = 0.0
	_flame.omni_range = 4.5
	_flame.shadow_enabled = true
	_hand.add_child(_flame)
	var quad := QuadMesh.new()
	quad.size = Vector2(0.07, 0.11)
	var glow := GradientTexture2D.new() # chama = mancha radial suave, não um retângulo
	glow.fill = GradientTexture2D.FILL_RADIAL
	glow.fill_from = Vector2(0.5, 0.6)
	glow.fill_to = Vector2(0.5, 0.05)
	glow.width = 32
	glow.height = 32
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 0.85, 0.45, 1.0))
	grad.set_color(1, Color(1.0, 0.35, 0.08, 0.0))
	glow.gradient = grad
	var fm := StandardMaterial3D.new()
	fm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	fm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	fm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	fm.albedo_texture = glow
	quad.material = fm
	_flame_mesh.mesh = quad
	_flame_mesh.position.y = 0.04
	_flame_mesh.visible = false
	_hand.add_child(_flame_mesh)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


## Cria as ações extras e liga o controle (gamepad) às de movimento, sem depender do project.godot.
func _ensure_input() -> void:
	var ev := {
		"run": [_key(KEY_SHIFT), _btn(JOY_BUTTON_LEFT_STICK)],
		"crouch": [_key(KEY_CTRL), _key(KEY_C), _btn(JOY_BUTTON_B)],
		"interact": [_key(KEY_E), _btn(JOY_BUTTON_A)],
		"lighter": [_key(KEY_F), _btn(JOY_BUTTON_Y)],
		"diary": [_key(KEY_TAB), _btn(JOY_BUTTON_BACK)],
		"drop": [_key(KEY_Q), _btn(JOY_BUTTON_X)],
		"confront": [_key(KEY_G), _btn(JOY_BUTTON_RIGHT_SHOULDER)],
		"board": [_key(KEY_B), _btn(JOY_BUTTON_LEFT_SHOULDER)],
		"look_left": [_axis(JOY_AXIS_RIGHT_X, -1.0)],
		"look_right": [_axis(JOY_AXIS_RIGHT_X, 1.0)],
		"look_up": [_axis(JOY_AXIS_RIGHT_Y, -1.0)],
		"look_down": [_axis(JOY_AXIS_RIGHT_Y, 1.0)],
		"forward": [_axis(JOY_AXIS_LEFT_Y, -1.0)],
		"backward": [_axis(JOY_AXIS_LEFT_Y, 1.0)],
		"left": [_axis(JOY_AXIS_LEFT_X, -1.0)],
		"right": [_axis(JOY_AXIS_LEFT_X, 1.0)],
	}
	for action in ev:
		if not InputMap.has_action(action):
			InputMap.add_action(action, 0.2)
		for e in ev[action]:
			InputMap.action_add_event(action, e)


func _key(code: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = code
	return e


func _btn(b: JoyButton) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = b
	return e


func _axis(a: JoyAxis, v: float) -> InputEventJoypadMotion:
	var e := InputEventJoypadMotion.new()
	e.axis = a
	e.axis_value = v
	return e


func _unhandled_input(event: InputEvent) -> void:
	if examining or Story.busy:
		return
	if reading: # diário aberto: virar página, ou fechar
		if event.is_action_pressed("diary") or event.is_action_pressed("ui_cancel") or event.is_action_pressed("interact"):
			_set_reading(false)
		elif event.is_action_pressed("confront"):
			_set_reading(false)
			Story.confront()
		elif event.is_action_pressed("board"):
			_set_reading(false)
			Story.board()
		elif event.is_action_pressed("right") or (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN):
			_diary.flip(1)
		elif event.is_action_pressed("left") or (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP):
			_diary.flip(-1)
		return
	if event.is_action_pressed("ui_cancel"):
		_menu.open()
	elif event.is_action_pressed("diary"):
		_set_reading(true)
	elif event.is_action_pressed("board"):
		Story.board()
	elif event.is_action_pressed("drop") and held == "pistol":
		held = "none"
		dropped.emit("pistol")
	elif event is InputEventMouseMotion:
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and not OS.has_environment("FOM_NOMOUSE"):
			_look(event.relative * MOUSE * Settings.sensitivity)
	elif event.is_action_pressed("interact"):
		_interact()
	elif event.is_action_pressed("lighter") and held != "pistol": # com a pistola na mão, a mão está ocupada
		_flame_on = not _flame_on
		Sound.play("lighter_on" if _flame_on else "lighter_off", "Sfx", -4.0)


func _set_reading(on: bool) -> void:
	reading = on
	_diary.set_open(on)


func _look(rel: Vector2) -> void:
	rotate_y(-rel.x)
	head.rotation.x = clampf(head.rotation.x - rel.y * (-1.0 if Settings.invert_y else 1.0), -1.4, 1.4)


func _physics_process(delta: float) -> void:
	var frozen := examining or reading or Story.busy
	var dir := Vector2.ZERO if frozen else Input.get_vector("left", "right", "forward", "backward")
	var wants_crouch := Input.is_action_pressed("crouch") and not frozen
	_crouching = wants_crouch or (_cap.height < H_STAND - 0.05 and _ceiling_blocked())
	_running = Input.is_action_pressed("run") and not _crouching and dir.y < 0.3 and dir.length() > 0.2 and is_on_floor()
	var speed := CROUCH if _crouching else (RUN if _running else WALK)
	var wish := transform.basis * Vector3(dir.x, 0.0, dir.y) * speed
	var rate := (8.0 if dir.length() > 0.05 else 9.0) * (1.0 if is_on_floor() else 0.12) # peso: ~0,35 s para parar
	var k := 1.0 - exp(-rate * delta)
	velocity.x = lerpf(velocity.x, wish.x, k)
	velocity.z = lerpf(velocity.z, wish.z, k)
	if not is_on_floor():
		velocity += get_gravity() * delta
		_fall = minf(_fall, velocity.y)
	move_and_slide()
	if is_on_floor() and _air:
		if _fall < -2.0:
			_kick = -0.03
			Sound.play("step_%s_0" % Sound.surface, "Sfx", -3.0, 0.8)
		_fall = 0.0
	_air = not is_on_floor()
	_cap.height = lerpf(_cap.height, H_CROUCH if _crouching else H_STAND, 1.0 - exp(-10.0 * delta))
	_col.position.y = _cap.height / 2.0
	_eye = lerpf(_eye, EYE_CROUCH if _crouching else EYE_STAND, 1.0 - exp(-10.0 * delta))
	_scan()


func _ceiling_blocked() -> bool:
	var q := PhysicsRayQueryParameters3D.create(global_position + Vector3(0, H_CROUCH - 0.05, 0),
			global_position + Vector3(0, H_STAND + 0.1, 0))
	q.exclude = [get_rid()]
	return not get_world_3d().direct_space_state.intersect_ray(q).is_empty()


func _process(delta: float) -> void:
	_t += delta
	var s := Input.get_vector("look_left", "look_right", "look_up", "look_down")
	if s.length() > 0.0 and not (examining or reading or Story.busy):  # curva de resposta do controle: precisão perto do centro
		_look(s.normalized() * pow(s.length(), 1.7) * 2.6 * delta * Settings.sensitivity)
	var rv := get_real_velocity()
	var hv := Vector2(rv.x, rv.z).length()
	var moving := is_on_floor() and hv > 0.2
	_bob_amp = lerpf(_bob_amp, clampf(hv / RUN, 0.0, 1.0) if moving else 0.0, 1.0 - exp(-8.0 * delta))
	if moving:
		_bob_t += hv * delta * TAU / 1.5 # um ciclo completo a cada 1,5 m (dois passos)
	var b := Settings.bob
	var breathe := sin(_t * 1.15) * 0.0025 * (1.0 - _bob_amp)
	head.position = Vector3(cos(_bob_t) * 0.012 * _bob_amp * b, _eye + sin(_bob_t * 2.0) * 0.024 * _bob_amp * b + breathe, 0.0)
	if moving: # o pé toca o chão no ponto mais baixo do balanço
		var idx := int(floor((_bob_t - 0.75 * PI) / PI))
		if _last_step == -999:
			_last_step = idx
		if idx != _last_step:
			_last_step = idx
			_footstep()
	_kick = lerpf(_kick, 0.0, 1.0 - exp(-14.0 * delta))
	var strafe := 0.0 if (examining or reading or Story.busy) else Input.get_axis("left", "right")
	_roll = lerpf(_roll, -strafe * 0.010 * b, 1.0 - exp(-7.0 * delta)) # inclinação lateral mínima, separada do balanço
	rig.rotation = Vector3(_kick, 0.0, _roll) + Vector3(sin(_t * 29.0), sin(_t * 23.0 + 1.0), sin(_t * 31.0 + 2.0)) * 0.0012 * tremble
	_update_hand(delta)


func _footstep() -> void:
	_kick = -0.0035 * (1.8 if _running else 1.0) * Settings.bob
	var db := -16.0 if _crouching else (-4.5 if _running else -9.0)
	Sound.play("step_%s_%d" % [Sound.surface, randi() % 4], "Sfx", db, randf_range(0.92, 1.08) * (1.12 if _crouching else 1.0))


## A chama segue a câmera com atraso (posição rápida, rotação lenta), como a lanterna de Amnesia.
func _update_hand(delta: float) -> void:
	var want := cam.global_position + cam.global_basis * Vector3(0.26, -0.2, -0.45)
	_hand.global_position = _hand.global_position.lerp(want, 1.0 - exp(-18.0 * delta))
	var q := Quaternion(_hand.global_basis.orthonormalized()).slerp(Quaternion(cam.global_basis.orthonormalized()), 1.0 - exp(-9.0 * delta))
	_hand.global_basis = Basis(q)
	var e := (1.25 + 0.25 * sin(_t * 21.0) + 0.15 * sin(_t * 37.0 + 1.0)) if _flame_on else 0.0
	_flame.light_energy = lerpf(_flame.light_energy, e, 1.0 - exp(-14.0 * delta))
	_flame_mesh.visible = false # sem mãos na tela, só a luz da chama (sem sprite flutuando)


## Procura algo examinável: primeiro o raio central; senão uma esfera pequena (tolerância de pontaria).
func _scan() -> void:
	var best: Node3D = null
	var dist := 0.0
	_ray.force_raycast_update()
	if _ray.is_colliding():
		var c := _ray.get_collider()
		if c is Node3D and (c as Node).is_in_group("clue"):
			best = c
			dist = cam.global_position.distance_to(_ray.get_collision_point())
	if best == null:
		_sc.force_shapecast_update()
		var bd := 1e9
		for i in _sc.get_collision_count():
			var c := _sc.get_collider(i)
			if c is Node3D and (c as Node).is_in_group("clue"):
				var d := cam.global_position.distance_to(_sc.get_collision_point(i))
				if d < bd:
					bd = d
					best = c
					dist = d
	if examining or reading or Story.busy:
		best = null
	if best != target:
		target = best
		_cross.active = target != null
		var tw := create_tween()
		if target:
			_prompt.text = "E   %s" % str(target.get_meta("prompt", "Examinar"))
		tw.tween_property(_prompt, "modulate:a", 1.0 if target else 0.0, 0.18)
		target_changed.emit(target, dist)


func _interact() -> void:
	if target == null or reading or Story.busy:
		return
	var t := target
	interacted.emit(t)
	if t.has_meta("visual"):
		var src := get_node_or_null(t.get_meta("visual")) as Node3D
		if src:
			_inspect(t, src)


func _inspect(t: Node3D, src: Node3D) -> void:
	examining = true
	_cross.visible = false
	_prompt.visible = false
	var ins := Inspector.new()
	add_child(ins)
	ins.closed.connect(func():
		examining = false
		_cross.visible = true
		_prompt.visible = true
		inspected.emit(t))
	ins.show_object(src, str(t.get_meta("text", "")))
	Sound.play("paper", "Sfx", -6.0)
