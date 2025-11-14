extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func _db() -> Node:
    var db = preload("res://Game.Godot/Adapters/SqliteDataStore.cs").new()
    db.name = "SqlDb"
    get_tree().get_root().add_child(auto_free(db))
    return db

func test_try_open_user_path_should_succeed() -> void:
    var db = _db()
    var p = "user://utdb_%d/game.db" % Time.get_unix_time_from_system()
    var ok = db.TryOpen(p)
    assert_bool(ok).is_true()
    # Create a temp table and verify it exists
    db.Execute("CREATE TABLE IF NOT EXISTS tmp_ut(id INTEGER PRIMARY KEY);")
    assert_bool(db.TableExists("tmp_ut")).is_true()
    # File should exist under user://
    assert_bool(FileAccess.file_exists(p)).is_true()

func test_try_open_absolute_path_should_fail() -> void:
    var db = _db()
    var p = "C:/temp/evil.db"
    var ok = db.TryOpen(p)
    assert_bool(ok).is_false()
    assert_str(str(db.LastError)).to_lower().contains("user://")

func test_try_open_traversal_should_fail() -> void:
    var db = _db()
    var p = "user://../evil.db"
    var ok = db.TryOpen(p)
    assert_bool(ok).is_false()
    assert_str(str(db.LastError)).to_lower().contains("not allowed")
