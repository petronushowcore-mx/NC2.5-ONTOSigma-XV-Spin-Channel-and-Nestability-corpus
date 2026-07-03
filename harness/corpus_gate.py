"""corpus_gate.py -- declarative cross-document consistency gate + reference map.

Generalises the hygiene grep-gates (quote-punctuation / process-metadata /
serial patterns) to cross-doc SET-EQUALITY: a small list of
INVARIANTS run over a coupled corpus (essay + companion + protocol companion). Catches the mirror-drift
failure class -- a label added to one doc's list but NOT its mirror in the other
doc (e.g. OP 7.7 added to companion but absent from the essay table) -- which the
grep-in-head reconstruction misses. Also regenerates `corpus-map.md`: a grep-index
of each entity's occurrence sites across both works (the durable pre-edit checklist
that replaces holding the cross-reference map in memory).

No parser / namespace machinery: the invariants use UNAMBIGUOUS labels (OP N.M,
XV.k, bold-declared **Kind N.M**) that do not collide with a sibling corpus. Dangling-
reference resolution is intentionally OUT of scope (covered by the review passes);
add a namespace-aware version later only if a real broken ref slips through.

Stdlib only, -O-safe.  Usage:
    python corpus_gate.py            # run the gate (exit 0 / 1)
    python corpus_gate.py --map      # regenerate corpus-map.md
    python corpus_gate.py --teeth    # synthetic-fixture self-audit (exit 0 / 1)
"""
import re
import os
import sys


def check(cond, msg="check failed"):
    """-O-safe assert."""
    if not cond:
        raise AssertionError(msg)


HARNESS = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HARNESS)  # repository root
DOC_PATHS = {
    "essay": os.path.join(CORPUS, "ONTOSigma-XV-Spin-Channel-and-Nestability.md"),
    "companion": os.path.join(CORPUS,
                              "Spin-Channel Bridge and Core-Reduction — A Categorical Foundation.md"),
    "protocol": os.path.join(CORPUS,
                             "Two Funnels, One Spin — A Table-Top Protocol Companion.md"),
}


def _require_layout():
    """Fail with a clear message (not a bare traceback) when the repository layout
    is not preserved -- e.g. the files were downloaded flat into one directory."""
    missing = [p for p in DOC_PATHS.values() if not os.path.exists(p)]
    if missing:
        sys.stderr.write(
            "corpus_gate: corpus documents not found. This gate reads the corpus works\n"
            "relative to the repository layout (the corpus .md files at the repository root,\n"
            "this script inside harness/). Run it from an intact clone, not from a\n"
            "flattened copy. Missing:\n" + "".join("  %s\n" % m for m in missing))
        sys.exit(2)

_HDR = re.compile(r"^(#{1,6})\s")


def load_docs():
    _require_layout()
    d = {}
    for k, p in DOC_PATHS.items():
        with open(p, encoding="utf-8") as f:
            d[k] = f.read()
    return d


def section_slice(text, heading_regex):
    """Text from a heading matching heading_regex to the next heading of same-or-higher
    level (fewer-or-equal '#'), or EOF."""
    lines = text.splitlines()
    hre = re.compile(heading_regex)
    start = level = None
    for i, ln in enumerate(lines):
        if start is None:
            if hre.search(ln):
                start = i
                m = _HDR.match(ln)
                level = len(m.group(1)) if m else 6
            continue
        m = _HDR.match(ln)
        if m and len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    check(start is not None, "section heading not found: %s" % heading_regex)
    return "\n".join(lines[start:])


# -- invariant kinds (each returns (name, ok, detail)) --------------------
def inv_set_equal(name, pattern, scopeA, scopeB, docs):
    (ka, ha), (kb, hb) = scopeA, scopeB
    sa = set(re.findall(pattern, section_slice(docs[ka], ha)))
    sb = set(re.findall(pattern, section_slice(docs[kb], hb)))
    ok = sa == sb
    detail = "" if ok else "only-in-%s=%s  only-in-%s=%s" % (ka, sorted(sa - sb), kb, sorted(sb - sa))
    return (name, ok, detail)


def inv_same_set(name, pattern, ka, kb, docs):
    sa = set(re.findall(pattern, docs[ka]))
    sb = set(re.findall(pattern, docs[kb]))
    ok = sa == sb
    detail = "" if ok else "only-in-%s=%s  only-in-%s=%s" % (ka, sorted(sa - sb), kb, sorted(sb - sa))
    return (name, ok, detail)


def inv_no_dup(name, pattern, keys, docs):
    bad = []
    for k in keys:
        seen = {}
        for tup in re.findall(pattern, docs[k]):
            seen[tup] = seen.get(tup, 0) + 1
        dups = [t for t, c in seen.items() if c > 1]
        if dups:
            bad.append((k, dups))
    return (name, not bad, str(bad))


def inv_absent(name, pattern, keys, docs):
    hits = []
    rx = re.compile(pattern)
    for k in keys:
        for i, ln in enumerate(docs[k].splitlines(), 1):
            if rx.search(ln):
                hits.append("%s:L%d" % (k, i))
    return (name, not hits, "; ".join(hits[:8]))


# -- the XV corpus invariant list (per-corpus config) --------------------
# declarations are standalone paragraphs -> anchor at line-start (?m)^**Kind N.M ; this
# excludes bold *mentions* mid-line (e.g. the Abstract's "**Theorem 1 (...):**" list).
_DECL = r"(?m)^\*\*(Definition|Lemma|Proposition|Theorem|Counter-example|Remark) (\d+(?:\.\d+)?[a-z]?)"
# detector patterns, not content: process-vocabulary that must never appear in the
# published texts (the tokens below exist here only so the gate can reject them)
_META = r"Tier [12]|Tier 1[AB]|cards-first|tier-protocol|cascade-audit|\b[0-9]+ rounds?\b|de-declarativ|verbatim_relay|META-Q"

INVARIANTS = [
    ("OP-mirror  companion §7 == essay §10.2",
     lambda d: inv_set_equal("OP", r"OP (\d+\.\d+)",
                             ("companion", r"^## 7\. Open Problems"),
                             ("essay", r"^### 10\.2\."), d)),
    ("XV.k present in both docs",
     lambda d: inv_same_set("XV.k", r"XV\.(\d)\b", "essay", "companion", d)),
    ("no duplicate **Kind N.M** declaration",
     lambda d: inv_no_dup("decl", _DECL, ["essay", "companion", "protocol"], d)),
    ("quote-punctuation, logical style  (.\"  ,\")",
     lambda d: inv_absent("quotes", r'\."|,"', ["essay", "companion", "protocol"], d)),
    ("no process-metadata vocabulary",
     lambda d: inv_absent("meta", _META, ["essay", "companion", "protocol"], d)),
    ("serial-pattern hygiene",
     lambda d: inv_absent("serials", r"6[34]/[0-9]{3},?[0-9]{3}", ["essay", "companion", "protocol"], d)),
]


def run_gate(docs, verbose=True):
    results = [spec(docs) for _, spec in INVARIANTS]
    for name, ok, detail in results:
        if verbose:
            print("  [%s] %s%s" % ("OK  " if ok else "FAIL", name, "" if ok else "  --  " + detail))
    return all(ok for _, ok, _ in results), results


# -- the grep-index map ---------------------------------------------------
def _entities(docs):
    ents = set()
    for k in docs:
        for kind, num in re.findall(_DECL, docs[k]):
            ents.add("%s %s" % (kind, num))
        for op in re.findall(r"OP (\d+\.\d+)", docs[k]):
            ents.add("OP %s" % op)
    return ents


def _entkey(e):
    m = re.search(r"(\d+)(?:\.(\d+))?", e)
    return (e.split()[0], int(m.group(1)) if m else 0, int(m.group(2)) if (m and m.group(2)) else 0)


def gen_map(docs):
    out = ["# corpus-map.md", "",
           "Cross-reference index (generated: `python corpus_gate.py --map`). Per entity: its",
           "occurrence sites in each work -- the pre-edit cascade checklist. Do NOT hand-edit.",
           ""]
    for ent in sorted(_entities(docs), key=_entkey):
        out.append("## %s" % ent)
        for k in docs:
            sites = [i for i, ln in enumerate(docs[k].splitlines(), 1) if ent in ln]
            if sites:
                out.append("- %s: %s" % (k, ", ".join("L%d" % s for s in sites)))
        out.append("")
    return "\n".join(out)


# -- synthetic-fixture teeth (never touch the real files) ----------------
FIXT_COMPANION = """## 3. Section
**Definition 3.5 (X).** foo. XV.1 and XV.2 are discussed here.
**Proposition 3.7 (Y).** bar.
Abstract-style line restating **Proposition 3.7** and **Theorem 1** inline (a mid-line bold mention must NOT count as a declaration -- regression guard for line-anchoring).

## 7. Open Problems
- **OP 7.1 — A.** x
- **OP 7.2 — B.** y

## 8. References
"""

FIXT_ESSAY = """Intro. XV.1 and XV.2 are discussed here.

### 10.2. Open-Problem Status
| **OP 7.1** A | open |
| **OP 7.2** B | open |

---
"""


FIXT_PROTOCOL = """# Protocol fixture
An Illustration-level protocol document; hygiene-clean synthetic stand-in for the
table-top protocol companion (the absent-gates must scan it like the real one).
"""


def _fixtures():
    return {"companion": FIXT_COMPANION, "essay": FIXT_ESSAY,
            "protocol": FIXT_PROTOCOL}


def _drop_op_essay(d):
    d["essay"] = d["essay"].replace("| **OP 7.2** B | open |\n", "")

def _add_unmirrored_op_companion(d):
    d["companion"] = d["companion"].replace("## 8.", "- **OP 7.3 — C.** z\n\n## 8.")

def _inject_dedeclarativize(d):
    d["essay"] = d["essay"] + "\nThis would de-declarativize XV.2 fully.\n"

def _dup_definition(d):
    d["companion"] = d["companion"] + "\n**Definition 3.5 (accidental duplicate).** clash.\n"

def _add_mirrored_op_both(d):
    d["companion"] = d["companion"].replace("## 8.", "- **OP 7.3 — C.** z\n\n## 8.")
    d["essay"] = d["essay"].replace("---", "| **OP 7.3** C | open |\n\n---")

def _rephrase_no_label_change(d):
    d["essay"] = d["essay"].replace("| **OP 7.1** A |", "| **OP 7.1** A (reworded) |")

def _inject_meta_protocol(d):
    # process vocabulary planted in the THIRD doc: proves the absent-gates actually
    # scan the protocol companion (anti-vacuum for the DOC_PATHS extension)
    d["protocol"] = d["protocol"] + "\nThis line was verified across 3 rounds.\n"


TEETH = [
    ("drop OP from essay mirror",      _drop_op_essay,             "RED"),
    ("add unmirrored OP to companion", _add_unmirrored_op_companion, "RED"),
    ("inject de-declarativize (meta)", _inject_dedeclarativize,    "RED"),
    ("duplicate Definition 3.5",       _dup_definition,            "RED"),
    ("add mirrored OP to BOTH",        _add_mirrored_op_both,      "SURVIVE"),
    ("rephrase prose, labels intact",  _rephrase_no_label_change,  "SURVIVE"),
    ("plant meta-vocab in protocol doc", _inject_meta_protocol,    "RED"),
]


def run_teeth(verbose=True):
    # baseline fixtures must PASS the gate unmutated
    ok0, _ = run_gate(_fixtures(), verbose=False)
    check(ok0, "teeth baseline: unmutated fixtures must pass the gate")
    # positive parse-assert: the parser actually SEES the labels (anti-vacuum)
    fx = _fixtures()
    op_c = set(re.findall(r"OP (\d+\.\d+)", section_slice(fx["companion"], r"^## 7\. Open Problems")))
    check(op_c == {"7.1", "7.2"}, "parse-assert: companion §7 OP set must be {7.1,7.2}, got %s" % op_c)
    check(set(re.findall(r"XV\.(\d)\b", fx["essay"])) == {"1", "2"}, "parse-assert: essay XV.k must be {1,2}")
    ok = True
    for name, mut, expect in TEETH:
        d = _fixtures()
        mut(d)
        passed, _ = run_gate(d, verbose=False)
        actual = "SURVIVE" if passed else "RED"
        good = actual == expect
        if not good:
            ok = False
        if verbose:
            print("  %-34s expect %-8s got %-8s %s" % (name, expect, actual, "ok" if good else "*** MISMATCH ***"))
    return ok


# -- entry point ----------------------------------------------------------
def selftest():
    """Positive parse-assert on the REAL corpus, then the gate, then teeth.
    FAILURE RAISES (uniform with the other harness modules): a runner that calls
    selftest() and ignores the return value must still see the failure."""
    docs = load_docs()
    op_c = set(re.findall(r"OP (\d+\.\d+)", section_slice(docs["companion"], r"^## 7\. Open Problems")))
    check("7.7" in op_c, "parse-assert: companion §7 must contain OP 7.7 (parser sees latest label), got %s" % sorted(op_c))
    check(set(re.findall(r"XV\.(\d)\b", docs["essay"])) >= {"1", "2", "3"}, "parse-assert: essay must carry XV.1/2/3")
    ok_gate, _ = run_gate(docs, verbose=False)
    check(ok_gate, "corpus_gate: real-corpus invariant gate FAILED")
    check(run_teeth(verbose=False), "corpus_gate: teeth FAILED (a mutation deviated from expected)")
    return True


if __name__ == "__main__":
    if "--map" in sys.argv:
        docs = load_docs()
        out = os.path.join(CORPUS, "corpus-map.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(gen_map(docs) + "\n")
        print("wrote %s" % out)
        sys.exit(0)
    if "--teeth" in sys.argv:
        print("corpus_gate teeth:")
        ok = run_teeth(verbose=True)
        print("teeth:", "PASS (all as predicted)" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    # default: the gate on the real corpus
    docs = load_docs()
    op_c = set(re.findall(r"OP (\d+\.\d+)", section_slice(docs["companion"], r"^## 7\. Open Problems")))
    check("7.7" in op_c, "parse-assert: parser must see OP 7.7 in companion §7, got %s" % sorted(op_c))
    print("corpus_gate — cross-document invariants:")
    ok, _ = run_gate(docs, verbose=True)
    print("corpus_gate:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
