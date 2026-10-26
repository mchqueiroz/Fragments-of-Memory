class_name Dressing
extends RefCounted
## Sujeira e desgaste por decalques (Decal do Godot): manchas d'água, escorridos, rachaduras, tinta descascada, sujeira no chão,
## marcas de sapato e papéis soltos. Qualquer cena chama `Dressing.dress(self, ...)`; as cenas Room têm o atalho `dress(...)`.
## Texturas geradas por tools/decals.py (art/tex/decal_*.png).


## Projeta uma textura de sujeira/desgaste (decalque) numa superfície. `pos` = ponto na superfície, `normal` = para onde ela
## "olha" (para dentro da sala). `roll` gira a imagem; em paredes, o topo da imagem fica para cima.
static func decal(parent: Node3D, tex: String, pos: Vector3, normal: Vector3, w: float, h: float, roll := 0.0, alpha := 1.0, depth := 0.5) -> Decal:
	var d := Decal.new()
	d.texture_albedo = load("res://art/tex/decal_%s.png" % tex)
	d.size = Vector3(w, depth, h)
	d.modulate = Color(1, 1, 1, alpha)
	var n := normal.normalized()
	var x: Vector3
	if absf(n.y) > 0.9:                                  # piso ou teto: eixo X girado ao acaso
		x = Vector3(cos(roll), 0, sin(roll))
		if n.y < 0:
			x = -x
	else:                                                # parede: topo da imagem para cima, `roll` só vira de cabeça para baixo
		x = Vector3.UP.cross(n).normalized() * (1.0 if cos(roll) >= 0 else -1.0)
	var y := n
	var z := x.cross(y)
	d.basis = Basis(x, y, z)
	d.position = pos + n * (depth * 0.5 - 0.05)
	d.cull_mask = 1
	parent.add_child(d)
	return d


## Sujeira e desgaste automáticos numa sala retangular centrada na origem (hx, hz = meia largura/profundidade; h = pé-direito):
## manchas d'água e escorridos no alto, rachaduras, tinta descascada, faixa de sujeira junto ao chão; no chão, terra, marcas
## de sapato e papéis soltos. `density` > 1 suja mais (laboratório, porão); `seed` mantém a sala sempre igual.
static func dress(parent: Node3D, hx: float, hz: float, h: float, seed := 1, density := 1.0, papers := true) -> void:
	var r := RandomNumberGenerator.new()
	r.seed = seed
	var walls := [
		[Vector3(-hx, 0, 0), Vector3.RIGHT, hz * 2.0],
		[Vector3(hx, 0, 0), Vector3.LEFT, hz * 2.0],
		[Vector3(0, 0, -hz), Vector3.BACK, hx * 2.0],
		[Vector3(0, 0, hz), Vector3.FORWARD, hx * 2.0],
	]
	for wall in walls:
		var o: Vector3 = wall[0]
		var n: Vector3 = wall[1]
		var length: float = wall[2]
		var t := Vector3.UP.cross(n).normalized()
		decal(parent, "grime", o + Vector3(0, 0.35, 0), n, length, 0.7, PI, 0.6)                       # faixa de sujeira junto ao chão
		for i in int(2.0 * density):
			decal(parent, "stain", o + t * r.randf_range(-length * 0.45, length * 0.45) + Vector3(0, h - r.randf_range(0.4, 1.0), 0),
				n, r.randf_range(0.7, 1.4), r.randf_range(0.7, 1.4), 0.0, r.randf_range(0.25, 0.5))
		for i in int(1.0 * density):
			decal(parent, "streak", o + t * r.randf_range(-length * 0.45, length * 0.45) + Vector3(0, h - 0.7, 0),
				n, r.randf_range(0.6, 1.0), 1.4, 0.0, r.randf_range(0.5, 0.8))
		if r.randf() < 0.7 * density:
			decal(parent, "crack", o + t * r.randf_range(-length * 0.4, length * 0.4) + Vector3(0, r.randf_range(0.8, h - 0.6), 0),
				n, r.randf_range(0.5, 0.9), r.randf_range(0.5, 0.9), 0.0, 0.9)
		if r.randf() < 0.6 * density:
			decal(parent, "peeling", o + t * r.randf_range(-length * 0.4, length * 0.4) + Vector3(0, r.randf_range(0.7, h - 0.5), 0),
				n, r.randf_range(0.5, 1.0), r.randf_range(0.5, 1.0), 0.0, 0.85)
	for i in int(5.0 * density):
		decal(parent, "dirt", Vector3(r.randf_range(-hx, hx) * 0.9, 0, r.randf_range(-hz, hz) * 0.9), Vector3.UP,
			r.randf_range(0.8, 1.8), r.randf_range(0.8, 1.8), r.randf() * TAU, r.randf_range(0.5, 0.9), 0.3)
	for i in int(5.0 * density):
		decal(parent, "scuff", Vector3(r.randf_range(-hx, hx) * 0.8, 0, r.randf_range(-hz, hz) * 0.8), Vector3.UP,
			r.randf_range(0.5, 1.0), r.randf_range(0.5, 1.0), r.randf() * TAU, 0.8, 0.3)
	if papers:
		for i in int(6.0 * density):
			decal(parent, "paper", Vector3(r.randf_range(-hx, hx) * 0.85, 0, r.randf_range(-hz, hz) * 0.85), Vector3.UP,
				0.3, 0.3, r.randf() * TAU, 1.0, 0.3)


## Vida sonora de qualquer cena: cada evento = [som, intervalo mínimo (s), intervalo máximo (s), db, centro, extensão (Vector3)].
## Toca o som uma vez (Sound.once) numa posição aleatória da área, de tempos em tempos, enquanto a cena existir.
static func life(parent: Node3D, events: Array) -> void:
	for ev in events:
		_life_loop(parent, ev)


static func _life_loop(parent: Node3D, ev: Array) -> void:
	while is_instance_valid(parent) and parent.is_inside_tree():
		var tree := parent.get_tree()
		await tree.create_timer(randf_range(ev[1], ev[2])).timeout
		if not is_instance_valid(parent) or not parent.is_inside_tree():
			return
		var e: Vector3 = ev[5]
		Sound.once(parent, ev[0], (ev[4] as Vector3) + Vector3(randf_range(-e.x, e.x), randf_range(-e.y, e.y), randf_range(-e.z, e.z)), ev[3])
