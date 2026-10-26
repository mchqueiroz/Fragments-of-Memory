class_name Crosshair
extends Control
## Mira mínima: um ponto; quando há algo examinável sob ela, um anel se abre ao redor (sem ícones no mundo).

var active := false
var _r := 0.0


func _process(delta: float) -> void:
	_r = lerpf(_r, 7.0 if active else 0.0, 1.0 - exp(-14.0 * delta))
	queue_redraw()


func _draw() -> void:
	var c := size / 2.0
	draw_circle(c, 1.1, Color(1, 1, 1, 0.7))
	if _r > 0.8:
		draw_arc(c, _r, 0.0, TAU, 28, Color(1, 1, 1, 0.9 * _r / 7.0), 1.0)
