# PyYAML provenance

Selected dependency: **PyYAML 6.0.3**, pure-Python `lib/yaml/` package.

* Upstream: <https://github.com/yaml/pyyaml>
* Immutable commit: `49790e73684bebad1df05ef8d828fa12f685bffb`
* Tag evidence: <https://api.github.com/repos/yaml/pyyaml/git/ref/tags/6.0.3>
* License source: <https://raw.githubusercontent.com/yaml/pyyaml/49790e73684bebad1df05ef8d828fa12f685bffb/LICENSE>
* License: MIT, reproduced without changes in `LICENSE-PyYAML`.
* Source package: <https://github.com/yaml/pyyaml/tree/49790e73684bebad1df05ef8d828fa12f685bffb/lib/yaml>

The upstream tag and full license were read on 2026-10-23. No third-party
mirror, guessed attribution, rewritten parser, compiled extension, network
bootstrap, or ambient site-packages fallback is used.

The 16 pure-Python upstream `lib/yaml/*.py` files are included unchanged at
`vendor/yaml/*.py`. `cyaml.py` (the optional compiled-extension wrapper) is
deliberately excluded; upstream `__init__.py` already falls back to its bundled
pure-Python implementation when that module is absent. No C extension is
included or required. Each file's Git blob SHA-1 was compared with the
immutable upstream GitHub contents API, and the license was compared byte for
byte. `manifest.json` records the upstream blob identities and SHA-256 content
hashes. Tests verify all recorded source bytes and the license offline.
The vendor-local attributes enforce LF and exempt only upstream Python
trailing/end-of-file whitespace from Git whitespace checks, preserving the
original licensed source bytes instead of silently formatting them.

Vendoring is a development-time operation, never a consumer installation step.
The helper explicitly refuses normal operations when the bundle is missing;
it never downloads a replacement or silently imports an ambient parser.

The runtime loads only this bundled package using a private module name.
SafeLoader is further restricted with duplicate-key rejection, no YAML aliases,
and nesting/node/byte limits. Unsafe Python object constructors are unavailable.
