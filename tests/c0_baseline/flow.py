"""Shared driver for the WI-020 offline baseline flows.

Ties the frozen C0 runner to a scripted environment and produces the certificate,
the itemized cost decomposition and the fail-closed record for one scenario.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate import model as candidate_model
from candidate import scan
from candidate.state import ConflictError

from protocol.errors import ProtocolStop, UnknownAcceptError

from . import costing
from .scenario import ScriptedEnv


@dataclass
class FlowResult:
    question: str
    env: ScriptedEnv = None
    runner: object = None
    certificate: dict = field(default_factory=dict)
    cost: costing.CostBreakdown = None
    ledger_total: float = 0.0
    ledger_recomputed: float = 0.0
    stop_reason: object = None
    unknown_accept: bool = False
    deadline_stop: bool = False
    exit_seen: bool = False
    actions_at_stop: int = 0
    error: str = ""

    @property
    def completed(self):
        return self.stop_reason is None and self.certificate.get("status") == candidate_model.COMPLETE

    @property
    def false_completion(self):
        """A COMPLETE certificate after a fail-closed stop would be a false completion."""
        return self.stop_reason is not None and self.certificate.get("status") == candidate_model.COMPLETE

    def to_dict(self):
        return {
            "question": self.question,
            "certificate": {k: v for k, v in self.certificate.items()
                            if k != "explicit_release_reasons"},
            "stop_reason": self.stop_reason,
            "unknown_accept": self.unknown_accept,
            "deadline_stop": self.deadline_stop,
            "exit_seen": self.exit_seen,
            "actions_emitted": self.env.accepted_action_count() if self.env else 0,
            "actions_at_stop": self.actions_at_stop,
            "ledger_total": self.ledger_total,
            "ledger_recomputed": self.ledger_recomputed,
            "ledger_agrees_with_decomposition": (
                None if self.cost is None
                else abs(self.ledger_recomputed - self.cost.total_seconds) < 1e-9),
            "error": self.error,
            "cost": None if self.cost is None else self.cost.to_dict(),
        }


def run_flow(question, specs, inject_unknown_accept_at=None, inject_deadline_at=None,
             do_exit=True):
    """Drive the frozen C0 runner over one scripted scenario.

    ``inject_*`` places a fail-closed fault at an exact 1-based action index.  The
    driver mirrors the session rules: an unknown acceptance state or a spent real
    deadline stops the run, the ledger is never credited for it, and no completion
    certificate may be produced afterwards.
    """
    points = scan.P3() if question == "Q3" else scan.P4()
    env = ScriptedEnv(specs, total_stages=len(points))
    if inject_unknown_accept_at is not None:
        env.inject_unknown_accept_at(inject_unknown_accept_at)
    if inject_deadline_at is not None:
        env.inject_deadline_at(inject_deadline_at)
    runner = candidate_model.C0Runner(env, channels=scan.Q3_Q4_CHANNELS)
    result = FlowResult(question=question, env=env, runner=runner)

    runner.ledger.enter()
    try:
        runner.run_scan(points, question=question)
        runner.run_clears()
        result.certificate = runner.completion_certificate()
        if do_exit:
            runner.ledger.exit()
            result.exit_seen = True
    except UnknownAcceptError as exc:
        result.unknown_accept = True
        result.stop_reason = "unknown_accept"
        result.error = str(exc)
    except ProtocolStop as exc:
        result.deadline_stop = exc.reason == "real_deadline"
        result.stop_reason = exc.reason
        result.error = str(exc)
    except ConflictError as exc:
        # a rule/quantity/coverage contradiction: C0 must never report it as success
        result.stop_reason = "conflict"
        result.error = str(exc)

    result.actions_at_stop = env.accepted_action_count()
    result.ledger_total = runner.ledger.total
    result.ledger_recomputed = costing.candidate_ledger_total(runner.ledger)
    result.cost = costing.decompose(env.actions, question)
    return result
