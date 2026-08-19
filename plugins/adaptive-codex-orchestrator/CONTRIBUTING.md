# Contributing

Thank you for improving Adaptive Codex Orchestrator. This is an independent
community project and is not affiliated with or endorsed by OpenAI.

## Before starting

Read:

- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Privacy](docs/PRIVACY.md)
- [Compatibility](docs/COMPATIBILITY.md)
- [Testing](docs/TESTING.md)

Check repository-level contributor instructions before editing. Discuss a
change first when it would alter public behavior, state schema, command
semantics, hook trust, model policy, permission boundaries, privacy, or
platform support.

## Design invariants

Contributions must preserve these defaults:

1. The parent owns requirements, architecture, delegation judgment,
   integration, final validation, and the final answer.
2. Delegation is optional and limited to bounded, reversible, independently
   verifiable work.
3. The plugin does not change model selection, reasoning level, sandbox,
   approvals, permissions, or Codex global configuration.
4. Runtime state stays under `PLUGIN_DATA`; project source and raw paths are not
   persisted.
5. The control plane makes no external network request and stores no prompt,
   transcript, or source code.
6. Worker-model use is reported only to the strength supported by host evidence.
7. Disabled mode preserves ordinary Codex behavior.

## Development setup

The runtime and tests should use the Python standard library. Use a supported
Python interpreter and do not add a runtime dependency without a concrete,
documented need and maintainer agreement.

From the plugin root, run:

```text
python -m unittest discover -s tests -p "test_*.py" -v
python -m compileall -q hooks tests
```

See [Testing](docs/TESTING.md) for validators, hook simulations, policy evals,
manual flows, and cross-platform expectations.

## Making a change

- Keep changes small and scoped to the confirmed requirement.
- Preserve useful existing architecture and avoid unrelated cleanup.
- Use deterministic code for control behavior; do not add an LLM parser.
- Validate all external and persisted data at the boundary.
- Use `pathlib`/standard-library path handling and `shell=False` subprocesses.
- Add focused regression tests for behavior changes.
- Update architecture, compatibility, security, privacy, terms, testing, and
  changelog entries when the corresponding contract changes.
- Never commit machine-specific absolute paths, credentials, prompts,
  transcripts, proprietary code, generated user patches, or private fixtures.

## Command-language changes

A new alias or parser rule needs positive and negative fixtures in Korean and
English where applicable. Test quoted/fenced/incidental text, conflict
resolution, Unicode normalization, mixed command+task behavior, and state non-
mutation on ambiguity. Do not broaden matching merely to improve a happy-path
example.

## State and hook changes

State changes require a schema version/migration path, deterministic
serialization, backup/recovery behavior, cleanup tests, and privacy review.
Hook changes must use current official event and output shapes, remain fast,
emit safe JSON, preserve normal behavior on failure, and never use permissions
or blocking Stop decisions to force orchestration.

## Model and routing changes

Keep model names in the central policy. Verify the current official slug and
supported reasoning fields before changing it. Preserve requested versus host-
reported model distinctions, retry limits, parent fallback, writer caps, and
default prohibition on nested delegation.

## Pull-request checklist

- [ ] Scope and user-visible behavior are explained.
- [ ] Relevant offline tests pass with exact counts/results.
- [ ] Plugin, skill, JSON, hook, and link validation relevant to the change pass.
- [ ] Windows, macOS, and Linux effects were tested or explicitly documented.
- [ ] Security and privacy impact was reviewed.
- [ ] Documentation and changelog are current.
- [ ] No unrelated files, secrets, private data, or false capability claims are
      included.
- [ ] Publication, deployment, marketplace installation, or external writes are
      not performed without explicit owner authorization.

## Security reports

Do not open a public issue containing exploit details or sensitive data. Follow
the private process in [Security](docs/SECURITY.md).

## Licensing and branding

By contributing, you agree that your contribution may be distributed under the
[MIT License](LICENSE) and that you have the right to submit it. Use original
assets and avoid branding that suggests official OpenAI affiliation. Do not add
OpenAI/ChatGPT logos or copied Codex artwork.
