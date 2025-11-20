extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func _new_db(name: String) -> Node:
	var db: Node = null
    if ClassDB.class_exists("SqliteDataStore"):
        db = ClassDB.instantiate("SqliteDataStore")
    else:
        var s = load("res://Game.Godot/Adapters/SqliteDataStore.cs")
        db = Node.new()
        db.set_script(s)
    db.name = name
    get_tree().get_root().add_child(auto_free(db))
    await get_tree().process_frame
    if not db.has_method("TryOpen"):
        await get_tree().process_frame
    return db


func _today_dir() -> String:
    var d = Time.get_datetime_dict_from_system()
    return "%04d-%02d-%02d" % [d.year, d.month, d.day]


func _audit_path() -> String:
    return "res://logs/ci/%s/security-audit.jsonl" % _today_dir()


func _remove_audit_file() -> void:
    var p := _audit_path()
    if FileAccess.file_exists(p):
        var abs := ProjectSettings.globalize_path(p)
        DirAccess.remove_absolute(abs)


func test_open_denied_writes_audit_log() -> void:
    _remove_audit_file()

    var db = await _new_db("DbAuditOpenFail")
    var ok := db.TryOpen("C:/temp/security_open_denied.db")
    assert_bool(ok).is_false()

    await get_tree().process_frame

    var p := _audit_path()
    assert_bool(FileAccess.file_exists(p)).is_true()

    var txt := FileAccess.get_file_as_string(p)
    assert_str(txt).is_not_empty()

    var lines := txt.split("\n", false)
    var last := ""
    for i in range(lines.size() - 1, -1, -1):
        var l := lines[i].strip_edges()
        if l != "":
            last = l
            break

    assert_str(last).is_not_empty()
    var obj = JSON.parse_string(last)
    assert_that(obj).is_not_null()
    assert_str(str(obj["action"])).is_equal("db.open.fail")
