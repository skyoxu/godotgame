# Taskmaster Test Isolation

Purpose: prevent tests from mutating repo-global `.taskmaster/tasks` state and causing cross-test or cross-run contamination.

## Hard Rule

- Tests must not rename, replace, delete, or overwrite the repo-global `.taskmaster/tasks` directory.
- Tests must not treat the real repository root as a writable sandbox for task triplet fixtures.
- If a test needs custom `tasks.json`, `tasks_back.json`, or `tasks_gameplay.json`, it must stage them in a temporary directory and inject paths explicitly.

## Required Pattern

1. Create a temporary directory.
2. Write `tasks.json`, `tasks_back.json`, and `tasks_gameplay.json` into that temporary directory.
3. Pass those paths through one of these mechanisms:
   - `SC_TASKMASTER_TASKS_JSON_PATH`
   - `SC_TASKMASTER_TASKS_BACK_PATH`
   - `SC_TASKMASTER_TASKS_GAMEPLAY_PATH`
   - or explicit CLI flags such as `--tasks-json-path`, `--tasks-back-path`, `--tasks-gameplay-path`
4. Restore environment variables after the test finishes.

## Subprocess Rule

If a test launches a subprocess with `cwd` pointing at the real repository root and the subprocess needs task triplet data, the test must still inject temporary triplet paths through environment variables or explicit CLI flags.

Running from the real repo root does not permit writing `.taskmaster/tasks` directly.

## Allowed Cases

- Read-only tests that inspect the real repository's existing `.taskmaster/tasks` files without modifying them.
- Tests that construct a temporary repo root under `TemporaryDirectory()` and write `.taskmaster/tasks` only inside that temporary repo.
- Tests that use helper fixtures which stage triplet files outside the real repo and expose them through environment overrides.

## Forbidden Patterns

- Renaming `.taskmaster/tasks` to a backup directory and restoring it later.
- Writing fixture payloads into the real `.taskmaster/tasks` directory, even temporarily.
- Assuming that a missing task-scoped filter should fall through to a full-suite run.
- Mixing `cwd=<real repo root>` with hardcoded reads from `REPO_ROOT / '.taskmaster' / 'tasks' / ...` when the test already staged a temporary triplet.

## Review Checklist

Before merging any test that touches task triplet data, verify all of the following:

- The test does not mutate the real `.taskmaster/tasks` directory.
- Any temporary triplet data is created outside the real repo root unless the entire repo root itself is temporary.
- Subprocess tests pass the intended triplet paths explicitly.
- Cleanup restores environment overrides.
- Task-scoped unit tests fail fast when no task-scoped C# refs resolve; they must not silently expand to a full-suite run.

## Reference

- `scripts/sc/tests/_taskmaster_fixture.py` is the approved fixture pattern for staging task triplets in a temporary directory and injecting them through environment variables.
- `scripts/sc/_taskmaster_paths.py` is the default path resolver and honors the `SC_TASKMASTER_*` overrides.
