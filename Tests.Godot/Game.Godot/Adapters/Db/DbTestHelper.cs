using System;
using Godot;

namespace Game.Godot.Adapters.Db;

public partial class DbTestHelper : Node
{
    public void ForceManaged()
    {
        System.Environment.SetEnvironmentVariable("GODOT_DB_BACKEND", "managed");
    }

    private SqliteDataStore GetDb()
    {
        var db = GetNodeOrNull<SqliteDataStore>("/root/SqlDb");
        if (db == null) throw new InvalidOperationException("SqlDb not found at /root/SqlDb");
        return db;
    }

    public void CreateSchema()
    {
        var db = GetDb();
        db.Execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at INTEGER, last_login INTEGER);");
        db.Execute("CREATE TABLE IF NOT EXISTS saves (id TEXT PRIMARY KEY, user_id TEXT, slot_number INTEGER, data TEXT, created_at INTEGER, updated_at INTEGER);");
        db.Execute("CREATE TABLE IF NOT EXISTS inventory_items (user_id TEXT, item_id TEXT, qty INTEGER, updated_at INTEGER, PRIMARY KEY(user_id, item_id));");
    }

    public void ClearAll()
    {
        var db = GetDb();
        try { db.Execute("DELETE FROM inventory_items;"); } catch { }
        try { db.Execute("DELETE FROM saves;"); } catch { }
        try { db.Execute("DELETE FROM users;"); } catch { }
    }
}

