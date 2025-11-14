extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func _new_db(name: String) -> Node:
    var db = preload("res://Game.Godot/Adapters/SqliteDataStore.cs").new()
    db.name = name
    get_tree().get_root().add_child(auto_free(db))
    return db

static func _copy_file(src: String, dst: String) -> bool:
    DirAccess.make_dir_recursive(dst.get_base_dir())
    var r = FileAccess.open(src, FileAccess.READ)
    if r == null:
        return false
    var data = r.get_buffer(r.get_length())
    var w = FileAccess.open(dst, FileAccess.WRITE)
    if w == null:
        return false
    w.store_buffer(data)
    return true

func test_backup_restore_inventory() -> void:
    var path = "user://utdb_%s/inv_bak.db" % Time.get_unix_time_from_system()
    var db = _new_db("SqlDb")
    var ok = db.TryOpen(path)
    assert_bool(ok).is_true()
    var helper = preload("res://Game.Godot/Adapters/Db/DbTestHelper.cs").new()
    add_child(auto_free(helper))
    helper.CreateSchema()
    helper.ClearAll()

    var inv = preload("res://Game.Godot/Adapters/Db/InventoryRepoBridge.cs").new()
    add_child(auto_free(inv))
    assert_bool(inv.Add("potion", 3)).is_true()
    assert_bool(inv.Add("elixir", 2)).is_true()

    # close and copy to backup
    db.Close()
    await get_tree().process_frame
    var backup_dir = "user://backup_%s" % Time.get_unix_time_from_system()
    var backup_path = "%s/%s" % [backup_dir, path.get_file()]
    assert_bool(_copy_file(path, backup_path)).is_true()

    # open from backup and verify items present
    var ok2 = db.TryOpen(backup_path)
    assert_bool(ok2).is_true()
    var inv2 = preload("res://Game.Godot/Adapters/Db/InventoryRepoBridge.cs").new()
    add_child(auto_free(inv2))
    var items = inv2.All()
    var ok_p := false
    var ok_e := false
    for s in items:
        if str(s).find("potion:3") != -1:
            ok_p = true
        if str(s).find("elixir:2") != -1:
            ok_e = true
    assert_bool(ok_p and ok_e).is_true()

