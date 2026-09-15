#!/usr/bin/env python3
"""Extract assessment objectives and procedures from the NIST SP 800-171A PDF
(sources/NIST.SP.800-171A.pdf) into sources/sp800-171a-extracted.json.

Uses `pdftotext -raw` (poppler). The extracted JSON is committed so the build
does not depend on the poppler version present at build time; re-run this
script and diff when the PDF or poppler changes.

Join rule: a line ending in '-' is joined to the next line with the hyphen
kept (NIST does not soft-hyphenate; end-of-line hyphens are real compounds).
Every such join is listed in the output under "hyphen_joins" for review.
"""
import re, json, subprocess, pathlib, collections, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "sources/NIST.SP.800-171A.pdf"
OUT = ROOT / "sources/sp800-171a-extracted.json"

raw = subprocess.run(["pdftotext", "-raw", str(PDF), "-"], check=True,
                     capture_output=True, text=True).stdout.replace("\f", "\n")
lines = []
for l in raw.split("\n"):
    s = l.strip()
    if not s: continue
    if s.startswith("This publication is available free of charge"): continue
    if re.match(r"^(CHAPTER THREE|APPENDIX [A-Z]|NIST SP 800-171A|ASSESSING SECURITY REQUIREMENTS FOR CONTROLLED|PAGE \d+)\b", s): continue
    if re.fullmatch(r"_+", s): continue
    if re.fullmatch(r"\d+\.\d+ [A-Z ,]+", s): continue          # family headers
    lines.append(s)

start = next(i for i, l in enumerate(lines) if re.fullmatch(r"3\.1\.1\s+SECURITY REQUIREMENT", l))
lines = lines[start:]

hyphen_joins = []
def join(acc, l, where):
    if not acc: return l
    if acc.endswith("-"):
        hyphen_joins.append({"where": where, "text": acc.split()[-1] + l.split()[0]})
        return acc + l
    return acc + " " + l

ctrl = {}; cur = None; mode = None; key = None
for l in lines:
    m = re.fullmatch(r"(3\.\d+\.\d+)\s+SECURITY REQUIREMENT", l)
    if m:
        cur = m[1]; ctrl[cur] = {"statement": "", "objectives": collections.OrderedDict(),
                                 "examine": "", "interview": "", "test": ""}
        mode = "stmt"; key = None; continue
    if cur is None: continue
    if l.startswith("ASSESSMENT OBJECTIVE"): mode = "objhdr"; key = None; continue
    m1 = re.match(r"^Determine if\s+(.+)$", l)
    if m1:                                   # single-objective form: no [a] label
        mode = "obj"; key = "a"; ctrl[cur]["objectives"]["a"] = m1[1]; continue
    if l.startswith("Determine if"): mode = "obj"; key = None; continue
    if l.startswith("POTENTIAL ASSESSMENT METHODS"): mode = "meth"; key = None; continue
    if l.startswith("APPENDIX") or l == "REFERENCES": cur = None; continue
    mo = re.match(r"^" + re.escape(cur) + r"\[([a-z])\]\s*(.*)$", l)
    if mode == "obj" and mo:
        key = mo[1]; ctrl[cur]["objectives"][key] = mo[2]; continue
    if mode == "obj" and key is not None:
        ctrl[cur]["objectives"][key] = join(ctrl[cur]["objectives"][key], l, f"{cur}[{key}]"); continue
    if mode == "meth":
        mm = re.match(r"^(Examine|Interview|Test):\s*(.*)$", l)
        if mm: key = mm[1].lower(); ctrl[cur][key] = mm[2]; continue
        if key: ctrl[cur][key] = join(ctrl[cur][key], l, f"{cur} {key}"); continue
    if mode == "stmt": ctrl[cur]["statement"] = join(ctrl[cur]["statement"], l, f"{cur} statement")

objs = sum(len(v["objectives"]) for v in ctrl.values())
assert len(ctrl) == 110, len(ctrl)
assert objs == 320, objs
for k, v in ctrl.items():
    assert v["examine"] and v["interview"] and v["test"], f"{k} missing a method"
    assert list(v["objectives"]) == [chr(97 + i) for i in range(len(v["objectives"]))], k

out = {"source": {"file": PDF.name, "sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
                  "extractor": "pdftotext -raw (poppler)"},
       "hyphen_joins": hyphen_joins, "controls": ctrl}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"extracted 110 requirements, {objs} objectives; {len(hyphen_joins)} hyphen joins listed for review")
