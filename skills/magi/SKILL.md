---
name: magi
description: >
  Multi-perspective analysis system for Codex inspired by the MAGI supercomputers.
  Use this skill when the user asks for MAGI, three perspectives, multi-perspective
  analysis, MAGI review, or a multi-angle evaluation of code, design, debugging,
  trade-offs, or consequential decisions. Not suitable for trivial questions,
  simple bugs, or decisions with one obvious answer.
---

# MAGI System - Multi-Perspective Analysis Skill

## Overview

MAGI analyzes a non-trivial request through three independent perspectives, then
synthesizes a consensus:

| Agent | Codename | Lens |
| --- | --- | --- |
| **Melchior** | Scientist | Technical rigor and correctness |
| **Balthasar** | Pragmatist | Practicality and maintainability |
| **Caspar** | Critic | Risk, edge cases, and failure modes |

## Workflow

### Step 1: Gate Complexity and Detect Mode

Use MAGI only when the request benefits from structured disagreement. If the
request is simple, direct, or has one clear answer, answer normally without
running the three-perspective process.

Classify the request:

- `code-review` - code, diffs, PRs, patches, or implementation review.
- `design` - architecture, approach selection, migration plans, or solution design.
- `analysis` - general debugging, trade-offs, or decisions.

Default to `analysis` when ambiguous.

### Step 2: Prepare Shared Payload

Build a shared payload:

```text
MODE: <code-review | design | analysis>
CONTEXT: <user's full request, code, diff, file contents, and relevant local context>
```

If files are relevant, inspect them first and include concise, line-referenced
context in the payload.

### Step 3: Run Three Perspectives

Preferred in Codex: use native sub-agents when the user invocation explicitly
asks for MAGI, three perspectives, or multi-agent/multi-perspective analysis.
Launch the three perspectives independently with the shared payload and the
matching prompt files:

- `agents/melchior.md`
- `agents/balthasar.md`
- `agents/caspar.md`

Each perspective must return only this JSON object:

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

For code review mode, findings should include specific file and line references
when available.

### Step 4: Synthesize

Use the Python synthesis helpers when agent JSON files are available:

```bash
python skills/magi/scripts/synthesize.py <agent1.json> <agent2.json> [agent3.json] --output report.json
```

If running synthesis manually in the conversation, apply these weights:

- `approve = 1`
- `conditional = 0.5`
- `reject = -1`

Consensus labels:

| Score | Consensus |
| --- | --- |
| `1.0` | `STRONG GO` |
| `-1.0` | `STRONG NO-GO` |
| `> 0` with conditionals | `GO WITH CAVEATS (N-M)` |
| `> 0` without conditionals | `GO (N-M)` |
| `0` | `HOLD -- TIE` |
| `< 0` | `HOLD (N-M)` |

The `(N-M)` suffix reflects effective go-side versus no-side split.

### Step 5: Present Canonical Output

Every MAGI invocation must end with this canonical structure. Do not add a
separate `## Consensus Summary` section.

#### Canonical output template

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
[!!]  **[WARNING]**  Missing retry logic for API calls _(from balthasar)_
[i]   **[INFO]**     Consider adding request timeout _(from caspar)_

## Dissenting Opinion
**Caspar (Critic)**: Risk of data loss outweighs shipping speed...

## Conditions for Approval
- **Balthasar**: Add integration tests before merge

## Recommended Actions
- **Melchior** (Scientist): Fix SQL injection, add parameterized queries
- **Balthasar** (Pragmatist): Ship after adding integration tests
- **Caspar** (Critic): Rework query layer before proceeding
```

Omit optional sections when empty. Always include `## Recommended Actions`.

## Fallback

If native sub-agents are unavailable, simulate the three perspectives in one
response. Generate Caspar first, then Melchior, then Balthasar to reduce approval
anchoring. Treat those JSON blocks as intermediate scaffolding and still end with
the canonical MAGI report.

## Python Runner

The Python orchestrator in `scripts/run_magi.py` runs the same three-perspective
workflow through `codex exec` for local non-interactive usage and tests:

```bash
python skills/magi/scripts/run_magi.py <mode> <input_file_or_text> [--model opus] [--timeout 900]
```

The model short names are compatibility aliases: `opus` resolves to the most
capable Codex model, `sonnet` to the balanced model, and `haiku` to the fast
model.
