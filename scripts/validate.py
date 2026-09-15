#!/usr/bin/env python3
"""Validate the catalog against the official OSCAL catalog JSON schema and
assert the expected SP 800-171 Rev 2 counts. Mirrors the CI job."""
import json, sys, urllib.request
import jsonschema, regex

# The OSCAL schema uses \p{...} Unicode classes, which Python's `re` cannot
# parse. Point jsonschema's pattern checker at the `regex` module instead.
# The module holding it has moved between jsonschema releases.
_patched = False
for _name in ("jsonschema._keywords", "jsonschema._validators"):
    try:
        _mod = __import__(_name, fromlist=["re"])
        _mod.re = regex
        _patched = True
    except ImportError:
        pass
if not _patched:
    sys.exit("could not patch jsonschema regex engine; jsonschema version unsupported")

OSCAL_VERSION = "1.1.2"
SCHEMA_URL = (f"https://github.com/usnistgov/OSCAL/releases/download/"
              f"v{OSCAL_VERSION}/oscal_catalog_schema.json")

path = sys.argv[1]
schema = json.load(urllib.request.urlopen(SCHEMA_URL))
doc = json.load(open(path, encoding="utf-8"))

errs = list(jsonschema.Draft7Validator(schema).iter_errors(doc))
for e in errs:
    print("/".join(map(str, e.path)), "->", e.message)
if errs:
    sys.exit(f"{len(errs)} schema error(s)")

c = doc["catalog"]
ctrls = [x for g in c["groups"] for x in g["controls"]]
objs = sum(1 for x in ctrls for p in x["parts"] if p["name"] == "objective")
assert len(c["groups"]) == 14, f"groups: {len(c['groups'])}"
assert len(ctrls) == 110, f"controls: {len(ctrls)}"
assert objs == 320, f"objectives: {objs}"
print("OK: 14 families, 110 requirements, 320 objectives, schema-valid")
