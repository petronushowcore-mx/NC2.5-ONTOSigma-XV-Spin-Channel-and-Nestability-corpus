"""check_bundle.py -- bundle-level consistency gate for the ONTOSigma XV repository.

Three checks, one exit code:

  C1  SMOKE      every harness module runs clean (exit 0) as a script, in BOTH the
                 normal and the -O interpreter mode (the -O pass guards against
                 assert-stripped vacuity), from an intact repository layout.
  C2  COUNTS     each verification module's self-reported final tally ("selftest:
                 N/N OK") matches the count declared for it in MANIFEST.md -- the
                 doc<->code drift gate (a stale count in the manifest goes red here).
  C3  HYGIENE    the packaging documents (README.md, MANIFEST.md) pass the same
                 hygiene gates corpus_gate.py applies to the corpus works:
                 logical quote-punctuation, no process-metadata vocabulary, no
                 reserved serial patterns.

Stdlib only, -O-safe.  Usage:
    python check_bundle.py           # run the gate (exit 0 / 1)
    python check_bundle.py --teeth   # synthetic-fixture self-audit (exit 0 / 1)
"""
import os
import re
import subprocess
import sys

HARNESS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HARNESS)
sys.path.insert(0, HARNESS)
from corpus_gate import _META, inv_absent, check  # noqa: E402  (shared detector patterns)

# modules with a numeric self-tally, then the two gate modules (smoke + marker only)
COUNTED = ["graph_hodge.py", "nestability.py", "core_reduction.py",
           "boundary_witness.py", "bridge_falsifier.py", "pilot_entrainment.py",
           "tower_transport.py", "funnel_channels.py", "fano_channel.py"]
MARKERED = {"teeth_audit.py": "teeth_audit: PASS",
            "corpus_gate.py": "corpus_gate: PASS"}

_TALLY = re.compile(r"selftest: (\d+)/(\d+) OK")


def _run(args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable] + args, cwd=HARNESS, env=env,
                       capture_output=True, timeout=120)
    return p.returncode, p.stdout.decode("utf-8", errors="replace")


def c1_c2(manifest_text, verbose=True):
    ok = True
    declared = dict((m, int(n)) for m, n in
                    re.findall(r"`([a-z_]+\.py)`[^|\n]*\|[^|\n]*\|\s*(\d+)\s+checks", manifest_text))
    for f in COUNTED + list(MARKERED):
        tallies = []
        for mode in ([], ["-O"]):
            rc, out = _run(mode + [f])
            good = rc == 0 and (f in COUNTED or MARKERED[f] in out)
            if f in COUNTED:
                m = _TALLY.search(out)
                good = good and m is not None and m.group(1) == m.group(2)
                if m:
                    tallies.append(int(m.group(2)))
            if verbose:
                print("  [%s] C1 smoke %-22s %s" % ("OK  " if good else "FAIL", f,
                                                    "-O" if mode else ""))
            ok = ok and good
        if f in COUNTED:
            want = declared.get(f)
            good = want is not None and tallies and all(t == want for t in tallies)
            if verbose:
                print("  [%s] C2 count %-22s manifest=%s actual=%s"
                      % ("OK  " if good else "FAIL", f, want, tallies))
            ok = ok and good
    return ok


def c3(texts, verbose=True):
    """texts: dict name -> content of the packaging docs."""
    gates = [("quotes", r'\."|,"'), ("meta", _META),
             ("serials", r"6[34]/[0-9]{3},?[0-9]{3}")]
    ok = True
    for name, pat in gates:
        label, clean, detail = inv_absent(name, pat, list(texts), texts)
        if verbose:
            print("  [%s] C3 %-8s %s" % ("OK  " if clean else "FAIL", label,
                                         "" if clean else detail))
        ok = ok and clean
    return ok


def _missing_packaging(root):
    return [n for n in ("README.md", "MANIFEST.md")
            if not os.path.exists(os.path.join(root, n))]


def _load_packaging():
    missing = _missing_packaging(ROOT)
    if missing:
        sys.stderr.write(
            "check_bundle: packaging documents not found. This gate reads README.md and\n"
            "MANIFEST.md relative to the repository layout (the .md files at the repository\n"
            "root, this script inside harness/). Run it from an intact clone, not from a\n"
            "flattened copy. Missing:\n"
            + "".join("  %s\n" % os.path.join(ROOT, n) for n in missing))
        sys.exit(2)
    texts = {}
    for name in ("README.md", "MANIFEST.md"):
        with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
            texts[name] = fh.read()
    return texts


# -- synthetic-fixture teeth (never touch the real files) -------------------
def run_teeth(verbose=True):
    rows = [
        ("manifest count parser sees a declared row",   # positive parse-assert: C2's
         # comparison logic is only as real as this extraction (anti-vacuum guard)
         lambda: dict(re.findall(r"`([a-z_]+\.py)`[^|\n]*\|[^|\n]*\|\s*(\d+)\s+checks",
                                 "| `graph_hodge.py` | core | 99 checks |")).get("graph_hodge.py") == "99",
         True),
        ("quote violation is caught",
         lambda: not c3({"fx": 'they said "done."'}, verbose=False), True),
        ("meta token is caught",
         lambda: not c3({"fx": "verified across 3 rounds"}, verbose=False), True),
        ("clean packaging text survives",
         lambda: c3({"fx": 'a clean line, quoted "properly", no vocabulary'}, verbose=False), True),
        ("flat-layout guard detects missing packaging docs",
         lambda: _missing_packaging(os.path.join(HARNESS, "no-such-root"))
         == ["README.md", "MANIFEST.md"], True),
    ]
    ok = True
    for name, fn, expect in rows:
        got = bool(fn())
        good = got == expect
        ok = ok and good
        if verbose:
            print("  %-38s %s" % (name, "ok" if good else "*** MISMATCH ***"))
    return ok


if __name__ == "__main__":
    if "--teeth" in sys.argv:
        print("check_bundle teeth:")
        good = run_teeth(verbose=True)
        print("teeth:", "PASS" if good else "FAIL")
        sys.exit(0 if good else 1)
    texts = _load_packaging()
    print("check_bundle -- bundle-level gates:")
    ok = c1_c2(texts["MANIFEST.md"], verbose=True)
    ok = c3(texts, verbose=True) and ok
    check(run_teeth(verbose=False), "check_bundle: self-audit teeth failed")
    print("check_bundle:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
