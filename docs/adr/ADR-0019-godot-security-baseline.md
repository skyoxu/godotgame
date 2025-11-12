# ADR-0019: Godot Security Baseline

- Status: Proposed
- Context: Migration Phase-2; replaces Electron-specific ADR-0002 baseline with Godot-focused rules; ties to CH02 security posture
- Decision: Enforce res:// (read-only) and user:// (read/write) path constraints; only HTTPS external links with allowlist; disable runtime dynamic code loading; initialize Sentry Godot SDK early for release health; provide security smoke tests in CI
- Consequences: Any absolute or traversal path is denied; all URL opens must go through Security adapter; HTTP requests constrained by allowlist and offline mode; editor-only plugins excluded from release exports
- References: docs/migration/Phase-14-Godot-Security-Baseline.md, docs/architecture/base/02-security-baseline-electron-v2.md

