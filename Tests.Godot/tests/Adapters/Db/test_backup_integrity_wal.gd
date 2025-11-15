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

func _force_managed() -> Node:
    var helper = preload("res://Game.Godot/Adapters/Db/DbTestHelper.cs").new()
    add_child(auto_free(helper))
    helper.ForceManaged()
    return helper

func _abs(p: String) -> String:
    return ProjectSettings.globalize_path(p)

func _copy_abs(from_path: String, to_path: String) -> void:
    var rf = FileAccess.open(from_path, FileAccess.ModeFlags.READ)
    var wf = FileAccess.open(to_path, FileAccess.ModeFlags.WRITE)
    wf.store_buffer(rf.get_buffer(rf.get_length()))
    rf.close(); wf.close()

func test_wal_backup_copy_and_reopen_has_same_data() -> void:
    var helper = _force_managed()
    helper.SetEnv("GD_DB_JOURNAL", "WAL")
    var src_user = "user://utdb_%s/backup_src.db" % Time.get_unix_time_from_system()
    var db = await _new_db("SqlDb")
    assert_bool(db.TryOpen(src_user)).is_true()
    db.Execute("CREATE TABLE IF NOT EXISTS t(k TEXT PRIMARY KEY, v INTEGER);")
    db.Execute("INSERT OR REPLACE INTO t(k,v) VALUES(@0,@1);", "alpha", 99)
    await get_tree().process_frame
    var src_abs = _abs(src_user)
    var wal_abs = src_abs + "-wal"
    assert_bool(FileAccess.file_exists(wal_abs)).is_true()
    var dst_abs = src_abs.get_base_dir().path_join("backup_copy.db")
    _copy_abs(src_abs, dst_abs)
    if FileAccess.file_exists(wal_abs):
        _copy_abs(wal_abs, dst_abs + "-wal")
    # reopen backup
    var db2 = await _new_db("SqlDb2")
    assert_bool(db2.TryOpen(ProjectSettings.localize_path(dst_abs))).is_true()
    var rows = db2.Query("SELECT v FROM t WHERE k=@0;", "alpha")
    assert_int(rows.size()).is_equal(1)
    assert_int(int(rows[0]["v"])) .is_equal(99)

