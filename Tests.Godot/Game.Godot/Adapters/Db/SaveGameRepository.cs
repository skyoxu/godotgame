using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Game.Core.Domain.Entities;
using Game.Core.Ports;
using Game.Core.Repositories;

namespace Game.Godot.Adapters.Db;

public class SaveGameRepository : ISaveGameRepository
{
    private readonly ISqlDatabase _db;
    public SaveGameRepository(ISqlDatabase db) => _db = db;

    public Task UpsertAsync(SaveGame save)
    {
        if (string.IsNullOrEmpty(save.Id)) save.Id = Guid.NewGuid().ToString();
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        if (save.CreatedAt == 0) save.CreatedAt = now;
        save.UpdatedAt = now;

        _db.Execute("INSERT INTO saves(id,user_id,slot_number,data,created_at,updated_at) VALUES(@0,@1,@2,@3,@4,@5) " +
                    "ON CONFLICT(id) DO UPDATE SET user_id=@1, slot_number=@2, data=@3, updated_at=@5;",
            save.Id, save.UserId, save.SlotNumber, save.Data, save.CreatedAt, save.UpdatedAt);
        return Task.CompletedTask;
    }

    public Task<SaveGame?> GetAsync(string userId, int slot)
    {
        var rows = _db.Query("SELECT id,user_id,slot_number,data,created_at,updated_at FROM saves WHERE user_id=@0 AND slot_number=@1 LIMIT 1;", userId, slot);
        if (rows.Count == 0) return Task.FromResult<SaveGame?>(null);
        var r = rows[0];
        var s = new SaveGame
        {
            Id = r["id"]?.ToString() ?? string.Empty,
            UserId = r["user_id"]?.ToString() ?? string.Empty,
            SlotNumber = Convert.ToInt32(r["slot_number"] ?? 0),
            Data = r["data"]?.ToString() ?? "",
            CreatedAt = Convert.ToInt64(r["created_at"] ?? 0),
            UpdatedAt = Convert.ToInt64(r["updated_at"] ?? 0)
        };
        return Task.FromResult<SaveGame?>(s);
    }

    public Task<List<SaveGame>> ListByUserAsync(string userId)
    {
        var rows = _db.Query("SELECT id,user_id,slot_number,data,created_at,updated_at FROM saves WHERE user_id=@0 ORDER BY slot_number;", userId);
        var list = new List<SaveGame>(rows.Count);
        foreach (var r in rows)
        {
            list.Add(new SaveGame
            {
                Id = r["id"]?.ToString() ?? string.Empty,
                UserId = r["user_id"]?.ToString() ?? string.Empty,
                SlotNumber = Convert.ToInt32(r["slot_number"] ?? 0),
                Data = r["data"]?.ToString() ?? "",
                CreatedAt = Convert.ToInt64(r["created_at"] ?? 0),
                UpdatedAt = Convert.ToInt64(r["updated_at"] ?? 0)
            });
        }
        return Task.FromResult(list);
    }
}

