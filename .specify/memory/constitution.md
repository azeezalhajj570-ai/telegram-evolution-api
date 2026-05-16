<!--
Version change: (template) → 1.0.0
Modified principles: N/A (initial population from template)
Added sections:
  - I. Code Quality
  - II. Testing Standards
  - III. User Experience Consistency
  - IV. Performance Requirements
  - V. Security & Observability
  - Technology & Architecture Constraints (Section 2)
  - Development Workflow & Quality Gates (Section 3)
  - Governance (fully populated)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/tasks-template.md → ⚠️ requires update: "Tests are OPTIONAL" line contradicts mandatory testing principle
Follow-up TODOs: N/A
-->

# Telegram Evolution API Constitution

## Core Principles

### I. Code Quality

Every codebase MUST be maintainable, readable, and consistent. Code reviews
are mandatory for all changes. Linting and formatting MUST be enforced via
automated tooling. No dead code, commented-out code, or TODO/FIXME without
an associated issue reference. Complexity MUST be justified — prefer simple
solutions over clever ones. All public APIs MUST include type annotations or
typed interfaces. Error messages MUST be actionable and include context.

### II. Testing Standards

Testing is NON-NEGOTIABLE. Every feature MUST include contract, integration,
and unit tests where applicable. Tests MUST be deterministic, independent, and
run as part of CI. No code reaches production without passing tests. The
red-green-refactor cycle MUST be followed for new features. Test coverage
MUST not regress — a failing test MUST be written before implementation code.
Flaky tests MUST be quarantined and fixed within one sprint.

### III. User Experience Consistency

All user-facing interfaces MUST follow a consistent design language,
terminology, and interaction pattern. Error states, loading states, and empty
states MUST be handled explicitly — no unhandled edge cases. Output formats
(CLI, API responses, logs) MUST be consistent in structure, naming, and error
codes. Documentation MUST accompany all user-facing changes. Accessibility
MUST be considered for all UI surfaces.

### IV. Performance Requirements

All features MUST define and meet measurable performance objectives. Latency
budgets MUST be established per endpoint or operation. Throughput and scaling
characteristics MUST be documented for service boundaries. Degradation under
load MUST be graceful and predictable. Database queries MUST be optimized —
N+1 patterns are forbidden in production paths. Performance MUST be part of
the review checklist; any change that materially affects performance MUST
include before/after benchmarks.

### V. Security & Observability

Security MUST be considered at every layer. All inputs MUST be validated and
sanitized. Secrets MUST never be hardcoded, logged, or committed.
Least-privilege access MUST be enforced for all service-to-service
communication. Structured logging is required for all services. Key metrics
(latency, error rate, throughput) MUST be exposed via a health endpoint.
Every failure mode MUST produce a traceable log entry with correlation
identifiers.

## Technology & Architecture Constraints

The primary implementation language MUST align with project conventions and
team expertise. Dependencies MUST be pinned to exact versions. No new
dependency MUST be added without evaluating its maintenance status, license
compatibility, and blast radius. Architecture MUST follow the patterns
established in the project — avoid introducing new frameworks, patterns, or
infrastructure without documented justification. Schema changes MUST be
backward-compatible or go through a documented migration plan.

## Development Workflow & Quality Gates

All changes MUST go through a pull request process with at least one approving
review before merge. The following gates MUST pass before merge:

- All tests pass (no skipped or ignored tests without justification)
- Linting and formatting checks pass
- No regressions in performance benchmarks (if applicable)
- Constitution compliance verification (complexity justification if violated)
- No secrets or sensitive data in the diff

Branch naming MUST follow the pattern `[###]-feature-name` where `###` is a
sequential issue number. Commits MUST be atomic and have descriptive messages.
Feature flags MUST be used for incomplete or experimental functionality.

## Governance

This Constitution supersedes all other process documentation. Amendments
require a documented proposal, team review, and explicit approval before
adoption.

**Amendment Process**:
1. Draft the proposed change with rationale
2. Open a review with affected stakeholders
3. Achieve consensus or majority approval
4. Update this document, incrementing the version according to semver
5. Propagate changes to dependent templates and guidance files

**Versioning Policy**:
- MAJOR: Backward-incompatible governance or principle removals/redefinitions
- MINOR: New principle or materially expanded guidance
- PATCH: Clarifications, wording refinements, typo fixes

**Compliance**: All PRs/reviews MUST verify compliance with these principles.
Complexity MUST be justified when a principle is violated. Runtime
development guidance is maintained in `AGENTS.md` (agent guidance) and team
conventions.

**Version**: 1.0.0 | **Ratified**: 2026-05-16 | **Last Amended**: 2026-05-16
