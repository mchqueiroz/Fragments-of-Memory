class_name Cinema
extends Node
## Linguagem de câmera: letterbox 2.39:1, foco seletivo (rack focus), câmera na mão e FOV por cena.

const VIEW := Vector2(480, 270)
const BAR := 34.0 # (270 - 480/2.39) / 2

var cam: Camera3D
var fov_target := 70.0
var _attr := CameraAttributesPractical.new()
var _top := ColorRect.new()
var _bottom := ColorRect.new()
var _bar := BAR:
	set(v):
		_bar = v
		_top.size = Vector2(VIEW.x, v)
		_bottom.size = Vector2(VIEW.x, v)
		_bottom.position = Vector2(0, VIEW.y - v)
var _t := 0.0
var _focused := false


func setup(camera: Camera3D) -> void:
	cam = camera
	cam.attributes = _attr
	_attr.dof_blur_far_enabled = true
	_attr.dof_blur_near_enabled = true
	_attr.dof_blur_amount = 0.0
	var layer := CanvasLayer.new()
	layer.layer = 11 # acima do pós-processo, as barras ficam pretas puras
	for r in [_top, _bottom]:
		r.color = Color.BLACK
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.add_child(r)
	add_child(layer)
	_bar = BAR


## Barras de cinema entram/saem. Use em diálogos e revelações.
func letterbox(on: bool, secs := 1.0) -> void:
	create_tween().tween_property(self, "_bar", BAR if on else 0.0, secs).set_trans(Tween.TRANS_SINE)


## Rack focus: foca em algo a `dist` metros, desfocando o primeiro e o último plano.
func focus(dist: float) -> void:
	_focused = true
	_attr.dof_blur_far_distance = dist + 0.6
	_attr.dof_blur_far_transition = 2.0
	_attr.dof_blur_near_distance = maxf(dist - 0.5, 0.2)
	_attr.dof_blur_near_transition = 0.8
	create_tween().tween_property(_attr, "dof_blur_amount", 0.12, 0.45)


func unfocus() -> void:
	if _focused:
		_focused = false
		create_tween().tween_property(_attr, "dof_blur_amount", 0.0, 0.5)


func _process(delta: float) -> void:
	_t += delta
	cam.fov = lerpf(cam.fov, fov_target, 1.0 - exp(-2.0 * delta))
	# câmera na mão: oscilação lenta e quase imperceptível
	cam.rotation = Vector3(sin(_t * 0.71) * 0.0015, sin(_t * 0.53) * 0.0012, sin(_t * 0.9) * 0.0035)
