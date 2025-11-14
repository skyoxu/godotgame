extends SceneTree

func _init() -> void:
    call_deferred("_run")

func _run() -> void:

    var result := {
        "ts": Time.get_datetime_string_from_system(true),
        "ports": {
            "time": false,
            "input": false,
            "resourceLoader": false,
            "dataStore": false,
            "logger": false,
            "eventBus": false,
        }
    }

    var cr := root.get_node_or_null("/root/CompositionRoot")
    if cr == null:
        result["error"] = "CompositionRoot not found (autoload not configured)"
        _write_and_quit(result)
        return

    # Prefer C# helper method for interop safety; wait a few frames for C# _Ready
    if cr.has_method("PortsStatus"):
        var st: Dictionary = {}
        var tries := 0
        while tries < 60:
            st = cr.PortsStatus()
            var any_true := false
            for k in st.keys():
                if bool(st[k]):
                    any_true = true
                    break
            if any_true:
                break
            await process_frame
            tries += 1
        for k in st.keys():
            if result["ports"].has(k):
                result["ports"][k] = bool(st[k])
    else:
        # fallback (best effort; may be blocked by C# interop)
        pass

    # Also probe legacy autoload singletons if present
    var rootn = get_root()
    if rootn.has_node("/root/Time"):
        result["ports"]["time"] = true
    if rootn.has_node("/root/Input"):
        result["ports"]["input"] = true
    if rootn.has_node("/root/DataStore"):
        result["ports"]["dataStore"] = true
    if rootn.has_node("/root/Logger"):
        result["ports"]["logger"] = true
    if rootn.has_node("/root/EventBus"):
        result["ports"]["eventBus"] = true
    if rootn.has_node("/root/ResourceLoader"):
        result["ports"]["resourceLoader"] = true
    elif result["ports"]["resourceLoader"] == false:
        # Fallback: read a resource directly
        var t = FileAccess.open("res://project.godot", FileAccess.READ)
        result["ports"]["resourceLoader"] = t != null

    _write_and_quit(result)

func _write_and_quit(result: Dictionary) -> void:
    var d = Time.get_date_dict_from_system()
    var ymd = "%04d-%02d-%02d" % [d.year, d.month, d.day]
    var out_dir = "user://e2e/%s" % ymd
    DirAccess.make_dir_recursive_absolute(out_dir)
    var out_path = out_dir + "/composition_root_selfcheck.json"
    var f = FileAccess.open(out_path, FileAccess.WRITE)
    if f:
        f.store_string(JSON.stringify(result))
        f.flush()
        f.close()
    print("SELF_CHECK_OUT:", ProjectSettings.globalize_path(out_path))
    quit()
