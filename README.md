# NIST SP 800-171 Rev 2 - Combined OSCAL Catalog

A single OSCAL 1.1.2 catalog containing all 110 security requirements from
**NIST SP 800-171 Revision 2** together with the 320 assessment objectives and
the Examine / Interview / Test procedures from **NIST SP 800-171A**.

> **Revision note:** this catalog is **Rev 2**. Control IDs use leading-zero
> formatting (`03.01.01`) for stable sorting. That formatting does **not**
> indicate Rev 3 content. Rev 3 is a separate catalog with a different
> requirement set.

## Verify before you use it

Every release is built by GitHub Actions and carries a signed provenance
attestation. Verify that the file you hold is the one this repository built:

```sh
gh attestation verify nist-sp-800-171r2-combined-catalog.json --owner khanssen
```

A passing result confirms the file's hash matches an attestation signed for the
`validate-and-release.yml` workflow in this repository at a specific commit.
Any modification to the file, however small, causes verification to fail.

**Offline / air-gapped environments:** `gh attestation verify` queries GitHub
by default. Download the attestation bundle from the release once, then verify
against it locally:

```sh
gh attestation download nist-sp-800-171r2-combined-catalog.json --owner khanssen
gh attestation verify nist-sp-800-171r2-combined-catalog.json --owner khanssen \
  --bundle <downloaded-bundle>.jsonl
```

`SHA256SUMS` is also attached to each release for environments without `gh`.

## What's in the file

| | Count |
|---|---|
| Families (groups) | 14 |
| Security requirements (controls) | 110 |
| Assessment objectives | 320 |
| Assessment procedures | 110 (one per requirement) |

Each control carries:

- `statement` - the requirement text, verbatim from SP 800-171 Rev 2
- `guidance` - the Discussion text, verbatim (including NIST's own typographical
  errors, which are preserved deliberately)
- `objective` parts, `a` through `n` as applicable — the 800-171A determination
  statements
- `assessment` - Examine / Interview / Test with the 800-171A "SELECT FROM" lists
- `props`: `label` (`3.1.1`), `sort-id` (`03.01.01`), and `requirement-type`
  (`basic` or `derived`, in the Archstone namespace)

### Identifier conventions

| Element | Pattern | Example |
|---|---|---|
| Group | `fam-<family>` | `fam-3.1` |
| Control | `_<fam>.<req>` zero-padded | `_03.01.01` |
| Discussion | `<control>_disc` | `_03.01.01_disc` |
| Objective | `<control>_obj.<letter>` | `_03.01.01_obj.a` |

The leading underscore keeps IDs valid OSCAL tokens (tokens may not begin with
a digit). Use the `label` prop when you want the human-readable `3.1.1` form.

## How it's built

The catalog is generated, not hand-edited:

```
sources/   NIST CPRT export of SP 800-171 Rev 2 (as downloaded) + frozen internal baseline
scripts/   build.py -> catalog/   diff_baseline.py -> CORRECTIONS.md   diff_cprt.py -> DIFFERENCES.md
```

Every repair to source text is a named entry in `scripts/build.py`. CI rebuilds
from sources on every push and fails if the committed catalog or generated docs
differ from the build output, then validates against the official OSCAL 1.1.2
schema and asserts the 14 / 110 / 320 counts. Anyone can rebuild and get the
same bytes:

```sh
pip install jsonschema regex
python scripts/build.py && python scripts/diff_baseline.py && python scripts/diff_cprt.py
python scripts/validate.py catalog/nist-sp-800-171r2-combined-catalog.json
```

## Why this exists

NIST does not publish SP 800-171 Rev 2 in OSCAL. The CPRT export of Rev 2
contains the requirement statements and discussion text but none of the
SP 800-171A assessment objectives or procedures, and carries PDF-extraction
artifacts (collapsed paragraph breaks, broken hyphenation). NIST's OSCAL
content covers Rev 3, which is a different requirement set. Rev 2 is what
CMMC Level 2 is assessed against.

This catalog takes the CPRT Rev 2 text as authoritative, repairs the
extraction artifacts, adds the full 800-171A content, and ships the result as
a schema-valid OSCAL catalog with a signed provenance attestation.

- [DIFFERENCES.md](DIFFERENCES.md) — mechanical comparison against the CPRT
  Rev 2 export, including what CPRT does and does not contain.
- [CORRECTIONS.md](CORRECTIONS.md) — field-level record of every change from
  the internal baseline to this release.

## License and notices

The requirement, discussion, and assessment text is a work of the United States
Government (NIST SP 800-171 Rev 2 and SP 800-171A) and is in the public domain.

The OSCAL structure, the combination of 800-171 and 800-171A into a single
catalog, the identifier scheme, corrections, and curation are
© Archstone Security LLC and released under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
See [LICENSE](LICENSE).

**Attribution:** "NIST SP 800-171 Rev 2 Combined OSCAL Catalog, Archstone
Security LLC, https://github.com/khanssen/oscal-nist-800-171r2"

**Trademarks:** ARCHSTONE SECURITY and COMPLIANCE AS INFRASTRUCTURE are
trademarks of Archstone Security LLC. Nothing in the CC BY 4.0 license grants
any right to use these marks.

## Citation

```
Stanford, K. (2026). NIST SP 800-171 Rev 2 Combined OSCAL Catalog
(Version 2.0-combined.1) [Data set]. Archstone Security LLC.
https://github.com/khanssen/oscal-nist-800-171r2
```
