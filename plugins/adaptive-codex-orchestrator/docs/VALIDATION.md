# Validation Record

## Local pre-submission snapshot

Date: **2026-08-19** (Asia/Seoul)

Environment:

- Windows
- Python 3.12.10
- Codex CLI 0.145.0
- Offline runtime and package checks; no credential or external service is
  required by the plugin itself

Commands are shown from the repository root unless the text says otherwise.

## Automated results

### Unit and hook fixtures

```text
python -B -m unittest discover \
  -s plugins/adaptive-codex-orchestrator/tests \
  -p "test_*.py" -v
```

Result: **PASS** — 108 tests ran with 0 failures, 0 errors, and 1 intentional
skip. The skipped check is POSIX `0600` permission-bit enforcement on Windows.

Coverage includes the Korean/English command matrix, quoted/fenced/incidental
text and strict non-mutation, scope/profile precedence, atomic state and
recovery, migration, concurrent sessions, 30-day stale-session cleanup, Git
and non-Git project identity, Windows and POSIX launchers, five lifecycle
events, one-shot cleanup, compatibility notices, missing host data, invalid and
oversized input, output schema, compact-policy revision de-duplication, lazy
detailed-policy loading, lock contention recovery, bounded revision metadata,
and prompt/source non-persistence.

### Policy scenarios

```text
python -B plugins/adaptive-codex-orchestrator/scripts/evaluate_policies.py
```

Result: **PASS** — all 31 deterministic routing scenarios passed their schema
and policy invariants, including task caps, one-writer enforcement, single
spawn attempt and parent fallback, no host-default substitution, exact six-
field worker results, requested/confirmed model separation, and targeted parent
spot-checking without broad duplicate exploration.

### Package contract

```text
python -B plugins/adaptive-codex-orchestrator/scripts/validate_package.py \
  --repo-root .
```

Result: **PASS** — 1,969 assertions. The validator covers manifest listing
limits and exact starter prompts, publisher and public URLs, marketplace
source, default hook discovery, skill metadata, model policy, Python AST
security boundaries, state persistence fields, JSON, SVG, exact 256×256 and
48×48 PNG dimensions, five positive plus three negative reviewer cases,
required package and root documents, the exact 34-file five-language suite,
relative links, license parity, and machine-local path leakage.

### Installed plugin and skill validators

```text
python -B <plugin-creator-root>/scripts/validate_plugin.py \
  plugins/adaptive-codex-orchestrator
python -B <skill-creator-root>/scripts/quick_validate.py \
  plugins/adaptive-codex-orchestrator/skills/adaptive-orchestration
```

Results: **PASS** — `Plugin validation passed` and `Skill is valid!`.
Developer-specific validator paths are intentionally not committed.

### Syntax and structured files

All 16 Python files under `hooks`, `scripts`, and `tests` compiled in memory.
The package validator parsed every JSON document with duplicate-key rejection.
The marketplace JSON and 3 OS × 2 Python GitHub Actions matrix were also
reviewed. The configured CI targets Windows, macOS, and Linux on Python 3.9 and
3.12.

### Localization

Result: **PASS** — 34 strict UTF-8 Markdown files provide English, Korean,
Japanese, Simplified Chinese, and Russian README, publishing, support,
security, privacy, terms, and submission coverage. Language switchers, local
links, manifest values, reviewer-case references, and the Korean/English-only
control-language boundary were checked. No Spanish file or Spanish language
claim is present.

### Deterministic release tooling

```text
python -B plugins/adaptive-codex-orchestrator/scripts/build_release.py
python -B plugins/adaptive-codex-orchestrator/scripts/validate_release_artifact.py \
  plugins/adaptive-codex-orchestrator/dist/adaptive-codex-orchestrator-0.1.1.zip \
  --trusted-source-root plugins/adaptive-codex-orchestrator \
  --require-sidecar
```

The builder performs two independent byte-identical builds, writes a SHA-256
sidecar atomically, and invokes safe archive validation. The validator rejects
path traversal, absolute and backslash paths, secret-like filenames, private
user-home paths, oversized members, compression-ratio bombs, portable-case
collisions, duplicate members, symlinks, non-deterministic metadata, and
source/archive byte differences. It imports archive code only after every byte
matches the trusted local source and then uses an isolated smoke process.

The final archive size and digest belong in the generated sidecar and the
repository submission record, not inside this packaged document; an archive
cannot contain its own stable digest.

## Independent review

Bounded independent audits found and rechecked defects involving long fenced
examples, informational questions, profile-use phrases, referential conflicts,
one-shot profile expiry, corrupt-backup privacy wording, Windows lock
initialization, public metadata limits, review-case shape, hook cleanup, and
release archive attacks. Confirmed defects were fixed and covered by focused
tests or deterministic validation.

## Live checks outside this snapshot

- GitHub Actions is configured but was not dispatched in this local snapshot;
  macOS, Linux, and Python 3.9 results remain CI evidence rather than local
  execution evidence.
- Public URL resolution, installation from the real GitHub marketplace source,
  Codex hook trust, a live host delegation, OpenAI upload scanning, and review
  status are external steps recorded separately when performed.
- Ultra reasoning cannot be programmatically verified. A worker `model` field
  is a host report, not proof of completed use or billing identity.
- Approval does not publish the plugin. The developer-controlled Publish action
  is intentionally outside this candidate's validation and remains withheld
  pending hands-on use and a separate owner decision.

See [Testing](TESTING.md), [Compatibility](COMPATIBILITY.md), and
[Publishing](PUBLISHING.md) for the repeatable workflow and residual host
limitations.
