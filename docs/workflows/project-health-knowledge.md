# Project Health: Knowledge + Impact

`serve-project-health` now serves the existing health dashboard and a loopback-only `/knowledge/` page from the same `127.0.0.1` process.

The page supports repository scan, deterministic knowledge search, Impact exploration and local source configuration. A fresh template intentionally has no business task records; empty task/runtime state is valid and must not be replaced with sibling-repository examples.

Security boundaries:

- bind only `127.0.0.1`;
- reject unexpected Host headers;
- writes require same-origin `Origin` plus an in-memory session token;
- JSON requests are bounded;
- no arbitrary command execution endpoint exists;
- Impact keyword matches are evidence only, not confirmed dependency edges.

Formal Chapter 6 and Review handoffs still use candidate preparation, explicit decisions, frozen context, Impact output and handoff validation. The browser page is an investigation surface, not a replacement for those contracts.
