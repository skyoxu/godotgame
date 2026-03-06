namespace Game.Core.Contracts.Guild;

/// <summary>
/// Domain event: core.guild.member.joined
/// Description: Emitted when a user joins a guild.
/// </summary>
/// <remarks>
/// ADR refs: ADR-0004, ADR-0031.
/// Overlay ref: docs/architecture/overlays/PRD-Guild-Manager/08/08-Contracts-Guild-Manager-Events.md
/// </remarks>
public sealed record GuildMemberJoined(
    string UserId,
    string GuildId,
    System.DateTimeOffset JoinedAt,
    string Role // member | admin
)
{
    public const string EventType = "core.guild.member.joined";
}

