# Privacy

## Summary

Adaptive Codex Orchestrator is designed to operate locally and offline. The
plugin makes no external network requests, collects no telemetry, uses no
analytics service, and requires no API key, OAuth grant, or external account.

This document describes plugin behavior, not any separate data handling by the
Codex host, selected models, operating system, Git, or repository provider.

## Data stored

The active state file is `${PLUGIN_DATA}/state-v1.json`. It stores only the
fields required to resolve mode behavior:

- State schema version.
- Plugin-global enabled preference and profile.
- Project enabled/profile preferences keyed by a SHA-256 digest.
- Session enabled/profile overrides, whether the compatibility notice was
  shown, a bounded numeric `active_policy_revision` marker with no prompt or
  task content, and a bounded last-seen value when lifecycle cleanup uses it.
- One-shot enabled/profile state and lifecycle identifiers needed to clear it.

The runtime may also create these local implementation files inside the same
plugin-owned directory:

- `state-v1.corrupt-<digest>.json`: content-addressed backup of readable
  malformed or unsupported state before recovery. Recovery preserves the raw
  prior bytes so evidence is not silently discarded. Normal runtime state has
  only the categories above, but a file altered by another process could
  contain arbitrary data; treat a corrupt backup as potentially sensitive.
  The runtime neither interprets nor transmits the backup.
- `state-v1.json.lock`: best-effort concurrency lock containing no prompt,
  source, project path, or transcript content.
- `.state-v1-*.tmp`: transient atomic-write copy containing the sanitized state;
  it is replaced or removed during normal completion.

## Project identity

The project key is:

```text
SHA-256(normalized Git repository root or normalized current directory)
```

Git discovery uses `shell=False` and a short timeout. When Git is missing,
times out, or the directory is not a repository, the normalized current
working directory is hashed instead. The hash reduces casual path disclosure
in state; it is a stable pseudonymous identifier, not encryption. Someone who
already knows a candidate path could compute and compare its hash.

## Data not stored or collected

The plugin does not persist or intentionally collect:

- User prompts or control-command source text.
- Conversation transcripts or transcript files.
- Repository source code or generated patches.
- Raw absolute project paths.
- Repository names unless a future documented feature makes one necessary.
- Tool inputs/outputs, worker conversations, or validation logs.
- Model-provider credentials, API keys, OAuth tokens, or account identifiers.
- Telemetry, analytics, advertising identifiers, or usage profiles.

Prompt text is parsed in memory for the current event and is neither logged nor
written to state.

## Network behavior

The shipped control-plane runtime has no network requirement and must make no
external request. Delegated work is executed by the Codex host under the
host's own settings; this privacy statement does not override or describe the
host's separate network and data policies.

## Location, access, and retention

State is stored only in the host-provided plugin-owned `PLUGIN_DATA` directory.
The plugin does not write mode state into a repository, home-level Codex
configuration, or another plugin's data directory. Access is governed by the
operating-system account and the Codex host. User-only file permissions are
applied where the platform provides a meaningful supported API.

One-shot state is cleared after request completion, and session state is
cleared when the host delivers session end. Because that event can be delayed
or missed, the current runtime also removes inactive session entries older than
30 days during a later `SessionStart`. This is bounded stale-state cleanup,
not a promise that every session record disappears immediately when a client
view closes. Project and plugin-global preferences remain until changed or
reset. Recovery backups may remain until the user removes the plugin-owned data
directory.

## Reset and deletion

To reset all plugin state safely:

1. End affected Codex sessions so a running hook cannot recreate or rewrite
   state during deletion.
2. Obtain the exact `PLUGIN_DATA` directory assigned to
   `adaptive-codex-orchestrator` by the host.
3. Resolve and inspect that absolute path. Confirm it is the plugin-specific
   data directory and is **not** the plugin source, repository root, home
   directory, `.codex` root, or another shared parent directory.
4. Delete only that confirmed plugin-owned directory using the operating
   system's file manager or a literal-path deletion command.
5. Never use a wildcard, unresolved environment variable, home directory, or
   shared plugin-data parent as a recursive deletion target.

To reset active preferences while retaining recovery material, delete only
`state-v1.json` from the confirmed directory after ending active sessions. The
lock and transient files contain no user content but can be removed with the
confirmed plugin-owned directory during a full reset. A later trusted hook
recreates empty state. Removing the plugin package alone may not remove host-
managed plugin data; follow the host's current uninstall/data-removal UI if it
provides one.

## Future changes

Any future feature that adds network access, telemetry, credentials, prompt or
source persistence, transcript access, additional identifiers, or a new data
recipient requires an explicit privacy-policy update, security review, user-
visible disclosure, versioned state handling, and any consent required by the
target distribution surface. Such a change must not be introduced silently.

## Related documents

- [Architecture](ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Terms](TERMS.md)
