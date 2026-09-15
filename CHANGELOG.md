# Changelog

All notable changes to this catalog are recorded here. Versions follow
`<oscal-content-version>-combined.<patch>`; the catalog is Rev 2 throughout.

## [2.0-combined.1] — 2026-09-15

First public, attested release.

### Changed
- Requirement statements and discussion text are now sourced verbatim from
  NIST's CPRT export of SP 800-171 Rev 2 (`SP_800_171_2_0_0`) rather than
  from the earlier PDF-derived baseline. See DIFFERENCES.md.

### Fixed (against the 2025-11-19 baseline)
- 3.13.12 carried the statement and discussion text of 3.13.11. Replaced with
  the correct text. Objectives and procedures were already correct.
- Eight truncated or altered requirement statements restored to Rev 2 text:
  3.1.1, 3.4.1, 3.4.8, 3.11.1, 3.13.1, 3.13.14 (cut at a parenthetical);
  3.13.6, 3.13.7 (trailing `(i.e., ...)` clause dropped).
- Three statements used Rev 1 wording; replaced with Rev 2: 3.1.21, 3.2.2,
  3.5.4.
- Parentheses restored in 3.1.11 and 3.5.2; comma restored in 3.3.2.
- Added the missing assessment procedure for 3.1.19 and the missing TEST
  procedure for 3.6.3 (SP 800-171A).
- Repaired 13 double-encoded UTF-8 sequences in discussion text; curly
  quotation marks and apostrophes restored as published by NIST.
- Restored spacing at 41 collapsed paragraph boundaries and repaired three
  line-break hyphenation artifacts (`point-of-origin`, `cloud-based`,
  `in-house`). These artifacts are present in the CPRT export itself.
- Normalized terminal punctuation and trailing whitespace on all statements
  and objectives.

### Added
- `label`, `sort-id`, and `requirement-type` (basic/derived) props on every
  control.
- `class: family` on every group.
- Schema validation and count assertions in CI.
- Signed build-provenance attestation on release artifacts.

### Unchanged (deliberately)
- NIST's original typographical errors in discussion text (e.g. "verses" in
  3.1.1) are preserved as published.
- Control identifiers retain the leading-underscore, zero-padded form
  (`_03.01.01`).

## [2.0-combined] — 2025-11-19

Internal baseline. Not published.
