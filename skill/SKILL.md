# WCAG Contrast Audit

Audit the foreground/background colour pairs on any web page against WCAG 2.1/2.2
contrast ratio requirements at AA and AAA levels, and generate a professional PDF report.

Available from **https://openaiskillpackage.com/**

---

## Quick start (one command)

```bash
python3 assets/scripts/generate_report.py --html /path/to/saved-page.html
```

This single command:
- Extracts the site domain from the saved HTML
- Discovers and parses linked CSS files in the same directory
- Identifies colour pairs from the stylesheet(s)
- Runs the WCAG contrast audit
- Writes `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.html` alongside the input file
- Attempts PDF conversion automatically (WeasyPrint → wkhtmltopdf → Puppeteer)

---

## Detailed procedure

### Step 1 — Obtain the page

Save the target page locally using your browser's **Save As → Webpage, Complete** option.
This downloads the HTML file and an accompanying asset directory containing the CSS files.

### Step 2 — Run the report generator

```bash
python3 assets/scripts/generate_report.py --html "/path/to/saved-page.html"
```

Optional: override the report date:
```bash
python3 assets/scripts/generate_report.py --html "/path/to/saved-page.html" --date 2026-07-03
```

Optional: include third-party framework CSS files in the audit (off by default — see note below):
```bash
python3 assets/scripts/generate_report.py --html "/path/to/saved-page.html" --include-min-css
```

The script prints a summary as it runs:

```
WCAG-CONTRAST-AUDIT-1.1.4.aiskill | https://openaiskillpackage.com/
Input: Home _ My Site.html
Site:  mysite.com
Skip:  bootstrap.min.css, swiper-bundle.min.css (framework CSS — use --include-min-css to include)
CSS:   styles.css, theme.css
Pairs: 18 extracted
Audit: 12 AA pass, 6 AA fail, 14 AAA fail
HTML:  /path/to/WCAG-Contrast-Audit-Report-mysite.com-2026-07-03.html
  [PDF] WeasyPrint → WCAG-Contrast-Audit-Report-mysite.com-2026-07-03.pdf
Done.
```

### Step 3 — PDF renderer (agent responsibility)

The agent running this skill is responsible for ensuring a PDF renderer is available.
The script tries in this order:

| Renderer | Install |
|----------|---------|
| WeasyPrint (recommended) | `pip install weasyprint` |
| wkhtmltopdf | `brew install wkhtmltopdf` (macOS) · `apt install wkhtmltopdf` (Linux) |
| Puppeteer | `npm install puppeteer` (requires Node.js) |

If none is available the HTML report is still written; the PDF is skipped with instructions.

### Step 4 — Manual audit (advanced)

To run the contrast calculator directly on specific pairs:

```bash
python3 assets/scripts/wcag_contrast.py --pairs "#353535,#FFFFFF" "#10b981,#0f1117"
```

Or pass a CSV with `fg,bg,label` columns:

```bash
python3 assets/scripts/wcag_contrast.py --csv inputs/example-pairs.csv
```

Add `--json` for machine-readable output.

---

## Output files

Both output files are written to the **same directory as the input HTML file**.

| File | Description |
|------|-------------|
| `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.html` | Normative output — deterministic across platforms |
| `WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.pdf` | Derived artefact — may vary slightly by renderer and OS fonts |

**The HTML file is the authoritative output.** PDF rendering may differ between WeasyPrint,
wkhtmltopdf, and Puppeteer (particularly font metrics and page breaks), so the HTML is the
source of truth for audit results.

---

## Colour pair extraction

The generator uses static CSS analysis to identify colour pairs:

1. **Explicit pairs**: CSS rules that declare both `color` and `background(-color)` in the
   same block — unambiguously paired by the stylesheet author.
2. **Implicit pairs**: Text colours without an explicit background pairing are tested against
   `#FFFFFF` (universally present as a default).

**Framework CSS exclusion (default behaviour):** Minified CSS files (`*.min.css`) are excluded
from the audit by default. These files are virtually always third-party frameworks (Bootstrap,
Tailwind, Font Awesome, Swiper, etc.) that define colours for every component they offer —
most of which never appear on any given page. Including them produces hundreds or thousands of
phantom pairs from unused utilities, inflating the failure count to meaningless levels.
The site's own CSS is almost never minified and accurately reflects the design palette.
Use `--include-min-css` only if you specifically need to audit framework component colours.

**Limitation on cascade**: Cascaded relationships (e.g. `<p>` inheriting background from
`<body>`) cannot be resolved by static analysis. Explicit co-declarations are the most reliable
subset. For complex cascade scenarios, use the manual procedure (Step 4) with pairs constructed
from browser DevTools inspection.

---

## Report template

The embedded report template (`assets/templates/report-template.html`) uses:

- **Token syntax**: `<<<TOKEN_NAME>>>` (avoids collision with CSS `{}` syntax)
- **CSS constraints**: no `color-mix()`, no CSS gradients, no `@page` margin boxes —
  ensures identical rendering across WeasyPrint, wkhtmltopdf, and Puppeteer
- **Layout**: `<table>`-based multi-column sections for maximum cross-renderer portability

### Template tokens

| Token | Description |
|-------|-------------|
| `<<<SITE_URL>>>` | Extracted domain (e.g. `mysite.com`) |
| `<<<REPORT_DATE>>>` | Formatted date (e.g. `3 July 2026`) |
| `<<<SKILL_VERSION>>>` | Skill version (e.g. `1.1.0`) |
| `<<<TOTAL_PAIRS>>>` | Total colour pairs tested |
| `<<<PASS_COUNT>>>` | Pairs passing WCAG AA Normal |
| `<<<FAIL_COUNT>>>` | Pairs failing WCAG AA Normal |
| `<<<AAA_FAIL_COUNT>>>` | Pairs failing WCAG AAA Normal |
| `<<<PAIR_COUNT>>>` | Same as TOTAL_PAIRS (used in methodology section) |
| `<<<CSS_FILES_AUDITED>>>` | Comma-separated list of CSS source filenames |
| `<<<EXECUTIVE_SUMMARY>>>` | Auto-generated opening paragraph |
| `<<<EXECUTIVE_DETAIL>>>` | Auto-generated context paragraph |
| `<<<RESULTS_TABLE_ROWS>>>` | HTML `<tr>` rows for the full results table |
| `<<<FAIL_INTRO>>>` | Intro paragraph for Section 4 |
| `<<<FAIL_CARDS>>>` | HTML fail card `<div>` blocks with remediation guidance |

---

## WCAG thresholds

| Level | Normal text | Large text (≥18pt or 14pt bold) |
|-------|-------------|----------------------------------|
| AA    | 4.5:1       | 3.0:1                            |
| AAA   | 7.0:1       | 4.5:1                            |

Relative luminance: `L = 0.2126·R + 0.7152·G + 0.0722·B` (sRGB, gamma-corrected)
Contrast ratio: `(L_lighter + 0.05) / (L_darker + 0.05)`

---

## Unit tests

```bash
python3 -m pytest assets/tests/test_wcag_contrast.py -v
```

---

## References

- WCAG 2.1: https://www.w3.org/TR/WCAG21/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- EN 301 549 v3.2.1 (EAA harmonised standard)
- SC 1.4.3 — Contrast (Minimum): https://www.w3.org/TR/WCAG21/#contrast-minimum
- SC 1.4.6 — Contrast (Enhanced): https://www.w3.org/TR/WCAG21/#contrast-enhanced
- EAA Directive 2019/882/EU — enforcement from 28 June 2025
- This skill: https://openaiskillpackage.com/
