"""Error taxonomy for the official robot interface (OFFICIAL-003).

The distinction that matters for P1-B is **definitive** versus **ambiguous**:

* definitive -- the simulator answered and we know whether the action executed
  (``accepted=true``, ``accepted=false``, a structural 400/413/415/404/405, or a
  409 idempotency conflict);
* ambiguous -- we do not know whether the action executed (connection refused or
  closed, timeout, response lost, unparseable/missing JSON, HTTP 429/500).

An ambiguous outcome must stop the affected interaction.  It must never cause a
**new** ``request_id``: the only legal recovery is to retry the identical request
with the identical id, which the simulator answers from its idempotency record.
"""

from __future__ import annotations


class ProtocolError(RuntimeError):
    """Base class for every protocol failure."""

    #: True when the simulator's execution state for this action is unknown.
    ambiguous = False
    #: True when the request may be corrected and retried with the same request_id.
    retryable_same_id = False


class TransportError(ProtocolError):
    """No HTTP response at all (connection refused/closed, timeout, DNS)."""

    ambiguous = True
    retryable_same_id = True


class MissingJsonError(ProtocolError):
    """An HTTP response arrived without a usable JSON business body."""

    ambiguous = True
    retryable_same_id = True


class UnknownAcceptError(ProtocolError):
    """The action's acceptance state could not be determined.

    Raised after the bounded same-id retries failed.  The caller must stop and
    must not send a new ``request_id``.
    """

    ambiguous = True
    retryable_same_id = False


class StructuralError(ProtocolError):
    """HTTP 400/413/415/404/405: the request itself was invalid.

    The request_id is **not** occupied, so the corrected request may reuse it.
    """

    ambiguous = False
    retryable_same_id = True

    def __init__(self, status, message, body=None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


class IdempotencyConflict(ProtocolError):
    """HTTP 409: the same request_id was already used for different content."""

    ambiguous = False
    retryable_same_id = False

    def __init__(self, status=409, message="same request_id with different content"):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


class ServerUnknownError(ProtocolError):
    """HTTP 429/500: the simulator may or may not have executed the action."""

    ambiguous = True
    retryable_same_id = True

    def __init__(self, status, message, body=None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


class ProtocolStop(ProtocolError):
    """The run must stop for a protocol/ledger reason (recorded, not hidden)."""

    def __init__(self, reason, detail=""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail
