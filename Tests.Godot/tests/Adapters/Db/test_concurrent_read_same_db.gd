extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func _new_db(name: String) -> Node:
    var db = null
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

func _force_managed() -> void:
    var helper = preload("res://Game.Godot/Adapters/Db/DbTestHelper.cs").new()
    add_child(auto_free(helper))
    helper.ForceManaged()

func test_concurrent_read_after_write_commit() -> void:
    var path = "user://utdb_%s/concurrent.db" % Time.get_unix_time_from_system()
    _force_managed()
    var a = await _new_db("SqlDbA")
    var b = await _new_db("SqlDbB")
    assert_bool(a.TryOpen(path)).is_true()
    assert_bool(b.TryOpen(path)).is_true()
    a.Execute("CREATE TABLE IF NOT EXISTS t(k TEXT PRIMARY KEY, v INTEGER);")
    a.Execute("INSERT OR REPLACE INTO t(k,v) VALUES(@0,@1);", "key", 7)
    await get_tree().process_frame
    var rows = b.Query("SELECT v FROM t WHERE k=@0;", "key")
    assert_int(rows.size()).is_equal(1)
    assert_int(int(rows[0]["v"])) .is_equal(7)

