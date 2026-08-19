# Terms and Usage Notice

## Independent community tool

Adaptive Codex Orchestrator is an independent, community-created developer
tool. It is not affiliated with, sponsored by, endorsed by, or an official
product of OpenAI. References to OpenAI, ChatGPT, Codex, Sol, and Spark identify
third-party products or compatibility targets only.

## Open-source license

The source code is provided under the [MIT License](../LICENSE). That license
governs permission to use, copy, modify, merge, publish, distribute,
sublicense, and sell copies of the software. This document explains operating
responsibilities and does not reduce rights granted by the license.

## User responsibility

The plugin supplies local state handling and orchestration guidance. It does
not replace professional review or make model-generated work correct, secure,
compliant, or fit for a particular purpose. Users remain responsible for:

- Reviewing prompts, worker contracts, generated code, delegated changes, and
  validation evidence.
- Deciding whether to trust local hooks and which permissions to grant Codex.
- Protecting credentials, private source, personal data, and production systems.
- Testing changes proportionately before integration, deployment, or release.
- Obtaining any required organizational, legal, security, privacy, licensing,
  regulatory, or third-party approval.
- Following the terms and policies of the Codex host and any selected model.

## High-impact use

Do not rely on this tool as the sole reviewer or decision-maker for destructive
operations, authentication or authorization, cryptography, safety-critical
systems, regulated decisions, production incidents, data migration, or other
high-impact work. The runtime policy intentionally leaves final judgment with
the parent and user, but that policy is not a technical guarantee that a model
will produce a safe result.

## Availability and compatibility

Model availability, names, quotas, hook events, plugin schemas, and host
features are controlled by third parties and may change. The plugin may enter
compatibility mode, fall back to the parent, or lose persistent controls when
the host does not expose a required capability. No guarantee of uninterrupted
operation, a particular worker model, or a particular performance improvement
is made.

## Privacy and security

The project is designed for local, offline control-plane operation as described
in [Privacy](PRIVACY.md) and [Security](SECURITY.md). Those documents describe
the plugin implementation and do not make guarantees about the separate Codex
host, model provider, operating system, Git installation, or user extensions.

## No warranty or legal guarantee

The software is provided under the warranty disclaimer in the MIT License. No
statement in project documentation is a promise of defect-free, secure,
compliant, or continuously available operation. This document is general
project information and is not legal advice. Repository owners should obtain
qualified review before adopting final public terms or using the tool in a
regulated or high-risk context.

## Changes and redistribution

Modified or redistributed versions should preserve applicable license and
copyright notices. Maintainers should clearly distinguish their changes and
must not imply official OpenAI affiliation. A distributor is responsible for
its own publication metadata, support commitments, privacy disclosures,
trademark review, and compliance obligations.
