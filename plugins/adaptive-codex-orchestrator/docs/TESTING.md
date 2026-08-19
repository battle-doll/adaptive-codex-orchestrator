# Testing

The latest local execution evidence is recorded in
[Validation](VALIDATION.md).

## Testing principles

- Tests run offline and use Python's standard-library `unittest` framework.
- Fixtures are deterministic and contain no user prompts, source code, secrets,
  or machine-specific absolute paths.
- Each result must record the exact command, test count, pass/fail outcome, and
  relevant platform. Do not claim a validation passed unless it ran and passed.
- Tests isolate `PLUGIN_DATA`, sessions, projects, and working directories in
  temporary locations.

Run commands from the plugin root unless a command says otherwise. Use the
platform's supported Python launcher in place of `python` when necessary.

## Unit tests

Run the complete offline suite:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

Run a focused module while developing:

```text
python -m unittest tests.test_command_parser -v
python -m unittest tests.test_state_store -v
python -m unittest tests.test_project_identity -v
python -m unittest tests.test_hooks -v
```

Compile Python without importing the hook runtime:

```text
python -m compileall -q hooks tests
```

### Command parser coverage

Tests must cover every required Korean and English session/one-shot/project/
global enable, generic/project/global disable, explicit negative, status, and
profile phrase. They must also cover enable+disable conflict, status containing
enable-like text, quotes, fenced code, incidental long text, mixed control and
real work, Korean Unicode variants, repeated whitespace, English case, active
and inactive unanchored referential ambiguity, explicit skill-invocation
context, generic non-orchestration mode/profile phrases, unknown profile,
conflicting scopes, empty input, and invalid Unicode where practical.

Assert structured intent, scope, profile, confidence, ambiguity reason, and
remaining-task flag, plus no state mutation for status or ambiguity.

### State coverage

Cover default OFF, global/project/session/one-shot overrides, independent
enable/profile precedence, one-shot restoration, session cleanup, project and
global persistence, atomic replace, malformed recovery and backup, migration,
concurrent access, missing/read-only storage, deterministic JSON, permissions
where testable, absence of raw paths, and isolation between projects/sessions.

### Project identity coverage

Cover Git root, nested repository directory, non-Git directory, missing Git,
timeout, Windows/POSIX path inputs, platform case behavior, stable SHA-256, and
proof that no raw path is persisted. Mock external process boundaries where
needed so the suite remains deterministic and offline.

## Hook simulations

All currently supported events use JSON fixtures. The hook entry point consumes
one JSON object on standard input and emits one current-schema JSON object on
standard output. Fixture tests must cover:

- Disabled/enabled session start and compact restart.
- Enable-only, enable+task, one-shot enable+task, status, disable, and profile.
- Active/inactive ordinary requests, ambiguity, compact-policy revision
  de-duplication, and reinjection after a packaged revision change.
- Confirmed Spark, confirmed non-Spark, and unavailable worker model.
- Exact six-field worker context, nested-delegation prohibition, and separation
  of requested from host-confirmed model facts.
- Request-completion and session cleanup.
- Missing environment/data directory, invalid stdin JSON, unknown event, and
  unsupported schema version.
- Once-per-session compatibility notice.

Validate output shape against the current hook contract in addition to JSON
syntax. A test that only proves output is parseable is not a schema validation.

For a manual POSIX simulation using a committed fixture:

```text
python hooks/runtime.py < tests/fixtures/<event>.json
```

For PowerShell:

```text
Get-Content -Raw tests/fixtures/<event>.json | python hooks/runtime.py
```

Replace `<event>` with an actual committed fixture name; placeholders are not
commands to report as executed.

## Policy evals

`evals/prompts.jsonl` is an offline decision dataset. It currently includes 31
required scenarios: trivial edit, one focused file, parallel read exploration,
five independent modules, overlapping writes, architecture, authentication,
database migration, test failure, narrow bug, ambiguous incident, Spark
unavailable/rate-limited, unsupported explicit selection, enable+task, disabled
mode, non-Sol parent, multimodal work, oversized context, missing evidence,
conflicting conclusions, scope expansion, nested delegation, and fast-profile
disjoint/overlapping writes, plus explicit user caps zero/one, no broad parent
duplication, the exact six-field result, and requested-versus-confirmed model
facts.

Each record includes the prompt/scenario, expected delegation decision, worker
count range, role, writer count, parent responsibility, fallback, and safety
behavior. Evaluation checks deterministic policy expectations; it must not make
a network model request or present subjective model output as a unit-test pass.
Checks must enforce one concurrent writer in every profile, no nested
delegation, one spawn attempt with parent return and no host-default substitute,
and canonical task-aware caps of zero, one, or two where applicable. Profile
ceilings of two/four/six remain upper bounds, not fan-out targets.

## JSON and metadata checks

Validate syntax for each committed JSON file, including:

```text
python -m json.tool .codex-plugin/plugin.json
python -m json.tool hooks/hooks.json
python -m json.tool skills/adaptive-orchestration/references/model-policy.json
```

Parse every nonblank line of `evals/prompts.jsonl` with the repository's offline
test; `json.tool` validates one JSON document and is not a JSONL validator.

## Plugin and skill validation

Use the installed current validator rather than inventing manifest fields:

```text
python <plugin-creator-skill-root>/scripts/validate_plugin.py <plugin-root>
python <skill-creator-skill-root>/scripts/quick_validate.py skills/adaptive-orchestration
```

Record the resolved validator version/path in release evidence without
committing a developer-specific absolute path. The installed general plugin
validator does not validate the marketplace, full hook schema, starter-prompt
limits, exact PNG dimensions, or every submission-form constraint. The
repository package validator covers the marketplace, prompt, PNG, policy-link,
and reviewer-case checks; official upload scanning and clean installation are
still required.

## Manual test flow

Use a disposable repository and plugin-data directory:

1. Install from the configured GitHub or local marketplace and begin a new
   Codex task.
2. Confirm an ordinary disabled prompt injects no orchestration context.
3. Enable the session, request status, and verify the factual fields.
4. Send a mixed one-shot enable+task; confirm same-turn activation and cleanup.
5. Create project ON, issue a generic session OFF, and confirm the project
   preference remains for a later session.
6. Change conservative/balanced/fast profiles and confirm that the profile
   ceiling is further reduced by user, host, useful-task, and zero/one/two
   task-specific caps; every profile still permits only one concurrent writer.
7. Test an ambiguous command, quoted example, and fenced example; state must not
   change.
8. Test compatibility mode with a non-Sol or unavailable parent identifier.
9. Confirm compact policy delivery on active session start, compaction, enable,
   and profile change; then confirm the same numeric policy revision is omitted
   on later ordinary active turns.
10. Exercise a bounded delegation when supported. Confirm detailed references
    are loaded once only after selection, Spark receives one spawn attempt, and
    failure returns to the parent without retry or host-default substitution.
11. Require the exact six-field worker result, distinguish requested and
    confirmed models, and confirm parent spot-checking does not repeat the same
    broad exploration.
12. End the session and confirm only session/one-shot entries are removed.
13. Disable or distrust hooks and verify the explicit skill remains current-
    task-only.

Installation and trust change host state, so this flow is a deliberate manual
release step, not an automatic offline test.

## Cross-platform expectations

At minimum, run the offline suite on supported Python versions on Windows,
macOS, and Linux. Validate platform launcher commands, path/case normalization,
Git missing/timeout behavior, state locking, atomic replacement, permission
best efforts, read-only storage, and hook stdin/stdout encoding. When a target
cannot be run, record it as unverified with the concrete residual risk; do not
convert documentation review into a platform pass.

## Release validation checklist

- [ ] Offline unit suite passed with exact count.
- [ ] Python syntax/compile check passed.
- [ ] JSON and JSONL files parsed.
- [ ] Plugin validator passed.
- [ ] Skill metadata/frontmatter validator passed.
- [ ] Hook fixture outputs matched current schema.
- [ ] References and internal documentation links exist.
- [ ] No machine-specific absolute paths are committed.
- [ ] Static checks found no runtime network client, prompt logging, source
      persistence, `eval`, user-text shell construction, approval changes, or
      sandbox elevation.
- [ ] Marketplace schema and source path were reviewed separately.
- [ ] Local installation, hook trust, activation, status, cleanup, and skill
      fallback smoke tests passed.
- [ ] Original SVGs and the exact 256×256 directory and 48×48 composer PNGs
      were reviewed; no product UI screenshot was invented for this skills-only
      package.
- [ ] [Publishing](PUBLISHING.md), [Security](SECURITY.md),
      [Privacy](PRIVACY.md), license, and changelog were reviewed.

The final implementation report must distinguish checks run by automation from
manual checks and list every untested platform or host limitation.
