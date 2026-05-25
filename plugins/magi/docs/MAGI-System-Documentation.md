# MAGI System Documentation

## Overview

MAGI is a Codex plugin for structured multi-perspective analysis. It evaluates
non-trivial requests through three independent lenses and renders a consensus
report:

| Agent | Codename | Lens |
| --- | --- | --- |
| Melchior | Scientist | Technical rigor and correctness |
| Balthasar | Pragmatist | Practicality and maintainability |
| Caspar | Critic | Risk, edge cases, and failure modes |

Use MAGI for code reviews, design decisions, debugging, migrations, and trade-offs
where disagreement can reveal useful risks. Do not use it for simple questions or
obvious fixes.

## Codex Plugin Layout

```text
.codex-plugin/
  plugin.json
skills/magi/
  SKILL.md
  agents/
    melchior.md
    balthasar.md
    caspar.md
  scripts/
    synthesize.py
    validate.py
    consensus.py
    reporting.py
```

The primary Codex behavior is defined by `skills/magi/SKILL.md`. When the user
explicitly invokes MAGI or asks for three perspectives, Codex should run the
three perspectives independently, collect their JSON outputs, and synthesize the
canonical report.

## Modes

| Mode | Use |
| --- | --- |
| `code-review` | Reviewing code, diffs, PRs, patches, or implementation details |
| `design` | Evaluating architecture, migration plans, and approach selection |
| `analysis` | General trade-offs, debugging, or decision analysis |

## Agent Output Schema

Each perspective emits one JSON object:

```json
{
  "agent": "melchior | balthasar | caspar",
  "verdict": "approve | reject | conditional",
  "confidence": 0.0,
  "summary": "One-line verdict summary",
  "reasoning": "Detailed analysis from this agent's perspective",
  "findings": [
    {
      "severity": "critical | warning | info",
      "title": "Short title",
      "detail": "Explanation"
    }
  ],
  "recommendation": "What this agent recommends doing"
}
```

For code review, findings should include file and line references when available.

## Consensus

Verdicts are weighted:

```text
approve = 1
conditional = 0.5
reject = -1
score = sum(weights) / number_of_agents
```

| Score | Consensus |
| --- | --- |
| `1.0` | `STRONG GO` |
| `-1.0` | `STRONG NO-GO` |
| `> 0` with conditionals | `GO WITH CAVEATS (N-M)` |
| `> 0` without conditionals | `GO (N-M)` |
| `0` | `HOLD -- TIE` |
| `< 0` | `HOLD (N-M)` |

The `(N-M)` suffix is the effective go-side versus no-side split.

## Canonical Report

MAGI reports must use the canonical structure pinned in `skills/magi/SKILL.md`:

```text
+==================================================+
|          MAGI SYSTEM -- VERDICT                  |
+==================================================+
|  Melchior (Scientist):   APPROVE (90%)           |
|  Balthasar (Pragmatist): CONDITIONAL (85%)       |
|  Caspar (Critic):        REJECT (78%)            |
+==================================================+
|  CONSENSUS: GO WITH CAVEATS (2-1)                |
+==================================================+

## Key Findings
[!!!] **[CRITICAL]** SQL injection in query builder _(from melchior, caspar)_

## Dissenting Opinion
**Caspar (Critic)**: Risk of data loss outweighs shipping speed...

## Conditions for Approval
- **Balthasar**: Add integration tests before merge

## Recommended Actions
- **Melchior** (Scientist): Fix SQL injection, add parameterized queries
- **Balthasar** (Pragmatist): Ship after adding integration tests
- **Caspar** (Critic): Rework query layer before proceeding
```

Optional sections are omitted when empty. `## Recommended Actions` is always
present. Do not add a `## Consensus Summary` section.

## Python Runner

`skills/magi/scripts/run_magi.py` runs the three MAGI perspectives through
`codex exec` using a JSON output schema and `--output-last-message`. The runner
is useful for local non-interactive checks and keeps the same synthesis pipeline
used by the skill.
