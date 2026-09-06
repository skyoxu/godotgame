extends "res://addons/gdUnit4/src/GdUnitTestSuite.gd"

# ADR-0018: shipped example scenes must load with their C# scripts attached.
func check_example(path: String) -> void:
    var packed := load("res://Game.Godot/Examples/" + path) as PackedScene
    assert_object(packed).is_not_null()
    if packed == null:
        return
    var scene := packed.instantiate()
    assert_object(scene).is_not_null()
    if scene == null:
        return
    auto_free(scene)
    assert_object(scene.get_script()).is_not_null()
    add_child(scene)
    await get_tree().process_frame
    assert_bool(scene.is_inside_tree()).is_true()

func test_event_listener_panel_loads() -> void:
    await check_example("Components/EventListenerPanel.tscn")

func test_modal_loads() -> void:
    await check_example("Components/Modal.tscn")

func test_primary_button_loads() -> void:
    await check_example("Components/PrimaryButton.tscn")

func test_toast_loads() -> void:
    await check_example("Components/Toast.tscn")

func test_demo_screen_loads() -> void:
    await check_example("Screens/DemoScreen.tscn")

func test_combat_panel_loads() -> void:
    await check_example("UI/CombatPanel.tscn")

func test_inventory_panel_loads() -> void:
    await check_example("UI/InventoryPanel.tscn")

func test_score_panel_loads() -> void:
    await check_example("UI/ScorePanel.tscn")
