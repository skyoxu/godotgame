using System;
using Godot;

namespace Game.Godot.Adapters.Db;

public partial class DbTestHelper : Node
{
    public void ForceManaged()
    {
        System.Environment.SetEnvironmentVariable("GODOT_DB_BACKEND", "managed");
        System.Environment.SetEnvironmentVariable("GD_DB_JOURNAL", "DELETE");
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
        // Core domain tables
        db.Execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at INTEGER, last_login INTEGER);");
        db.Execute("CREATE TABLE IF NOT EXISTS saves (id TEXT PRIMARY KEY, user_id TEXT, slot_number INTEGER, data TEXT, created_at INTEGER, updated_at INTEGER);");
        db.Execute("CREATE TABLE IF NOT EXISTS inventory_items (user_id TEXT, item_id TEXT, qty INTEGER, updated_at INTEGER, PRIMARY KEY(user_id, item_id));");
        // Schema versioning meta (single row id=1)
        db.Execute("CREATE TABLE IF NOT EXISTS schema_version (id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL);");
        db.Execute("INSERT OR IGNORE INTO schema_version(id,version) VALUES(1,1);");
    }

    public void ClearAll()
    {
        var db = GetDb();
        try { db.Execute("DELETE FROM inventory_items;"); } catch { }
        try { db.Execute("DELETE FROM saves;"); } catch { }
        try { db.Execute("DELETE FROM users;"); } catch { }
    }

    public int GetSchemaVersion()
    {
        var db = GetDb();
        try
        {
            var rows = db.Query("SELECT version FROM schema_version WHERE id=1;");
            if (rows.Count == 0) return -1;
            var v = rows[0]["version"];
            if (v == null) return -1;
            return Convert.ToInt32(v);
        }
        catch
        {
            return -1;
        }
    }

    public void SetEnv(string key, string value)
    {
        System.Environment.SetEnvironmentVariable(key, value);
    }
}
