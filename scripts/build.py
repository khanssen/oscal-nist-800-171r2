#!/usr/bin/env python3
"""Build the combined catalog deterministically from sources.

  sources/cprt_SP_800_171_2_0_0_*.json   NIST CPRT export of SP 800-171 Rev 2
                                          -> requirement statements, discussion,
                                             basic/derived type (AUTHORITATIVE)
  sources/sp800-171a-extracted.json       extracted from the SP 800-171A PDF by
                                          scripts/extract_171a.py
                                          -> assessment objectives and Examine /
                                             Interview / Test procedures (AUTHORITATIVE)
  sources/baseline-2025-11-19.json        internal baseline
                                          -> OSCAL skeleton (groups, control and part
                                             ids, part layout) only

Every repair applied to source text is listed in HYPHEN_REPAIRS / repair_cprt_text below so
it is visible in the diff of this file, never hidden in the output.
"""
import json, re, sys, glob, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CPRT = sorted(glob.glob(str(ROOT / "sources/cprt_SP_800_171_2_0_0_*.json")))[-1]
BASELINE = ROOT / "sources/baseline-2025-11-19.json"
A171 = ROOT / "sources/sp800-171a-extracted.json"
OUT = ROOT / "catalog/nist-sp-800-171r2-combined-catalog.json"
VERSION = "2.0-combined.1"

# --- repairs to CPRT text: PDF-extraction artifacts only --------------------
HYPHEN_REPAIRS = {
    "point-oforigin": "point-of-origin",   # 3.1.2 discussion
    "cloudbased": "cloud-based",           # 3.3.1 discussion
    "in- house": "in-house",               # 3.7.3 discussion
}
def repair_cprt_text(s: str) -> str:
    s = re.sub(r"([a-z\)0-9])\.([A-Z])", r"\1. \2", s)   # collapsed paragraph breaks
    s = re.sub(r"\s{2,}", " ", s).strip()                 # double spaces
    for a, b in HYPHEN_REPAIRS.items():
        s = s.replace(a, b)
    return s

def assessment_prose(a):
    """Single markdown part, matching the baseline's layout."""
    return (f"**EXAMINE:** {a['examine']}\n"
            f"**INTERVIEW:** {a['interview']}\n"
            f"**TEST:** {a['test']}")

def label_of(cid):  # _03.01.01 -> 3.1.1
    return ".".join(str(int(x)) for x in cid.lstrip("_").split("."))

def main():
    cprt = json.load(open(CPRT, encoding="utf-8"))["response"]["elements"]
    stmt = {e["element_identifier"]: e["text"] for e in cprt["elements"] if e["element_type"] == "requirement"}
    disc = {e["element_identifier"][2:]: e["text"] for e in cprt["elements"] if e["element_type"] == "discussion"}
    rtype = {r["source_element_identifier"]: r["dest_element_identifier"][3:]
             for r in cprt["relationships"] if r["dest_element_identifier"].startswith("RT_")}
    assert len(stmt) == 110 and len(disc) == 110 and len(rtype) == 110

    a171 = json.load(open(A171, encoding="utf-8"))["controls"]
    assert len(a171) == 110 and sum(len(v["objectives"]) for v in a171.values()) == 320

    doc = json.load(open(BASELINE, encoding="utf-8"))
    cat = doc["catalog"]
    for g in cat["groups"]:
        g["class"] = "family"
        for c in g["controls"]:
            cid = c["id"]; lab = label_of(cid)
            s = stmt[lab].strip(); d = repair_cprt_text(disc[lab])
            c["title"] = s
            props = [{"name": "label", "value": lab},
                     {"name": "sort-id", "value": cid.lstrip("_")},
                     {"name": "requirement-type", "ns": "https://archstonesecurity.com/ns/oscal", "value": rtype[lab]}]
            a = a171[lab]
            parts = [{"id": f"{cid}_smt", "name": "statement", "prose": s},
                     {"id": f"{cid}_disc", "name": "guidance", "prose": d}]
            for letter, text in a["objectives"].items():
                parts.append({"id": f"{cid}_obj.{letter}", "name": "objective", "prose": text})
            parts.append({"name": "assessment", "prose": assessment_prose(a)})
            c.clear()
            c.update({"id": cid, "title": s, "props": props, "parts": parts})

    md = cat["metadata"]
    md["title"] = "NIST SP 800-171 Rev 2 Combined \u2014 Security Requirements with Assessment Procedures"
    md["version"] = VERSION
    md["oscal-version"] = "1.1.2"
    # last-modified is the CPRT export date, not build time, so builds are reproducible
    md["last-modified"] = re.search(r"(\d{4}-\d{2}-\d{2})", CPRT).group(1) + "T00:00:00Z"

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ctrls = [c for g in cat["groups"] for c in g["controls"]]
    objs = sum(1 for c in ctrls for p in c["parts"] if p["name"] == "objective")
    print(f"built {OUT.name}: {len(cat['groups'])} families, {len(ctrls)} controls, {objs} objectives")

if __name__ == "__main__":
    main()
