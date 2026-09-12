"""P1-B protocol adapter for the official robot interface (OFFICIAL-003).

Modules:

* :mod:`protocol.errors` -- definitive vs ambiguous error taxonomy;
* :mod:`protocol.client` -- stdlib HTTP/JSON client for ``/enter``, ``/measure``,
  ``/clear``, ``/exit`` with request_id idempotency and bounded same-id retry;
* :mod:`protocol.mapping` -- maps responses into the frozen candidate's
  observation/ledger types.

Nothing in this package imports ``evaluator``; no third-party package is used.
"""

__all__ = ["client", "errors", "mapping"]
