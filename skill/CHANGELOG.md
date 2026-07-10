# Changelog — WCAG Contrast Audit

All notable changes to this skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

Per-version dates were not preserved in the original package and are not recorded below —
only the version history itself, as retained in the shipped manifest.

---

## [2.0.1] — 2026-07-10

### Added
- Bundled `skill/LICENSE.txt` (MIT) — conforms to the v2.1.0 `.aiskill` spec's
  optional bundled license file

## [2.0.0]

### Changed
- **BREAKING:** `CARD.md` is now a third REQUIRED package file, alongside `manifest.yaml` and
  `SKILL.md` — generated deterministically by `build_card.py` from `manifest.yaml`

## [1.1.4]

### Fixed
- Cover page meta layout — each field now on its own row (label left, value right)
- Tool name displayed as a single unbroken line (`WCAG-CONTRAST-AUDIT-x.x.x.aiskill`)

### Added
- Audit Tool URL as a dedicated cover field

## [1.1.3]

### Fixed
- Results table overflow in PDF output — `table-layout:fixed` so column percentages are strictly respected
- Long selectors bursting table columns — added `word-break` and `overflow:hidden` to body cells
- HTML report rendered without gutters in a browser — added browser-only body margins via `@media screen`

## [1.1.2]

### Fixed
- Implicit pair explosion on large CSS files (6000+ lines)
- Removed the dominant-background heuristic; implicit pairs are now only tested against white
- Reduced a real-world 491 spurious pairs down to 38 credible pairs on a large test site
- Explicit co-declared pairs (foreground + background in the same rule) were unaffected by this fix

## [1.1.1]

### Added
- Per-file include control via `--include-css FILENAME [FILENAME ...]`
- Per-excluded-file AI re-run instruction in the Scope & Limitations table
- Re-download instruction in the accountability panel (Ctrl+S / Cmd+S workflow)
- Transparent console reporting of skipped files

### Changed
- `*.min.css` files excluded from the audit by default; `--include-min-css` to include all

## [1.1.0]

### Added
- `generate_report.py` — one-command end-to-end report generator
- `assets/templates/report-template.html` — portable HTML report template (plain hex colours only — no `color-mix()`, no CSS gradients — for identical rendering across WeasyPrint, wkhtmltopdf, and Puppeteer)
- Automatic site domain extraction, CSS discovery, and colour pairing from stylesheets
- Output naming: `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.html` + `.pdf`
- Quick-start workflow and template token reference in `SKILL.md`
- Skill reference URL added to all report output

## [1.0.0]

### Added
- Initial release — contrast calculator (`wcag_contrast.py`) and manual audit procedure
