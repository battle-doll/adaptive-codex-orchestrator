# Publishing and Review Checklist

## State model

Verified on 2026-08-29: Adaptive Codex Orchestrator `0.1.0` is **Published** in
OpenAI Platform. The remote catalog records `GLOBAL` / `AVAILABLE` with
discoverability `UNLISTED` at
<https://chatgpt.com/plugins/plugins_6a86354985fc8191b33d2795e2851821>.
The date of first publication is not established. `UNLISTED` does not mean the
plugin appears in directory search or browse surfaces.

Version `0.1.1` is an **unsubmitted update candidate**. Keep these states
distinct for that update:

1. Source and policy pages are available on GitHub.
2. A ZIP is uploaded and **Submit for Review** is selected.
3. OpenAI approves the submitted version.
4. The developer separately selects **Publish**.

Approval does not publish an update. The published state of v0.1.0 does not
imply submission, approval, publication, or LISTED discoverability for v0.1.1.
Repository presence alone must not be presented as any of those states.

This is an independent community project and must not imply OpenAI affiliation,
sponsorship, endorsement, or official status.

## Candidate metadata

- [x] Package and manifest name: `adaptive-codex-orchestrator`
- [x] Version: `0.1.1`
- [x] Verified public developer identity used by existing listings:
      `battle-doll`
- [x] Display name and subtitle satisfy the 30-character limits.
- [x] Category: `Developer Tools`
- [x] One skill, no MCP server, no OAuth, no external account, and no custom UI.
- [x] Starter prompts: three entries, each at most 128 characters.
- [x] Public website, support, privacy, and terms destinations are declared in
      the repository [submission notes](../../../SUBMISSION.md).
- [x] Default `hooks/hooks.json` discovery is used. The manifest omits the
      optional `hooks` field for compatibility with the installed local
      validator.

Do not add invented URLs or claim a live destination before it resolves from
the public repository. Recheck every HTTPS URL immediately before submission.

## Visual assets

- [x] Original neutral SVG icon and logo reviewed for external resources and
      executable content.
- [x] `assets/logo.png` is an exact `256×256` directory icon.
- [x] `assets/composer-icon.png` is an exact `48×48` composer icon.
- [x] The same neutral PNG may be supplied to the corresponding light and dark
      slots; no additional theme-specific claim is made.
- [x] No OpenAI/ChatGPT logo, copied Codex artwork, external font, or remote
      image is bundled.
- [x] UI screenshots are not applicable because this is a skills-only package
      with no app or custom UI.

## Reviewer evidence

- [x] Exactly five positive and three negative cases, including setup,
      fixtures, expected behavior, expected result shape, and negative-case
      rationale, are in `evals/reviewer-cases.json`.
- [x] The broader policy dataset contains 31 deterministic scenarios.
- [x] Unit and fixture tests cover command ambiguity and non-mutation, state
      migration/concurrency/cleanup, project identity, five lifecycle events,
      compatibility notices, missing host data, invalid input, and output
      schema.
- [x] Package validation checks metadata limits, links, policies, JSON, SVG/PNG,
      reviewer cases, hook/runtime invariants, and local-path leakage.
- [x] The release builder creates a deterministic one-root ZIP and SHA-256
      sidecar; the artifact validator performs safe archive inspection before
      an optional trusted-source smoke import.
- [ ] Re-run every validation after the packaged tree is frozen. Record test
      counts in [Validation](VALIDATION.md), and record the final archive size
      and SHA-256 in the repository submission record and generated sidecar so
      the archive does not attempt to contain its own digest.

## Public repository and clean install

- [x] Public repository exists at
      `https://github.com/battle-doll/adaptive-codex-orchestrator`.
- [ ] Verify the root website, support, privacy, terms, security, and submission
      pages over HTTPS.
- [ ] Confirm GitHub Issues and private security advisories are usable.
- [ ] Install from the real GitHub marketplace source in a clean Codex setup.
- [ ] Start a new task, review and trust hooks, then exercise disabled behavior,
      one-shot/session/project/global scopes, profiles, status, cleanup,
      compatibility mode, bounded delegation, and the explicit skill fallback.

Public marketplace installation:

```text
codex plugin marketplace add battle-doll/adaptive-codex-orchestrator --ref main
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

For a local checkout, use the absolute repository root containing
`.agents/plugins/marketplace.json` as the marketplace source. Do not add the
implicitly discovered personal marketplace with `marketplace add`.

## Submission form

Immediately before the owner-authorized upload:

1. Recheck the current official package, listing, review, and policy rules.
2. Upload the deterministic ZIP, not a skill-only subdirectory.
3. Use `assets/logo.png` for both 256×256 directory-icon slots and
   `assets/composer-icon.png` for both 48×48 composer-icon slots.
4. Enter the three starter prompts and the exact five positive plus three
   negative reviewer cases.
5. Supply the release notes in the repository [submission notes](../../../SUBMISSION.md).
6. Request all countries and regions where the applicable OpenAI plugin and
   Codex surfaces are offered; this local/offline package has no service-side
   geographic dependency of its own.
7. Confirm the skill security scan has no unresolved finding.
8. Select **Submit for Review** only with action-time owner confirmation.

Do not select **Publish** for v0.1.1, even after approval, until the owner
separately asks for publication after hands-on use.

## Post-approval, pre-publication

- Record the approved version and review result without claiming publication.
- Install and test the exact approved package.
- Compare the installed bytes or checksum with the reviewed release artifact.
- Keep support and private security-reporting channels monitored.
- Let the owner decide whether to publish, revise, or keep the approved version
  unpublished.

## Maintenance

Before every later version, revalidate schemas, hook events, model slugs,
reasoning fields, platform claims, translations, state migrations, privacy and
security disclosures, reviewer cases, release notes, and public URLs. Changes
that add network access, credentials, telemetry, prompt/source persistence, or
new recipients require explicit design, privacy, and security review.
