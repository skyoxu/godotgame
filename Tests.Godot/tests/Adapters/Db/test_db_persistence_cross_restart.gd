extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func _new_db(name: String) -> Node:
    var db = preload("res://Game.Godot/Adapters/SqliteDataStore.cs").new()
    db.name = name
    get_tree().get_root().add_child(auto_free(db))
    return db

func test_cross_restart_persists_rows() -> void:
    # unique DB path per run
    var path = "user://utdb_%s/persist.db" % Time.get_unix_time_from_system()
    # first open and write
    var db1 = _new_db("SqlDb1")
    var ok1 = db1.TryOpen(path)
    assert_bool(ok1).is_true()
    # create temp table and insert one row
    db1.Execute("CREATE TABLE IF NOT EXISTS ut_persist(id INTEGER PRIMARY KEY, v INTEGER);")
    db1.Execute("INSERT INTO ut_persist(id,v) VALUES(1,123);")
    # close first instance
    db1.Close()
    await get_tree().process_frame
    
    # reopen same path with a fresh instance
    var db2 = _new_db("SqlDb2")
    var ok2 = db2.TryOpen(path)
    assert_bool(ok2).is_true()
    var rows = db2.Query("SELECT v FROM ut_persist WHERE id=@0;", 1)
    # rows is an array-like collection; accept >=1 rows and contain 123 when stringified
    assert_int(int(rows.size())).is_greater_or_equal(1)
    var found = false
    for r in rows:
        var s = str(r)
        if s.find("123") != -1:
            found = true
            break
    assert_bool(found).is_true()
