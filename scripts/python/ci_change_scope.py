"""Select expensive runtime checks conservatively (ADR-0005)."""
import os
import subprocess
from pathlib import Path


def needs_runtime(paths):
    # Only known documentation-only changes may skip runtime. Unknown files run it.
    return any(not ((p.endswith('.md') and (p.startswith('docs/') or '/' not in p)) or (p.startswith('docs/') and p.endswith(('.txt', '.svg', '.png', '.jpg')))) for p in paths)


def needs_export(paths):
    return any(p.startswith(('.github/workflows/', '.github/actions/', 'scripts/ci/')) or
               p.endswith(('.csproj', '.sln', 'export_presets.cfg', 'project.godot')) for p in paths)


def main():
    base = os.environ.get('CI_BASE_SHA', '')
    event = os.environ.get('CI_EVENT', '')
    runtime = True
    export = True
    if event in {'pull_request', 'push'} and base and set(base) != {'0'}:
        result = subprocess.run(['git', 'diff', '--name-only', '-z', base, 'HEAD'], capture_output=True, check=False)
        if result.returncode == 0:
            paths = [p for p in result.stdout.decode('utf-8').split('\0') if p]
            runtime = needs_runtime(paths)
            export = needs_export(paths)
    value = str(runtime).lower()
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as f:
        f.write(f'runtime={value}\nexport={str(export).lower()}\n')
    print(f'CI_SCOPE runtime={value}')


if __name__ == '__main__':
    main()
