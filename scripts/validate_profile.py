#!/usr/bin/env python3
"""Validate the profile against the official OSCAL profile JSON schema, then
resolve its catalog import locally and assert it selects all 110 requirements."""
import json, os, sys, urllib.request
import jsonschema, regex

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
              f"v{OSCAL_VERSION}/oscal_profile_schema.json")

path = sys.argv[1]
base = os.path.dirname(os.path.abspath(path))
schema = json.load(urllib.request.urlopen(SCHEMA_URL))
doc = json.load(open(path, encoding="utf-8"))

errs = list(jsonschema.Draft7Validator(schema).iter_errors(doc))
for e in errs:
    print("/".join(map(str, e.path)), "->", e.message)
if errs:
    sys.exit(f"{len(errs)} schema error(s)")

p = doc["profile"]
imports = p["imports"]
assert len(imports) == 1, f"imports: {len(imports)}"
href = imports[0]["href"]
if "://" in href:
    sys.exit(f"import href must be a repo-relative path, got {href}")
cat_path = os.path.normpath(os.path.join(base, href))
if not os.path.exists(cat_path):
    sys.exit(f"import href does not resolve: {href} -> {cat_path}")
cat = json.load(open(cat_path, encoding="utf-8"))["catalog"]

expected_uuid = next((pr["value"] for r in p.get("back-matter", {}).get("resources", [])
                      for pr in r.get("props", []) if pr["name"] == "catalog-uuid"), None)
if expected_uuid and expected_uuid != cat["uuid"]:
    sys.exit(f"catalog uuid mismatch: profile expects {expected_uuid}, catalog is {cat['uuid']}")

cat_ids = {x["id"] for g in cat["groups"] for x in g["controls"]}
selected = [i for inc in imports[0].get("include-controls", []) for i in inc.get("with-ids", [])]
missing = sorted(set(selected) - cat_ids)
if missing:
    sys.exit(f"{len(missing)} selected id(s) not in catalog: {missing[:5]}")
assert len(selected) == 110, f"selected: {len(selected)}"
assert len(set(selected)) == 110, "duplicate ids in with-ids"
assert set(selected) == cat_ids, "profile does not select every catalog requirement"
print(f"OK: profile schema-valid, import resolves to {os.path.relpath(cat_path, base)}, 110/110 requirements selected")
