extends Control
## Tela de título: Continuar (o jogo salva ao entrar em cada cena) / Novo jogo / Opções / Sair.

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
float h(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
void fragment(){
	vec2 q = UV - 0.5; q.x *= 1.78;
	float v = smoothstep(0.9, 0.1, length(q + vec2(sin(TIME*0.2)*0.05, 0.0)));
	float n = h(floor(FRAGCOORD.xy/2.0) + floor(TIME*12.0));
	float lines = 0.5 + 0.5*sin(UV.y*540.0);
	vec3 c = vec3(0.07,0.06,0.08) * v + vec3(0.02,0.02,0.03);
	c += (n-0.5) * 0.05 * (0.4 + v);
	c *= 0.9 + 0.1*lines;
	COLOR = vec4(c, 1.0);
}"""
	var mat := ShaderMaterial.new()
	mat.shader = sh
	bg.material = mat
	add_child(bg)
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(220, 0)
	box.add_theme_constant_override("separation", 6)
	center.add_child(box)
	var t := Label.new()
	t.text = "FRAGMENTS OF MEMORY"
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_font_size_override("font_size", 16)
	box.add_child(t)
	var sub := Label.new()
	sub.text = "Moscou, outubro de 1993"
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 9)
	sub.modulate = Color(1, 1, 1, 0.55)
	box.add_child(sub)
	var first: Button
	if Story.has_save():
		first = _button(box, "Continuar", Story.continue_game)
	var nova := _button(box, "Novo jogo", Story.new_game)
	var menu := PauseMenu.new()
	menu.from_title = true
	add_child(menu)
	var opts := _button(box, "Opções", func():
		box.visible = false
		menu.open())
	menu.closed.connect(func():
		box.visible = true
		opts.grab_focus())
	_button(box, "Sair", get_tree().quit)
	(first if first else nova).grab_focus()
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 2.0)
	Sound.scene("amb_room", "tinnitus", -40.0, "concrete", 0.9, 0.4)
	Sound.music_for("titulo")


func _button(box: Control, text: String, fn: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", 10)
	b.pressed.connect(fn)
	box.add_child(b)
	return b
