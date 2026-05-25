#!/usr/bin/env python3
# Author: Julian Bolivar
# Version: 1.1.1
# Date: 2026-04-26
"""MAGI model registry.

Single source of truth for the MAGI model short names accepted on the
command line and the Codex model IDs they resolve to. The short names are
kept for compatibility with the original MAGI CLI; their targets are Codex
models.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

_MODEL_IDS_MUTABLE: dict[str, str] = {
    "opus": "gpt-5.5",
    "sonnet": "gpt-5.4",
    "haiku": "gpt-5.4-mini",
}

#: Read-only view of the short-name -> Codex model-ID mapping.
#: Exposed as a :class:`~types.MappingProxyType` so downstream code cannot
#: accidentally mutate the canonical registry at runtime.
MODEL_IDS: Mapping[str, str] = MappingProxyType(_MODEL_IDS_MUTABLE)

#: Tuple of accepted short names, kept in lockstep with :data:`MODEL_IDS`.
VALID_MODELS: tuple[str, ...] = tuple(MODEL_IDS.keys())

#: Per-mode default short name. When ``--model`` is not given on the
#: CLI, :func:`run_magi.parse_args` looks the analysis mode up here
#: to pick the default. Explicit ``--model X`` always wins.
#:
#: **History:**
#:
#: * 2.2.2 and earlier: uniform ``opus`` default for every mode.
#: * 2.2.3 (2026-04-25): switched ``analysis`` to ``sonnet`` for cost
#:   relief, on the assumption that sonnet would match opus quality on
#:   exploratory questions at ~4× lower cost.
#: * 2.2.5 (2026-04-26): reverted ``analysis`` to ``opus``. Production
#:   evidence: Caspar (the most-output agent by design, consistently
#:   producing 4-7K output tokens) failed in ≥33% of sbtdd Loop
#:   verifications under sonnet — an order of magnitude above the
#:   3.3% design assumption. The 2.2.4 retry could not recover Caspar
#:   because the failure was structural (sonnet's ~8K output ceiling
#:   pressure on Caspar's adversarial-by-design verbosity), not
#:   stochastic. Reverting restores opus's 32K output budget for the
#:   mode where Caspar runs into the ceiling. The tripwire policy in
#:   memory/routine_telemetry_post_2.2.1.md fired by sustained
#:   evidence rather than by the literal "n=2 iter-2-style" letter.
#:
#: Every key MUST be in :data:`run_magi.VALID_MODES` and every value
#: MUST be in :data:`MODEL_IDS`; the test suite enforces both invariants.
_MODE_DEFAULTS_MUTABLE: dict[str, str] = {
    "code-review": "opus",
    "design": "opus",
    "analysis": "opus",
}
MODE_DEFAULT_MODELS: Mapping[str, str] = MappingProxyType(_MODE_DEFAULTS_MUTABLE)


def resolve_model(short_name: str) -> str:
    """Return the Codex model ID for *short_name*.

    Args:
        short_name: A MAGI model short name (e.g. ``"opus"``).

    Returns:
        The corresponding Codex model identifier.

    Raises:
        ValueError: If *short_name* is not a registered model.
    """
    try:
        return MODEL_IDS[short_name]
    except KeyError:
        raise ValueError(
            f"Unknown model '{short_name}'. Must be one of {sorted(MODEL_IDS.keys())}."
        ) from None
