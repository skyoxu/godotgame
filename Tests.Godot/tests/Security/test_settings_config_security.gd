extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func test_settings_configfile_path_security() -> void:
    var cfg = ConfigFile.new()
    cfg.set_value("s", "k", "v")
    # allow: user://
    var ok = cfg.save("user://ok_settings.cfg")
    assert_int(ok).is_equal(0)

    # deny: absolute path
    var abs = cfg.save("C:/temp/bad_settings.cfg")
    assert_bool(abs != 0).is_true()

    # deny: traversal
    var trav = cfg.save("user://../bad_settings.cfg")
    assert_bool(trav != 0).is_true()

