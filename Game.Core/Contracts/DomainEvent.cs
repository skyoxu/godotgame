namespace Game.Core.Contracts;

/// <summary>
/// Canonical domain event envelope used by adapters and event transport boundaries.
/// </summary>
/// <remarks>
/// ADR refs: ADR-0004, ADR-0031.
/// Overlay ref: docs/architecture/overlays/PRD-Guild-Manager/08/08-Contracts-CloudEvent.md
/// </remarks>
public record DomainEvent(
    string Type,
    string Source,
    object? Data,
    DateTime Timestamp,
    string Id,
    string SpecVersion = "1.0",
    string DataContentType = "application/json"
);
