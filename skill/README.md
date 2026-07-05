# WCAG Contrast Audit

Audits foreground/background colour pairs against WCAG 2.1/2.2 AA and AAA contrast ratios and generates a professional PDF report from a saved HTML page in one command.

**Version:** 1.1.4
**License:** MIT
**Author:** Anthony Harrison
**Homepage:** https://openaiskillpackage.com/

---

## Prerequisites

- Python 3.8+
- A PDF renderer, in order of preference: [WeasyPrint](https://weasyprint.org/) (`pip install weasyprint`), `wkhtmltopdf`, or Puppeteer (`npm install puppeteer`). If none is available, the HTML report is still written and the PDF step is skipped with install instructions.

---

## Quick Start

Save the target page with your browser's **Save As → Webpage, Complete**, then:

```bash
python3 assets/scripts/generate_report.py --html "/path/to/saved-page.html"
```

This extracts the site domain, discovers linked CSS files, identifies colour pairs, runs the audit, and writes both an HTML report and (if a renderer is available) a PDF alongside the input file.

---

## Inputs

The primary entry point (`generate_report.py`) takes a saved HTML page and its accompanying CSS files — no separate input file is required. See `inputs/schema.json` for the formal definition, and `inputs/example-pairs.csv` for the `fg,bg,label` CSV format accepted by the lower-level `wcag_contrast.py --csv` path (Step 4 in `SKILL.md`).

---

## Output

| File | Description |
|------|--------------|
| `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.html` | Normative output — deterministic across platforms. This is the source of truth. |
| `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.pdf` | Derived artefact — may vary slightly by renderer and OS fonts. |

Both are written to the same directory as the input HTML file.

---

## Source Repository

https://github.com/PenrithBeacon/AISKILL-WCAG-CONTRAST-AUDIT
