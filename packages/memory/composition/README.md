# Memory composition

Author the helper and its data only in the canonical `runtime/`, `vendor/`,
`contracts/`, `templates/`, `skills/`, and `references/` directories.
`python scripts/build_memory_package.py` copies those bytes into both Memory
platform plugins and the Software Team Copilot plugin. No install-time symlinks,
sibling-package imports, transitive plugin installation, network calls, or
consumer dependency installation are required.

Each install root contains `skills/` and a private
`memory/{runtime,vendor,contracts,templates,references}/` payload. Existing
Software Team `contracts/` and `skills/st-*/` remain separately owned.
The generated `.memory-package.json` inventories every copied file by SHA-256;
its plugin version is independent of store schema version 1 and OKF 0.2.
Unknown files and locally edited generated files are never overwritten.

Copilot install roots also require an authored root `plugin.json`, separate
from the copied-payload inventory and marketplace catalog. The build command
checks its name, version and component paths against the catalog. These use the
[legacy Copilot manifest format](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
with explicit `skills/` and, for Software Team, `agents/`; adding an Agent Plugins
`$schema` would change layout semantics and requires a deliberate migration.

Use `--output-root <temporary-directory>` to stage initial builds away from the
checkout, and `--check` to detect drift without changing files. Rebuild after
editing canonical sources; commit the canonical and generated changes together.

`mirrors.json` is generated from the canonical skills and explicitly permits
only the named Memory/Software Team pairs to share a repository mirror. The
mirror script checks byte identity before choosing Memory as the canonical
source. Every other artifact-name collision remains an error.
