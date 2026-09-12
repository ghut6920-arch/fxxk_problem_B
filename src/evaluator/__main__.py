"""CLI: ``PYTHONPATH=src python -m evaluator`` runs the ``evaluator_now`` self-check only.

Prints one line per fixture ID plus the manifest integrity result, and exits non-zero if any
``evaluator_now`` item mismatches its frozen expectation. It never invokes a candidate.
"""

from __future__ import annotations

import sys

from . import selfcheck


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    fixtures_dir = argv[0] if argv else selfcheck.default_fixtures_dir()
    results = selfcheck.check_all(fixtures_dir)
    failures = 0
    for result in results:
        status = "PASS" if result["ok"] else "FAIL"
        if not result["ok"]:
            failures += 1
        print("%-4s %-12s %s" % (result["id"], ",".join(result["phase_checks"]), status))
        for problem in result["mismatches"]:
            print("        %s" % problem)
    manifest = selfcheck.check_manifest(fixtures_dir)
    bad = [name for name, info in manifest.items() if not info["ok"]]
    print("manifest files checked: %d, mismatched: %d" % (len(manifest), len(bad)))
    for name in bad:
        print("        manifest mismatch: %s" % name)
    print("evaluator_now fixtures: %d, failed: %d" % (len(results), failures))
    return 1 if (failures or bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
