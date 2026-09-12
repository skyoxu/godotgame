# Repository Knowledge Control Plane

`knowledge/**` is the machine-consumption control plane. It stores contracts, policies and generated publication pointers; it does not own repository facts.

Authoritative facts stay in source code, Taskmaster, PRD/GDD, ADR/Base/Overlay, contracts and reviewed `docs/knowledge/**` resource entries.

Consumers: `repository-session`, `chapter4`, `chapter5`, `chapter6`, `review`.

The template starts without a publication. Build/locate/prepare operations may run with no task data; freeze and formal Impact handoff remain explicit, revision-bound operations.
