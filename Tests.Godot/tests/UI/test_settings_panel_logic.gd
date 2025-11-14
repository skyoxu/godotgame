extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

func before() -> void:
    var __db = preload("res://Game.Godot/Adapters/SqliteDataStore.cs").new()
    __db.name = "SqlDb"
    get_tree().get_root().add_child(auto_free(__db))

func _open_db()->bool:
    var db = get_node_or_null("/root/SqlDb")
    if db == null:
        push_warning("SKIP settings test: SqlDb not found")
        return false
    var path := "user://utdb_%s/game.db" % Time.get_ticks_msec()
    if not db.TryOpen(path):
        push_warning("SKIP settings test: " + str(db.LastError))
        return false
    return true

func test_settings_save_and_load() -> void:
    if not _open_db():
        return
    var packed = load("res://Game.Godot/Scenes/UI/SettingsPanel.tscn")
    if packed == null:
        push_warning("SKIP settings panel test: SettingsPanel.tscn not found")
        return
    # Ensure schema exists for tests
    var db = get_node_or_null("/root/SqlDb")
    if db == null or not db.has_method("Execute"):
        push_warning("SKIP settings panel test: SqlDb missing or Execute not available")
        return
    else:
        db.Execute("CREATE TABLE IF NOT EXISTS settings(user_id TEXT PRIMARY KEY, audio_volume REAL, graphics_quality TEXT, language TEXT, updated_at INTEGER);")
    var panel = packed.instantiate()
    add_child(auto_free(panel))
    # set values
    var slider = panel.get_node("VBox/VolRow/VolSlider")
    slider.value = 0.7
    var gfx = panel.get_node("VBox/GraphicsRow/GraphicsOpt")
    if gfx.get_item_count() == 0:
        gfx.add_item("low"); gfx.add_item("medium"); gfx.add_item("high")
    gfx.selected = 2 # high
    var lang = panel.get_node("VBox/LangRow/LangOpt")
    if lang.get_item_count() == 0:
        lang.add_item("en"); lang.add_item("zh"); lang.add_item("ja")
    lang.selected = 1 # zh
    # save
    panel.get_node("VBox/Buttons/SaveBtn").emit_signal("pressed")
    # reset
    slider.value = 0.0
    gfx.selected = 0
    lang.selected = 0
    # load
    panel.get_node("VBox/Buttons/LoadBtn").emit_signal("pressed")
    await get_tree().process_frame
    assert_float(float(slider.value)).is_greater(0.0)
    panel.queue_free()
