#!/usr/bin/env python3
"""Build the combined catalog deterministically from sources.

  sources/cprt_SP_800_171_2_0_0_*.json   NIST CPRT export of SP 800-171 Rev 2
                                          -> requirement statements, discussion,
                                             basic/derived type (AUTHORITATIVE)
  sources/baseline-2025-11-19.json        internal baseline
                                          -> OSCAL skeleton, SP 800-171A objectives
                                             and assessment procedures

Every repair applied to source text is listed in REPAIRS / ADDITIONS below so
it is visible in the diff of this file, never hidden in the output.
"""
import json, re, sys, glob, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CPRT = sorted(glob.glob(str(ROOT / "sources/cprt_SP_800_171_2_0_0_*.json")))[-1]
BASELINE = ROOT / "sources/baseline-2025-11-19.json"
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

# --- repairs to baseline 171A text -------------------------------------------
MOJIBAKE = {"â€™": "\u2019", "â€œ": "\u201c", "â€\x9d": "\u201d", "â€\u201d": "\u2014"}
def repair_baseline_text(s: str) -> str:
    for a, b in MOJIBAKE.items():
        s = s.replace(a, b)
    s = re.sub(r"\s{2,}", " ", s).strip()
    if s and not s.endswith("."):
        s += "."
    return s

# --- SP 800-171A content missing from the baseline ---------------------------
# VERIFY AGAINST SP 800-171A PDF BEFORE FINAL RELEASE.
ADDITIONS = {
    "3.1.19": {"assessment":
        "**EXAMINE:** [SELECT FROM: Access control policy; procedures addressing access control for mobile devices; system design documentation; system configuration settings and associated documentation; encryption mechanisms and associated configuration documentation; system audit logs and records; other relevant documents or records].\n"
        "**INTERVIEW:** [SELECT FROM: Personnel with access control responsibilities for mobile devices; system or network administrators; personnel with information security responsibilities].\n"
        "**TEST:** [SELECT FROM: Encryption mechanisms protecting confidentiality of information on mobile devices]."},
    "3.6.3": {"assessment_append":
        "\n**TEST:** [SELECT FROM: Mechanisms and processes for incident response]."},
}

def label_of(cid):  # _03.01.01 -> 3.1.1
    return ".".join(str(int(x)) for x in cid.lstrip("_").split("."))

def main():
    cprt = json.load(open(CPRT, encoding="utf-8"))["response"]["elements"]
    stmt = {e["element_identifier"]: e["text"] for e in cprt["elements"] if e["element_type"] == "requirement"}
    disc = {e["element_identifier"][2:]: e["text"] for e in cprt["elements"] if e["element_type"] == "discussion"}
    rtype = {r["source_element_identifier"]: r["dest_element_identifier"][3:]
             for r in cprt["relationships"] if r["dest_element_identifier"].startswith("RT_")}
    assert len(stmt) == 110 and len(disc) == 110 and len(rtype) == 110

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
            parts = []
            for p in c["parts"]:
                if p["name"] == "statement":
                    p["prose"] = s
                elif p["name"] == "guidance":
                    p["prose"] = d
                else:
                    p["prose"] = repair_baseline_text(p["prose"])
                parts.append(p)
            add = ADDITIONS.get(lab, {})
            if "assessment" in add and not any(p["name"] == "assessment" for p in parts):
                parts.append({"name": "assessment", "prose": add["assessment"]})
            if "assessment_append" in add:
                for p in parts:
                    if p["name"] == "assessment" and "**TEST:**" not in p["prose"]:
                        p["prose"] = p["prose"].rstrip() + add["assessment_append"]
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
