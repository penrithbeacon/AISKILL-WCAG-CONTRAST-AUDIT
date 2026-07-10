# AISKILL-WCAG-CONTRAST-AUDIT

**WCAG Contrast Audit** — Audits foreground/background colour pairs against WCAG 2.1/2.2 AA and AAA contrast ratios and generates a professional PDF report from a saved HTML page in one command.

Audits every foreground/background colour pair on a saved web page against WCAG 2.1/2.2 AA and AAA contrast ratio thresholds — AA (4.5:1 normal text, 3.0:1 large text) and AAA (7.0:1 / 4.5:1) — and produces a professional, deterministic HTML report plus a derived PDF, extracting the page's linked CSS and identifying colour pairs automatically rather than requiring them to be listed by hand. Minified framework CSS is excluded by default, since auditing every colour a framework declares produces thousands of phantom failures rather than a usable result.

Reach for this whenever WCAG contrast compliance needs to be demonstrated, documented, or fixed for a real site — including EN 301 549 / EAA (European Accessibility Act) audits, which reference the same SC 1.4.3 and SC 1.4.6 success criteria this skill checks against. A manual CSV-driven path is also available for auditing a specific list of colour pairs outside a full page context.

Ships with a pytest suite covering the contrast-ratio calculator itself, and the HTML/PDF report is generated from the same fixed template every run, so the same input page always produces the same report. Carries the same SYSTEM.md external-registry verification as every other package in this ecosystem.

| | |
|---|---|
| Version | `2.0.3` |
| License | `MIT` |
| Author | Anthony Harrison |
| Homepage | https://openaiskillpackage.com/ |
| Spec | [Open AI Skill Package Specification](https://openaiskillpackage.com/) |

---

## What This Skill Does

Audits every foreground/background colour pair on a web page against WCAG 2.1/2.2 contrast
ratio requirements — AA (4.5:1 normal text, 3.0:1 large text) and AAA (7.0:1 / 4.5:1) — and
produces a professional, deterministic report.

Give the agent a saved copy of a page (browser "Save As → Webpage, Complete"), and one
command extracts the site's linked CSS, identifies explicit and implicit colour pairs,
runs the audit, and writes both an HTML report (the authoritative output) and a PDF
(a derived, best-effort artefact — rendering can vary slightly between WeasyPrint,
wkhtmltopdf, and Puppeteer). Minified framework CSS (Bootstrap, Tailwind, etc.) is excluded
by default, since auditing every colour a framework defines — most of which never appear
on the page — produces thousands of phantom failures rather than a usable result.

Use this when you need to demonstrate, document, or fix WCAG contrast compliance for a real
site — including EN 301 549 / EAA (European Accessibility Act) audits, which reference the
same SC 1.4.3 and SC 1.4.6 success criteria this skill checks against.

---

## Prerequisites

Before using this skill, ensure the following are available in the AI agent's environment:

- Python 3.8 or later
- A PDF renderer (optional but recommended): `pip install weasyprint` (preferred), or
  `wkhtmltopdf` via your OS package manager, or `npm install puppeteer`. Without one,
  the HTML report is still produced and the PDF step is skipped with install instructions.

---

## Quick Start

1. Download `WCAG-CONTRAST-AUDIT-2.0.3.aiskill` from the [Releases](https://github.com/PenrithBeacon/AISKILL-WCAG-CONTRAST-AUDIT/releases) page
2. Give your AI agent the following prompt:

```
Using the Skill Package at /path/to/WCAG-CONTRAST-AUDIT-2.0.3.aiskill,
[describe what you want the skill to do, e.g. 'audit the contrast of /path/to/saved-page.html']
```

---

## Skill Archive Contents

```
WCAG-CONTRAST-AUDIT-2.0.3.aiskill  (ZIP archive)
├── manifest.yaml          # identity & metadata
├── SKILL.md               # AI entry point — execution instructions
├── README.md              # this file — byte-identical to the repo-root copy
├── CHANGELOG.md           # version history
├── checksums.yaml         # SHA-256 integrity hashes
├── assets/
│   ├── scripts/
│   │   ├── generate_report.py   # one-command end-to-end report generator
│   │   └── wcag_contrast.py     # contrast calculator (manual/CSV audit path)
│   ├── templates/
│   │   └── report-template.html # portable HTML report template
│   └── tests/
│       └── test_wcag_contrast.py
└── inputs/
    ├── schema.json         # input schema
    └── example-pairs.csv   # example fg,bg,label CSV for the manual audit path
```

---

## Development Workflow

To modify and repackage this skill:

```bash
# 1. Clone the source
git clone https://github.com/PenrithBeacon/AISKILL-WCAG-CONTRAST-AUDIT.git
cd AISKILL-WCAG-CONTRAST-AUDIT

# 2. Edit skill files in skill/
#    - skill/SKILL.md       — execution instructions
#    - skill/assets/scripts/ — the computation
#    - skill/assets/tests/   — unit tests

# 3. Run tests (must pass before packaging)
python3 -m pytest skill/assets/tests/ -v

# 4. Package
python3 skill/assets/scripts/pack.py \
  --skill-dir skill/ \
  --dist-dir dist/

# 5. Bump version in skill/manifest.yaml, update skill/CHANGELOG.md

# 6. Commit, tag, and release
git add -A
git commit -m "feat: WCAG-CONTRAST-AUDIT v[NEW-VERSION]"
git push origin main
git tag v[NEW-VERSION]
git push origin v[NEW-VERSION]
gh release create v[NEW-VERSION] dist/WCAG-CONTRAST-AUDIT-[NEW-VERSION].aiskill \
  --title "v[NEW-VERSION]" --notes "..."
```

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## License

MIT

---

## Contact

**Anthony Harrison**
For questions or contributions, open an issue on [GitHub](https://github.com/PenrithBeacon/AISKILL-WCAG-CONTRAST-AUDIT).
