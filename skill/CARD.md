# WCAG Contrast Audit

Audits foreground/background colour pairs against WCAG 2.1/2.2 AA and AAA contrast ratios and generates a professional PDF report from a saved HTML page in one command.

Audits every foreground/background colour pair on a saved web page against
WCAG 2.1/2.2 AA and AAA contrast ratio thresholds -- AA (4.5:1 normal text,
3.0:1 large text) and AAA (7.0:1 / 4.5:1) -- and produces a professional,
deterministic HTML report plus a derived PDF, extracting the page's linked
CSS and identifying colour pairs automatically rather than requiring them
to be listed by hand. Minified framework CSS is excluded by default, since
auditing every colour a framework declares produces thousands of phantom
failures rather than a usable result.

Reach for this whenever WCAG contrast compliance needs to be demonstrated,
documented, or fixed for a real site -- including EN 301 549 / EAA
(European Accessibility Act) audits, which reference the same SC 1.4.3 and
SC 1.4.6 success criteria this skill checks against. A manual CSV-driven
path is also available for auditing a specific list of colour pairs outside
a full page context.

Ships with a pytest suite covering the contrast-ratio calculator itself,
and the HTML/PDF report is generated from the same fixed template every
run, so the same input page always produces the same report. Carries the
same SYSTEM.md external-registry verification as every other package in
this ecosystem.

**Version:** 2.0.3
**Author:** Anthony Harrison
**License:** MIT
**Package ID:** `com.widgetcontextprotocol.wcag-contrast-audit`
**Package UUID:** `18a27cc7-932b-433a-9a3b-b29fe866a84e`
**Homepage:** https://openaiskillpackage.com/

---

## Capabilities

- `filesystem.read`
- `filesystem.write`
- `process.exec`

## Permissions

- **`filesystem.read`** — paths: `*.html`, `*.css`
- **`filesystem.write`** — paths: `*.html`, `*.pdf`

---

*Generated deterministically by `build_card.py` from `manifest.yaml` — do not hand-edit.
Re-run `build_card.py` after any `manifest.yaml` change, before packaging.*
