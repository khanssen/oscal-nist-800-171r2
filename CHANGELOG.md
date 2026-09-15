# Changelog

All notable changes to this catalog are recorded here. Versions follow
`<oscal-content-version>-combined.<patch>`; the catalog is Rev 2 throughout.

## [2.0-combined.1] — 2026-09-15

First public, attested release. Every text field now traces to a NIST source.

### Changed
- Requirement statements and discussion text are sourced verbatim from NIST's
  CPRT export of SP 800-171 Rev 2 (`SP_800_171_2_0_0`).
- Assessment objectives and Examine / Interview / Test procedures are sourced
  from the SP 800-171A PDF via `scripts/extract_171a.py`; the extracted text is
  committed in `sources/` and asserted against on every build.
- Statement parts now carry an id (`<control>_smt`), matching OSCAL convention.

### Fixed (against the 2025-11-19 baseline) — see CORRECTIONS.md
- 3.13.12 carried the statement and discussion of 3.13.11.
- Eight truncated or altered statements restored (3.1.1, 3.4.1, 3.4.8, 3.11.1,
  3.13.1, 3.13.14, 3.13.6, 3.13.7); three Rev 1 wordings replaced (3.1.21,
  3.2.2, 3.5.4); parentheses and a comma restored (3.1.11, 3.5.2, 3.3.2).
- The 800-171A layer was not verbatim: 58 objectives and 157 procedure texts
  differed from the PDF, 3.1.19 had no procedure, 3.6.3 had no TEST. Dominant
  patterns: "security plan" for "system security plan"; single-objective
  requirements carrying the requirement text instead of the determination
  statement; 3.1.17 objectives swapped; 3.11.2 reworded. All replaced.
- 13 double-encoded UTF-8 sequences, 41 collapsed paragraph breaks, three
  line-break hyphenation artifacts, and punctuation/whitespace normalized.

### Added
- `label`, `sort-id`, and `requirement-type` (basic/derived) props on every
  control; `class: family` on every group.
- Build-driven repo: `scripts/build.py`, `diff_baseline.py`, `diff_cprt.py`,
  `extract_171a.py`; CI fails on drift between sources and committed outputs.
- Signed build-provenance attestation on release artifacts.

### Unchanged (deliberately)
- NIST's original typographical errors (e.g. "verses" in 3.1.1) are preserved.
- Control identifiers retain the leading-underscore, zero-padded form.

## [2.0-combined] — 2025-11-19

Internal baseline. Not published.
