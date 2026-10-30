extends Room
## Cena genérica dos episódios 11–30: monta a sala (modelo ep_*.glb) ou o exterior (primitivas) a partir de rooms/data/<nome>.json,
## gerado por tools/episodios.py. Esquema do JSON (tudo em coordenadas do Godot):
##   kind "room"|"outdoor", model, size [x,y,z], title [linha1, linha2], tint [r,g,b], fov,
##   start {pos [x,y,z], yaw}, env {ambient, fog, density}, sky {top, horizon}, sun {rot [x,y], color, energy}, lamps [{pos,color,energy,range,flicker}],
##   dress [seed, density, papers] (decalques de sujeira), sound {amb, music, music_db, amb_db, ground, size, wet, emitters, life},
##   npcs [{id, model, face, pos [x,z], yaw, voice, pitch, prompt, pose, always, size}],
##   clues [{id, prompt, pos, size, note, alt, say, flag {nome: valor}, truth, ask {q, opts, truth, flag, correct, reply}, flash, optional, hidden, reveal, sound}],
##   needed [ids] (padrão: todas as pistas não opcionais), talk {npc, hint, lines, note, alt, say, flag}, intro [[texto, s]...], wake (bool),
##   outro [[texto, s]...], finale {endings [{min, max, flag [nome, valor], title, text}]}, primitives [...] (exterior), ground {color, tex}.
## Fluxo: examinar as pistas necessárias -> o personagem fala (se houver) -> Story.next_scene (ou o final, na cena 30).

@export var data_path := ""

var d: Dictionary = {}
var _npcs := {}               # id -> Actor
var _npc_bodies := {}         # id -> StaticBody3D (colisor de conversa)
var _clue_bodies := {}        # id -> StaticBody3D
var _clue_by_id := {}
var _done := {}
var _talked := false
var _ending := false
var _forget := 0.0
var _people: Array[Node3D] = []
var _flash_rect: ColorRect
var _fire_lights: Array[OmniLight3D] = []
var _wake := 0.0              # furtivo: barulho (correr) perto de quem dorme


func _ready() -> void:
	d = JSON.parse_string(FileAccess.get_file_as_string(data_path))
	_overlay()
	if Story.cp_scene != scene_file_path:
		Story.checkpoint(scene_file_path)
	var outdoor: bool = d.get("kind", "room") == "outdoor"
	if outdoor:
		_build_outdoor()
	else:
		add_child(model(str(d["model"])))
		var env: Dictionary = d.get("env", {})
		environment(_col(env.get("ambient", [0.1, 0.1, 0.1])), _col(env.get("fog", [0.7, 0.7, 0.7])), float(env.get("density", 0.02)))
	for l in d.get("lamps", []):
		lamp(_v3(l["pos"]), _col(l["color"]), float(l["energy"]), float(l["range"]), bool(l.get("flicker", false)))
	if d.has("dress"):
		var ds: Array = d["dress"]
		var sz: Array = d.get("size", [4, 4, 3])
		dress(float(sz[0]) / 2.0, float(sz[1]) / 2.0, float(sz[2]), int(ds[0]), float(ds[1]), bool(ds[2]) if ds.size() > 2 else true)
	if not outdoor:
		var sz2: Array = d.get("size", [4, 4, 3])
		dust(Vector3(float(sz2[0]) / 2.0, float(sz2[2]) / 2.0, float(sz2[1]) / 2.0), Vector3(0, float(sz2[2]) * 0.5, 0))
	_sound()
	var st: Dictionary = d.get("start", {"pos": [0, 0.05, 1], "yaw": 0})
	setup_player(_v3(st["pos"]), deg_to_rad(float(st.get("yaw", 0))), float(d.get("fov", 62)), _v3(d.get("tint", [1.0, 1.0, 1.0])))
	player.interacted.connect(_on_interacted)
	_make_models()
	_make_npcs()
	_make_clues()
	_make_flash()
	question = str(d.get("question", ""))
	_intro()


## Contador de pistas no canto (o relógio e a pergunta do quadro vêm de Room): o jogador sempre sabe quanto falta.
func _hud_counter() -> String:
	var ids := _needed()
	var n := 0
	for id in ids:
		if _done.has(id):
			n += 1
	if n >= ids.size():
		return "◆ pronto" + ("  ·  falar com alguém" if d.has("talk") and not _talked else "")
	return "◇ %d/%d" % [n, ids.size()]


## Textos reescritos ficam em rooms/text/<nome>.json e se sobrepõem aos do gerador (regerar a cena não os perde).
## Chaves: qualquer uma de topo (intro, outro, talk, needed, timer, watch, finale...) substitui; "clues" {id: campos} mescla; "add_clues" [..] acrescenta.
func _overlay() -> void:
	var path := "res://rooms/text/%s.json" % str(d.get("name", ""))
	if not FileAccess.file_exists(path):
		return
	var o: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	for k in o:
		if k == "clues":
			for c in d["clues"]:
				if o["clues"].has(c["id"]):
					c.merge(o["clues"][c["id"]], true)
		elif k == "add_clues":
			d["clues"].append_array(o[k])
		else:
			d[k] = o[k]


func _process(delta: float) -> void:
	super._process(delta)
	_stealth(delta)
	post.set_shader_parameter("forget", _forget)
	if _forget > 0.01:
		Sound.attention(_forget * 0.6)
	for i in _people.size():
		_people[i].rotation.z = sin(_t * 0.9 + i * 1.7) * 0.025
	for i in _fire_lights.size():
		_fire_lights[i].light_energy = 3.0 * (0.8 + 0.2 * sin(_t * 13.0 + i * 3.0) + 0.1 * sin(_t * 29.0 + i))


# ---- utilidades ---------------------------------------------------------------------------------------------------------------------

func _v3(a) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))


func _col(a) -> Color:
	return Color(float(a[0]), float(a[1]), float(a[2]))


## O JSON entrega números como float: os pesos de escolha (truth) precisam ser inteiros.
func _fix(lines: Array) -> Array:
	var out := []
	for l in lines:
		if l is Dictionary:
			var m: Dictionary = l.duplicate(true)
			if m.has("truth"):
				var ints := []
				for v in m["truth"]:
					ints.append(int(v))
				m["truth"] = ints
			if m.has("reply"):
				var rep := []
				for r in m["reply"]:
					rep.append(_fix(r))
				m["reply"] = rep
			out.append(m)
		else:
			out.append(l)
	return out


func _sound() -> void:
	var s: Dictionary = d.get("sound", {})
	Sound.scene(str(s.get("amb", "amb_room")), str(s.get("music", "tinnitus")), float(s.get("music_db", -50.0)), str(s.get("ground", "parquet")),
		float(s.get("size", 0.4)), float(s.get("wet", 0.2)))
	Sound._amb.volume_db = float(s.get("amb_db", -30.0))
	Sound._amb.set_meta("db", float(s.get("amb_db", -30.0)))
	for e in s.get("emitters", []):
		Sound.emitter(self, str(e[0]), _v3(e[1]), float(e[2]), float(e[3]), float(e[4]) if e.size() > 4 else 20500.0)
	var life_events: Array = []
	for ev in s.get("life", []):
		life_events.append([str(ev[0]), float(ev[1]), float(ev[2]), float(ev[3]), _v3(ev[4]), _v3(ev[5])])
	if not life_events.is_empty():
		life(life_events)


## Modelos soltos (ex.: o tabuleiro de xadrez): [{model, pos, rot (graus), scale}].
func _make_models() -> void:
	for m in d.get("models", []):
		var n := model(str(m["model"]))
		n.position = _v3(m["pos"])
		n.rotation_degrees.y = float(m.get("rot", 0))
		n.scale = Vector3.ONE * float(m.get("scale", 1.0))
		add_child(n)


func _make_npcs() -> void:
	for n in d.get("npcs", []):
		var a := Actor.new()
		var p: Array = n["pos"]
		a.position = Vector3(float(p[0]), 0.0, float(p[1]))
		add_child(a)
		a.setup(str(n["model"]), str(n["face"]), player)
		a.voice_tag = str(n.get("voice", "low"))
		a.voice_pitch = float(n.get("pitch", 1.0))
		if str(n.get("pose", "")) == "slump":                                          # dorme debruçado sobre a mesa
			a.rotation_degrees.x = 38.0
		var sz: Array = n.get("size", [0.7, 1.8, 0.5])
		var talks: bool = str(d.get("talk", {}).get("npc", "")) == str(n["id"])                        # só quem tem o que dizer mostra "Falar"
		clue_on(a, str(n["id"]), str(n.get("prompt", "Falar")), Vector3(0, 0.9, 0), _v3(sz), bool(n.get("always", false)) and (talks or n.has("idle")))
		_npcs[str(n["id"])] = a
		_npc_bodies[str(n["id"])] = a.get_child(a.get_child_count() - 1)


func _make_clues() -> void:
	for c in d.get("clues", []):
		var b := clue(str(c["id"]), str(c["prompt"]), _v3(c["pos"]), _v3(c["size"]))
		_clue_by_id[str(c["id"])] = c
		_clue_bodies[str(c["id"])] = b
		if bool(c.get("hidden", false)):
			b.remove_from_group("clue")


func _needed() -> Array:
	if d.has("needed"):
		return d["needed"]
	var ids := []
	for c in d.get("clues", []):
		if not bool(c.get("optional", false)) and not bool(c.get("hidden", false)):
			ids.append(c["id"])
	return ids


func _all_done() -> bool:
	for id in _needed():
		if not _done.has(id):
			return false
	return true


func _make_flash() -> void:
	var cl := CanvasLayer.new()
	cl.layer = 15
	_flash_rect = ColorRect.new()
	_flash_rect.color = Color(0.97, 0.95, 0.9)
	_flash_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_flash_rect.modulate.a = 0.0
	cl.add_child(_flash_rect)
	add_child(cl)


## Lampejo de memória: a tela estoura em branco e volta, com o som de transição.
func _flash() -> void:
	Sound.play("transition", "Sfx", -2.0)
	_flash_rect.modulate.a = 1.0
	create_tween().tween_property(_flash_rect, "modulate:a", 0.0, 1.6)
	var tw := create_tween()
	tw.tween_property(self, "_forget", 0.6, 0.2)
	tw.tween_property(self, "_forget", 0.0, 1.6)


# ---- fluxo ---------------------------------------------------------------------------------------------------------------------------

func _intro() -> void:
	var t: Array = d.get("title", ["", ""])
	Story.busy = true
	await Story.fade_to(1.0, 0.01)
	await get_tree().create_timer(0.5).timeout
	Story.fade_to(0.0, 1.8)
	Story.card(str(t[0]), str(t[1]), 3.2)
	if bool(d.get("wake", false)):
		_forget = 1.0
		create_tween().tween_property(self, "_forget", 0.0, 6.0)
	await get_tree().create_timer(1.8).timeout
	Story.busy = false                                                                # o jogador já anda enquanto a voz em off fala
	cinema.letterbox(false, 1.0)
	if d.has("timer"):
		start_clock(d["timer"])
	for line in d.get("intro", []):
		Story.say(str(line[0]), float(line[1]))
		await get_tree().create_timer(float(line[1]) + 0.4).timeout


## Furtivo: correr perto de quem dorme o acorda (o relógio da cena está em Room.start_clock).
func _stealth(delta: float) -> void:
	if _ending or _caught_now or Story.busy or player == null:
		return
	var wt: Dictionary = d.get("watch", {})
	if wt.is_empty() or not _npcs.has(str(wt["npc"])):
		return
	var near: bool = player.global_position.distance_to(_npcs[str(wt["npc"])].global_position) < float(wt.get("radius", 3.0))
	if near and player._running:
		_wake += delta
		if _wake > float(wt.get("limit", 1.2)) * 0.5 and not _warned.has("wake"):
			_warned["wake"] = true
			Story.say(str(wt.get("warn", "Ele se mexeu. Devagar.")), 3.0)
		if _wake > float(wt.get("limit", 1.2)):
			_caught(str(wt.get("fail", "Ele abriu os olhos.")))
	else:
		_wake = maxf(0.0, _wake - delta * 0.5)


func _on_interacted(t: Node3D) -> void:
	var id := str(t.get_meta("id", ""))
	if _npcs.has(id):
		var idle = _npc_idle(id)
		if idle != "":
			Story.say(idle, 3.5)
		else:
			_talk(id)
		return
	if not _clue_by_id.has(id):
		return
	var c: Dictionary = _clue_by_id[id]
	if _done.has(id) and not bool(c.get("repeat", false)):
		return
	_done[id] = true
	if c.has("sound"):
		Sound.play(str(c["sound"]), "Sfx", -3.0)
	if bool(c.get("flash", false)):
		_flash()
	if c.has("ask"):
		await _ask(c["ask"])
	if c.has("flag"):
		for k in c["flag"]:
			Story.flags[k] = c["flag"][k]
	if c.has("truth"):
		Story.truth += int(c["truth"])
	if c.has("give"):
		Story.give(str(c["give"]))
	var key := "%s:%s" % [d.get("name", ""), id]
	if c.has("note"):
		Story.add_note(str(c["note"]), str(c.get("alt", "")), key)
	var say_txt := str(c.get("say", ""))
	if c.has("uses") and Story.items.has(str(c["uses"]["item"])):                  # o objeto que carrego muda o que vejo
		var u: Dictionary = c["uses"]
		if u.has("note"):
			Story.add_note(str(u["note"]), str(u.get("alt", "")), key + "+")
		say_txt = str(u.get("say", say_txt))
	if say_txt != "":
		Story.say(say_txt, float(c.get("say_s", 4.5)))
	if c.has("reveal"):                                                                # libera outra pista escondida
		var r := str(c["reveal"])
		if _clue_bodies.has(r):
			_clue_bodies[r].add_to_group("clue")
	_check()


func _ask(a: Dictionary) -> void:
	await get_tree().process_frame                                                    # o E que abriu a escolha não conta
	var opts := PackedStringArray()
	for o in a["opts"]:
		opts.append(str(o))
	var gates: Dictionary = a.get("gates", {})                                          # opção que só existe com o saber certo no quadro
	for k in gates:
		if not Story.is_resolved(str(gates[k]["ledger"])):
			opts[int(k)] = str(gates[k]["text"])
	var i := await Story.ask(str(a["q"]), opts, float(a.get("seconds", 0.0)), int(a.get("default", -1)))
	if gates.has(str(i)) and not Story.is_resolved(str(gates[str(i)]["ledger"])):
		await Story.talk([str(gates[str(i)].get("fail", "(Nenhum nome vem.)"))])
		i = int(gates[str(i)]["as"])
	while a.has("must") and i != int(a["correct"]):                                      # puzzle: só segue quem acerta
		Story.apply(a, i)
		await Story.talk(_fix(a["reply"][i]))
		await get_tree().process_frame
		i = await Story.ask(str(a["q"]), opts, 0.0)
	Story.apply(a, i)
	if a.has("reply"):
		await Story.talk(_fix(a["reply"][i]))


func _check() -> void:
	if _ending or _talked or not _all_done():
		return
	_clock = -1.0                                                                       # objetivo cumprido: o relógio para
	var tk: Dictionary = d.get("talk", {})
	if tk.is_empty():
		_finish()
		return
	if _npc_bodies.has(str(tk["npc"])):
		_npc_bodies[str(tk["npc"])].add_to_group("clue")
	Story.say(str(tk.get("hint", "Acho que posso conversar agora.")), 4.5)


## Fala curta de quem está na cena mas não é o interlocutor (campo "idle" do NPC); "" = é o interlocutor.
func _npc_idle(id: String) -> String:
	if str(d.get("talk", {}).get("npc", "")) == id:
		return ""
	for n in d.get("npcs", []):
		if str(n["id"]) == id:
			return str(n.get("idle", ""))
	return ""


func _talk(id: String) -> void:
	var tk: Dictionary = d.get("talk", {})
	if _talked or tk.is_empty() or str(tk["npc"]) != id:
		return
	if not _all_done():
		Story.say(str(d.get("not_yet", "Ainda não. Olhe em volta primeiro.")), 3.5)
		return
	_talked = true
	var a: Actor = _npcs[id]
	cinema.letterbox(true, 0.8)
	Sound.duck(true)
	a.speak(120.0)
	await Story.talk(_fix(tk["lines"]))
	a.speak(0.05)
	Sound.duck(false)
	cinema.letterbox(false, 1.2)
	if tk.has("give"):
		Story.give(str(tk["give"]))
	if tk.has("note"):
		Story.add_note(str(tk["note"]), str(tk.get("alt", "")), "%s:conversa" % d.get("name", ""))
	if tk.has("flag"):
		for k in tk["flag"]:
			Story.flags[k] = tk["flag"][k]
	if tk.has("say"):
		Story.say(str(tk["say"]), 4.0)
	await get_tree().create_timer(3.5).timeout
	_finish()


func _finish() -> void:
	if _ending:
		return
	_ending = true
	for line in d.get("outro", []):
		Story.say(str(line[0]), float(line[1]))
		await get_tree().create_timer(float(line[1]) + 0.3).timeout
	if d.has("finale"):
		await _finale()
		return
	Story.next_scene()


## Final do jogo: o desfecho depende de `Story.truth` e das flags guardadas pelas escolhas.
func _finale() -> void:
	var chosen: Dictionary = {}
	for e in d["finale"]["endings"]:
		var ok := true
		if e.has("min") and Story.truth < int(e["min"]):
			ok = false
		if e.has("max") and Story.truth > int(e["max"]):
			ok = false
		if e.has("flag") and bool(Story.flags.get(e["flag"][0], false)) != bool(e["flag"][1]):
			ok = false
		if e.has("when") and not Story.test(e["when"]):
			ok = false
		if ok:
			chosen = e
			break
	_flash_rect.modulate.a = 0.0
	create_tween().tween_property(_flash_rect, "modulate:a", 1.0, 3.0)
	await get_tree().create_timer(3.2).timeout
	var lab := Label.new()
	lab.set_anchors_preset(Control.PRESET_FULL_RECT)
	lab.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lab.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	lab.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lab.add_theme_font_size_override("font_size", 13)
	lab.add_theme_color_override("font_color", Color(0.12, 0.10, 0.10))
	lab.text = "%s\n\n%s" % [str(chosen.get("title", "FIM")), str(chosen.get("text", ""))]
	_flash_rect.add_child(lab)
	await get_tree().create_timer(12.0).timeout
	lab.text = "FRAGMENTS OF MEMORY\n\nObrigado por lembrar."
	await get_tree().create_timer(6.0).timeout
	lab.text = "Um jogo de Michael Queiroz\n\nGodot 4.6 · Blender\nVozes russas: LibriVox (domínio público)\nMandelstam · Pushkin\n\nMoscou, 3–4 de outubro de 1993"
	await get_tree().create_timer(10.0).timeout
	Story.end_game()


# ---- exteriores ------------------------------------------------------------------------------------------------------------------------

func _mat(color: Color, glow := false, rough := 0.85) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	if glow:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = 1.0
	return m


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


func _build_outdoor() -> void:
	var sk: Dictionary = d.get("sky", {"top": [0.3, 0.3, 0.4], "horizon": [0.7, 0.6, 0.5]})
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = _col(sk["top"])
	sm.sky_horizon_color = _col(sk["horizon"])
	sm.ground_horizon_color = _col(sk["horizon"]) * 0.7
	sm.ground_bottom_color = _col(sk["top"]) * 0.4
	var sky := Sky.new()
	sky.sky_material = sm
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = float(d.get("ambient", 0.9))
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var fg: Dictionary = d.get("env", {})
	env.fog_enabled = true
	env.fog_light_color = _col(fg.get("fog", [0.55, 0.5, 0.48]))
	env.fog_density = float(fg.get("density", 0.006))
	env.fog_sky_affect = 0.6
	env.glow_enabled = true
	env.glow_intensity = 0.5
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	_env = env
	var sn: Dictionary = d.get("sun", {"rot": [-30, 20], "color": [1, 0.85, 0.7], "energy": 1.0})
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(float(sn["rot"][0]), float(sn["rot"][1]), 0)
	sun.light_color = _col(sn["color"])
	sun.light_energy = float(sn["energy"])
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0
	add_child(sun)
	var gr: Dictionary = d.get("ground", {"color": [0.3, 0.3, 0.3]})
	var gm := _mat(_col(gr["color"]))
	if gr.has("tex"):
		gm.albedo_texture = load("res://art/tex/%s.png" % str(gr["tex"]))
		gm.uv1_triplanar = true
		gm.uv1_scale = Vector3.ONE * 0.2
	var gp := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(600, 600)
	pm.material = gm
	gp.mesh = pm
	add_child(gp)
	var body := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var bs := BoxShape3D.new()
	bs.size = Vector3(600, 1, 600)
	cs.shape = bs
	cs.position.y = -0.5
	body.add_child(cs)
	add_child(body)
	for p in d.get("primitives", []):
		_primitive(p)


func _primitive(p: Dictionary) -> void:
	var t := str(p["t"])
	var c := _col(p.get("c", [0.4, 0.4, 0.4]))
	match t:
		"box":
			_solid(_v3(p["p"]), _v3(p["s"]), _mat(c, bool(p.get("glow", false))), bool(p.get("solid", false)), deg_to_rad(float(p.get("rot", 0))))
		"cyl":
			var m := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = float(p["r"]) * float(p.get("taper", 1.0))
			cm.bottom_radius = float(p["r"])
			cm.height = float(p["h"])
			cm.material = _mat(c, bool(p.get("glow", false)))
			m.mesh = cm
			m.position = _v3(p["p"])
			add_child(m)
		"sphere":
			var m2 := MeshInstance3D.new()
			var sm2 := SphereMesh.new()
			sm2.radius = float(p["r"])
			sm2.height = float(p["r"]) * 2.0
			sm2.material = _mat(c)
			m2.mesh = sm2
			m2.position = _v3(p["p"])
			add_child(m2)
		"tree":
			var pos := Vector3(float(p["p"][0]), 0, float(p["p"][1]))
			var h := float(p.get("h", 6.0))
			_solid(pos + Vector3(0, h * 0.35, 0), Vector3(0.35, h * 0.7, 0.35), _mat(Color(0.22, 0.16, 0.12)), true)
			_primitive({"t": "sphere", "p": [pos.x, h * 0.85, pos.z], "r": h * 0.32, "c": p.get("leaf", [0.45, 0.35, 0.15])})
			_primitive({"t": "sphere", "p": [pos.x + h * 0.15, h * 0.7, pos.z - h * 0.1], "r": h * 0.22, "c": p.get("leaf", [0.45, 0.35, 0.15])})
		"bldg":
			var bm := _mat(Color(1, 1, 1))
			bm.albedo_texture = load("res://art/tex/facade.png")
			var s: Vector3 = _v3(p["s"])
			bm.uv1_scale = Vector3(s.z / 12.0, s.y / 12.0, 1.0)
			bm.emission_enabled = true
			bm.emission_texture = load("res://art/tex/facade_emit.png")
			bm.emission_energy_multiplier = float(p.get("emit", 1.2))
			var pp := Vector3(float(p["p"][0]), s.y / 2.0, float(p["p"][1]))
			_solid(pp, s, bm, true)
		"people":
			_crowd(Vector3(float(p["p"][0]), 0, float(p["p"][1])), int(p.get("n", 6)), float(p.get("r", 2.0)))
		"grave":
			var pos2 := Vector3(float(p["p"][0]), 0, float(p["p"][1]))
			var rot := deg_to_rad(float(p.get("rot", 0)))
			_solid(pos2 + Vector3(0, 0.45, 0), Vector3(0.1, 0.9, 0.1), _mat(Color(0.35, 0.3, 0.25)), false, rot)
			_solid(pos2 + Vector3(0, 0.7, 0), Vector3(0.5, 0.1, 0.1), _mat(Color(0.35, 0.3, 0.25)), false, rot)
			_solid(pos2 + Vector3(0, 0.08, 0.5), Vector3(0.7, 0.16, 1.2), _mat(Color(0.6, 0.62, 0.6)), false, rot)
		"bench":
			var pb := Vector3(float(p["p"][0]), 0, float(p["p"][1]))
			var rb := deg_to_rad(float(p.get("rot", 0)))
			_solid(pb + Vector3(0, 0.45, 0), Vector3(1.6, 0.06, 0.5), _mat(Color(0.35, 0.25, 0.15)), false, rb)
			_solid(pb + Vector3(0, 0.75, -0.22), Vector3(1.6, 0.4, 0.05), _mat(Color(0.35, 0.25, 0.15)), false, rb)
		"lamp":
			var pl := Vector3(float(p["p"][0]), 0, float(p["p"][1]))
			_solid(pl + Vector3(0, 3.0, 0), Vector3(0.14, 6.0, 0.14), _mat(Color(0.22, 0.22, 0.24)), true)
			_solid(pl + Vector3(0.5, 6.0, 0), Vector3(1.0, 0.12, 0.12), _mat(Color(0.22, 0.22, 0.24)), false)
			_solid(pl + Vector3(1.0, 5.9, 0), Vector3(0.5, 0.14, 0.3), _mat(Color(1.0, 0.85, 0.55), true), false)
		"light":
			lamp(_v3(p["p"]), c, float(p.get("e", 2.0)), float(p.get("r", 8.0)), bool(p.get("flicker", false)))
		"fire":
			var pf := Vector3(float(p["p"][0]), 0, float(p["p"][1]))
			var cm2 := CylinderMesh.new()
			cm2.top_radius = 0.32
			cm2.bottom_radius = 0.32
			cm2.height = 0.9
			cm2.material = _mat(Color(0.28, 0.12, 0.08))
			var bar := MeshInstance3D.new()
			bar.mesh = cm2
			bar.position = pf + Vector3(0, 0.45, 0)
			add_child(bar)
			_solid(pf + Vector3(0, 1.1, 0), Vector3(0.45, 0.5, 0.45), _mat(Color(1.0, 0.55, 0.15), true), false)
			_fire_lights.append(lamp(pf + Vector3(0, 1.6, 0), Color(1.0, 0.55, 0.2), 3.0, 9.0, false))
		"snow":
			_snow(_v3(p["p"]), _v3(p.get("s", [30, 12, 30])))


func _crowd(center: Vector3, n: int, radius: float) -> void:
	var r := RandomNumberGenerator.new()
	r.seed = int(center.x * 100 + center.z)
	for i in n:
		var pn := Node3D.new()
		pn.position = center + Vector3(r.randf_range(-radius, radius), 0, r.randf_range(-radius * 0.6, radius * 0.6))
		pn.rotation.y = r.randf() * TAU
		var tone := r.randf_range(0.05, 0.2)
		var cm := CapsuleMesh.new()
		cm.radius = 0.24
		cm.height = 1.5
		cm.material = _mat(Color(tone, tone * 0.9, tone * 0.85))
		var body := MeshInstance3D.new()
		body.mesh = cm
		body.position.y = 0.85
		pn.add_child(body)
		var sph := SphereMesh.new()
		sph.radius = 0.14
		sph.height = 0.28
		sph.material = _mat(Color(0.55, 0.42, 0.36))
		var head := MeshInstance3D.new()
		head.mesh = sph
		head.position.y = 1.78
		pn.add_child(head)
		add_child(pn)
		_people.append(pn)


func _snow(at: Vector3, extents: Vector3) -> void:
	var pt := GPUParticles3D.new()
	pt.amount = 700
	pt.lifetime = 8.0
	pt.preprocess = 8.0
	pt.visibility_aabb = AABB(-extents, extents * 2.0)
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = extents
	pm.direction = Vector3(0.15, -1.0, 0.05)
	pm.spread = 8.0
	pm.initial_velocity_min = 1.0
	pm.initial_velocity_max = 2.0
	pt.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.06, 0.06)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.albedo_color = Color(0.95, 0.96, 1.0, 0.9)
	q.material = m
	pt.draw_pass_1 = q
	pt.position = at
	add_child(pt)
