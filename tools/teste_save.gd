extends SceneTree
## Save: gravação atômica, save incompleto e save corrompido não quebram o "Continuar".
## Uso: godot --headless --path . --script res://tools/teste_save.gd   (sai com código 1 se falhar)

func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var st = root.get_node("Story")
	var path: String = st.SAVE
	var backup := FileAccess.get_file_as_string(path) if FileAccess.file_exists(path) else ""
	st.index = 4
	st.truth = 2
	st.save_game()
	assert(FileAccess.file_exists(path) and not FileAccess.file_exists(path + ".tmp"))
	assert(int(JSON.parse_string(FileAccess.get_file_as_string(path))["truth"]) == 2)
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string('{"index": 3}')                                           # save antigo: só o índice
	f.close()
	st.continue_game()
	await process_frame
	assert(st.index == 3 and st.truth == 0 and st.trust["boris"] == 0)
	f = FileAccess.open(path, FileAccess.WRITE)
	f.store_string('{"index": 3, "tru')                                      # corrompido
	f.close()
	st.continue_game()
	await process_frame
	assert(st.index == 0)
	if backup != "":
		f = FileAccess.open(path, FileAccess.WRITE)
		f.store_string(backup)
	else:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	print("SAVE OK")
	quit()
