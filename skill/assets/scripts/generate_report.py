#!/usr/bin/env python3
"""
WCAG Contrast Audit Report Generator
Part of WCAG-CONTRAST-AUDIT-1.1.1.aiskill
https://openaiskillpackage.com/

Usage:
    python3 generate_report.py --html /path/to/saved-page.html
    python3 generate_report.py --html /path/to/saved-page.html --date 2026-07-03
    python3 generate_report.py --html /path/to/saved-page.html --include-min-css

The script automatically:
  - Extracts the site domain from the saved HTML (supports browser-saved pages,
    canonical links, og:url, and title fallback)
  - Discovers linked CSS files saved alongside the HTML
  - Extracts foreground/background colour pairs from the CSS
  - Runs the WCAG contrast audit
  - Writes WCAG-Contrast-Audit-Report-{domain}-{YYYY-MM-DD}.html alongside the input file
  - Attempts PDF conversion via WeasyPrint, wkhtmltopdf, or Puppeteer

Output file: HTML is the normative output (deterministic across platforms).
             PDF is a derived artefact and may vary slightly by renderer and OS fonts.
"""

import argparse
import datetime
import html as _html
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_VERSION = "1.1.4"
SKILL_FILENAME = f"WCAG-CONTRAST-AUDIT-{SKILL_VERSION}.aiskill"
SKILL_URL = "https://openaiskillpackage.com/"

_HERE = Path(__file__).parent.resolve()
_TEMPLATE_PATH = _HERE.parent / "templates" / "report-template.html"

sys.path.insert(0, str(_HERE))
import wcag_contrast as _wc


# ── Site URL extraction ───────────────────────────────────────────────────────

def extract_site_url(html: str) -> str:
    """Extract domain from browser-saved page metadata or fallback sources."""
    # Browser-saved: <!-- saved from url=(N)https://example.com/... -->
    m = re.search(r'saved from url=\(\d+\)(https?://[^\s"\'<]+)', html)
    if m:
        raw = m.group(1)
        domain = re.sub(r'^https?://', '', raw).split('/')[0]
        domain = re.sub(r'^www\.', '', domain)
        return domain

    # <link rel="canonical" href="...">
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I)
    if not m:
        m = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', html, re.I)
    if m:
        domain = re.sub(r'^https?://(www\.)?', '', m.group(1)).split('/')[0]
        if domain:
            return domain

    # <meta property="og:url" content="...">
    m = re.search(r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if m:
        domain = re.sub(r'^https?://(www\.)?', '', m.group(1)).split('/')[0]
        if domain:
            return domain

    # <title> — slugify as last resort
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
    if m:
        slug = re.sub(r'[^a-z0-9]+', '-', m.group(1).strip().lower()).strip('-')[:40]
        return slug or 'unknown-site'

    return 'unknown-site'


# ── CSS file discovery ────────────────────────────────────────────────────────

def find_css_files(html: str, html_dir: Path,
                   include_min_css: bool = False,
                   include_css: set | None = None) -> list:
    """
    Return paths of CSS files linked from the HTML that exist locally.

    By default, minified CSS files (*.min.css) are excluded. They are virtually
    always third-party frameworks (Bootstrap, Tailwind, Font Awesome, Swiper, etc.)
    that define colours for hundreds of components, most of which are never rendered
    on any given page. Including them produces thousands of phantom pairs that inflate
    the failure count far beyond what the site's actual design choices warrant.

    include_min_css=True  — include ALL *.min.css files
    include_css={'f.min.css', ...} — include specific named files regardless of pattern
    """
    include_css = include_css or set()
    found = []
    seen = set()
    pattern = re.compile(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+\.css)["\']'
        r'|<link[^>]+href=["\']([^"\']+\.css)["\'][^>]+rel=["\']stylesheet["\']',
        re.I
    )
    for m in pattern.finditer(html):
        href = m.group(1) or m.group(2)
        href = re.sub(r'^https?://[^/]+/', '', href)
        fname = Path(href).name

        if fname.lower().endswith('.min.css') and not include_min_css:
            if fname not in include_css:
                continue

        candidate = (html_dir / href).resolve()
        if candidate.exists() and candidate not in seen:
            found.append(candidate)
            seen.add(candidate)
            continue
        for sub in html_dir.rglob(fname):
            if sub not in seen:
                found.append(sub)
                seen.add(sub)
                break
    return found


# ── Colour normalisation ──────────────────────────────────────────────────────

def _normalise(val: str) -> str | None:
    """Return six-digit uppercase hex or None if unparseable."""
    val = val.strip()
    # 3-digit hex
    m = re.match(r'^#([0-9a-fA-F]{3})$', val)
    if m:
        c = m.group(1)
        return f'#{c[0]*2}{c[1]*2}{c[2]*2}'.upper()
    # 6-digit hex
    m = re.match(r'^#([0-9a-fA-F]{6})$', val)
    if m:
        return f'#{m.group(1).upper()}'
    # 8-digit hex — strip alpha channel
    m = re.match(r'^#([0-9a-fA-F]{6})[0-9a-fA-F]{2}$', val)
    if m:
        return f'#{m.group(1).upper()}'
    # rgb()
    m = re.match(r'^rgb\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)$', val, re.I)
    if m:
        r, g, b = [min(255, int(float(x))) for x in m.groups()]
        return f'#{r:02X}{g:02X}{b:02X}'
    # rgba() — ignore alpha
    m = re.match(r'^rgba\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)', val, re.I)
    if m:
        r, g, b = [min(255, int(float(x))) for x in m.groups()]
        return f'#{r:02X}{g:02X}{b:02X}'
    return None


_BG_SKIP = re.compile(
    r'gradient|^none$|^transparent$|^inherit$|^initial$|^unset$|url\(|var\(|currentcolor',
    re.I
)


# ── Colour pair extraction ────────────────────────────────────────────────────

def extract_pairs(css_blocks: list) -> list:
    """
    Extract (fg, bg, label) dicts from CSS source blocks.

    Strategy:
      1. Explicit pairs: CSS rules that declare both `color` and `background(-color)`
         in the same block — these are definitively paired by the author.
      2. Implicit pairs: text colours with no explicit background pairing are tested
         against #FFFFFF (universally common) and any background that appears in 3+
         rules (a dominant site background).

    Limitation: cascade relationships (e.g. text colour from <p> against body background)
    cannot be resolved from static CSS analysis. Explicit co-declarations are the
    authoritative subset; implicit white-background pairs catch common omissions.
    """
    seen: set = set()
    pairs: list = []
    all_text_cols: list = []

    css = "\n".join(css_blocks)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

    for rule_m in re.finditer(r'([^{}]+)\{([^{}]+)\}', css, re.DOTALL):
        selector = rule_m.group(1).strip()
        decls = rule_m.group(2)

        if re.search(r'@(?:keyframes|font-face|charset)', selector, re.I):
            continue

        text_cols: list = []
        bg_cols: list = []

        for decl in decls.split(';'):
            decl = decl.strip()
            # color:
            mc = re.match(r'^color\s*:\s*(.+)', decl, re.I)
            if mc:
                raw = mc.group(1).split('!')[0].strip()
                h = _normalise(raw)
                if h:
                    text_cols.append(h)
                    all_text_cols.append(h)
            # background / background-color:
            mb = re.match(r'^background(?:-color)?\s*:\s*(.+)', decl, re.I)
            if mb:
                raw = mb.group(1).split('!')[0].strip()
                if _BG_SKIP.search(raw):
                    continue
                h = _normalise(raw)
                if h:
                    bg_cols.append(h)

        label = ' '.join(selector.split())[:60]
        for fg in text_cols:
            for bg in bg_cols:
                key = (fg, bg)
                if key not in seen and fg != bg:
                    seen.add(key)
                    pairs.append({'fg': fg, 'bg': bg, 'label': label})

    # Implicit: orphan text colours (no explicit bg partner) tested against white only.
    # White is the universal browser default and the most common actual background.
    # We deliberately do NOT test against "dominant" backgrounds derived from bg_freq:
    # that heuristic fires too broadly on large CSS files (6000+ lines can have 10+
    # backgrounds each appearing in 3+ rules) and creates hundreds of spurious pairs
    # from colours that never actually appear together on the rendered page.
    # Explicit co-declarations capture those genuine coloured-section cases.
    explicit_fgs = {p['fg'] for p in pairs}
    for tc in dict.fromkeys(all_text_cols):
        if tc in explicit_fgs:
            continue
        key = (tc, '#FFFFFF')
        if key not in seen and tc != '#FFFFFF':
            seen.add(key)
            pairs.append({'fg': tc, 'bg': '#FFFFFF',
                          'label': f'{tc} on white (implicit)'})

    return pairs


# ── Audit runner ──────────────────────────────────────────────────────────────

def run_audit(pairs: list) -> list:
    """Run wcag_contrast.format_row for each pair. Skips unparseable colours."""
    results = []
    for p in pairs:
        try:
            row = _wc.format_row(p['fg'], p['bg'], p.get('label', ''))
            results.append(row)
        except (ValueError, KeyError):
            pass
    return results


# ── HTML rendering helpers ────────────────────────────────────────────────────

def build_scope_rows(tested: list, skipped: list,
                     explicit: set, site_url: str) -> str:
    """
    Build <tr> rows for the scope & limitations table.

    tested   — CSS filenames that were included in the audit
    skipped  — *.min.css filenames that were excluded
    explicit — subset of tested that were explicitly named via --include-css
    site_url — used to generate the per-file AI re-run instruction
    """
    rows = []
    for name in tested:
        if name in explicit:
            classification = (
                'Explicitly included via <code>--include-css</code> &mdash; '
                'results for this file are included in the audit'
            )
            status_html = '<span class="scope-status-pass">Audited</span>'
        elif name.startswith('('):
            classification = 'Inline styles from the HTML page &mdash; always included'
            status_html = '<span class="scope-status-pass">Audited</span>'
        else:
            classification = 'Site stylesheet &mdash; included in this audit'
            status_html = '<span class="scope-status-pass">Audited</span>'
        rows.append(
            '<tr class="scope-audited">'
            f'<td>{status_html}</td>'
            f'<td><code>{_html.escape(name)}</code></td>'
            f'<td>{classification}</td>'
            '</tr>'
        )
    for name in skipped:
        safe_name = _html.escape(name)
        safe_site = _html.escape(site_url)
        rerun_instruction = (
            f'<span class="scope-rerun">To include, instruct your AI agent: '
            f'<em>&ldquo;Re-run the WCAG audit for {safe_site} '
            f'and include {safe_name}.&rdquo;</em></span>'
        )
        rows.append(
            '<tr class="scope-excluded">'
            '<td><span class="scope-status-warn">Excluded</span></td>'
            f'<td><code>{safe_name}</code></td>'
            f'<td>Presumed third-party framework &mdash; excluded by default '
            f'(<code>*.min.css</code> pattern).'
            f'{rerun_instruction}</td>'
            '</tr>'
        )
    if not rows:
        rows.append(
            '<tr><td colspan="3" style="color:#6b7280; font-style:italic;">'
            'No CSS files detected (inline styles only).</td></tr>'
        )
    return '\n'.join(rows)


def _swatch(hex_color: str) -> str:
    return (
        f'<span style="display:inline-block; width:9pt; height:9pt; '
        f'background:{hex_color}; border:1pt solid rgba(0,0,0,0.18); '
        f'vertical-align:middle; margin-right:2pt;"></span>'
    )


def _pf_cell(status: str) -> str:
    cls = 'pass' if status == 'PASS' else 'fail-text'
    return f'<td class="{cls}">{status}</td>'


def build_table_rows(results: list) -> str:
    rows = []
    for i, r in enumerate(results):
        is_fail = r['AA_normal'] == 'FAIL'
        row_cls = ' class="fail-row"' if is_fail else (' class="alt"' if i % 2 else '')
        label = _html.escape(r.get('label', ''))
        rows.append(
            f'<tr{row_cls}>'
            f'<td style="font-size:7.5pt; color:#6b7280;">{label}</td>'
            f'<td>{_swatch(r["foreground"])}<code>{r["foreground"]}</code></td>'
            f'<td>{_swatch(r["background"])}<code>{r["background"]}</code></td>'
            f'<td class="ratio">{r["ratio"]}:1</td>'
            + _pf_cell(r['AA_normal'])
            + _pf_cell(r['AA_large'])
            + _pf_cell(r['AAA_normal'])
            + _pf_cell(r['AAA_large'])
            + '</tr>'
        )
    return '\n'.join(rows)


def build_fail_cards(fails: list) -> str:
    cards = []
    for i, r in enumerate(fails, 1):
        fg, bg = r['foreground'], r['background']
        label = _html.escape(r.get('label', f'Pair {i}'))
        ratio = r['ratio']
        needed = 4.5 if r['AA_normal'] == 'FAIL' else 3.0
        level = 'AA Normal (4.5:1)' if r['AA_normal'] == 'FAIL' else 'AA Large (3:1)'
        shortfall = round(needed - ratio, 2)

        l_fg = _wc.relative_luminance(fg)
        l_bg = _wc.relative_luminance(bg)
        if l_fg < l_bg:
            direction = (f'darken the foreground (<code>{fg}</code>) '
                         f'or lighten the background (<code>{bg}</code>)')
        else:
            direction = (f'lighten the foreground (<code>{fg}</code>) '
                         f'or darken the background (<code>{bg}</code>)')

        cards.append(
            f'<div class="fail-card">'
            f'<h4>Failure {i} &mdash; {label}</h4>'
            f'<p style="font-size:8.5pt; margin-bottom:2mm;">'
            f'{_swatch(fg)}<code>{fg}</code> on {_swatch(bg)}<code>{bg}</code>'
            f' &mdash; measured ratio <strong>{ratio}:1</strong>,'
            f' failing {level} (shortfall: {shortfall}:1).'
            f'</p>'
            f'<div class="fix-box">'
            f'<span class="fix-label">Suggested remediation</span>'
            f'To reach the {needed}:1 threshold, {direction}. '
            f'Use the contrast checker at <strong>webaim.org/resources/contrastchecker</strong> '
            f'to identify a compliant replacement, then re-validate with '
            f'<code>assets/scripts/wcag_contrast.py</code> from '
            f'<code>{SKILL_FILENAME}</code> '
            f'(available from <strong>{SKILL_URL}</strong>).'
            f'</div>'
            f'</div>'
        )
    return '\n'.join(cards)


def build_executive_summary(site: str, total: int, passes: int, fails: int) -> tuple:
    pct = round(100 * fails / total) if total else 0
    summary = (
        f'<p>This report presents the results of an automated WCAG 2.1 colour contrast audit '
        f'of <strong>{_html.escape(site)}</strong>. Of the <strong>{total}</strong> '
        f'foreground/background colour pairs extracted from the page stylesheet(s), '
        f'<strong>{passes}</strong> met the WCAG 2.1 AA minimum contrast threshold of '
        f'4.5:1 for normal text, and <strong>{fails}</strong> did not ({pct}% failure rate).</p>'
    )
    if fails == 0:
        detail = (
            '<p>No WCAG AA contrast failures were detected across the audited colour pairs. '
            'The site demonstrates strong colour contrast compliance at the AA level. '
            'An AAA review or audit of dynamically-applied styles may still be warranted.</p>'
        )
    elif fails <= 3:
        detail = (
            f'<p>The {fails} failure(s) identified represent targeted remediation opportunities. '
            f'Addressing these pairs will bring the audited styles into full WCAG 2.1 AA '
            f'compliance. See Section 4 for specific colour values and remediation guidance.</p>'
        )
    else:
        detail = (
            f'<p>The volume of failures ({fails} of {total} pairs, {pct}%) suggests a systemic '
            f'contrast issue in the site\'s colour palette. A palette-level review &mdash; '
            f'examining base colour tokens or CSS custom properties &mdash; is likely to be more '
            f'efficient than correcting individual declarations. See Section 4 for per-pair '
            f'analysis and remediation direction.</p>'
        )
    return summary, detail


def build_fail_intro(fails: int) -> str:
    if fails == 0:
        return '<p>No WCAG AA failures were detected. No remediation items to report.</p>'
    return (
        f'<p>The {fails} colour pair(s) below fail the WCAG 2.1 AA minimum contrast ratio. '
        f'Each entry identifies the failing colours, the measured shortfall against the '
        f'required threshold, and a remediation direction. Corrections should be validated '
        f'using <code>assets/scripts/wcag_contrast.py</code> bundled within '
        f'<code>{SKILL_FILENAME}</code> (available from <strong>{SKILL_URL}</strong>).</p>'
    )


# ── PDF conversion ────────────────────────────────────────────────────────────

def convert_to_pdf(html_path: Path) -> bool:
    """
    Attempt PDF conversion using available renderers in order of preference:
      1. WeasyPrint  (pip install weasyprint)
      2. wkhtmltopdf (system install)
      3. Puppeteer   (npm install puppeteer)
    Returns True if PDF was produced, False otherwise.
    """
    out = html_path.with_suffix('.pdf')

    # 1. WeasyPrint
    try:
        import weasyprint  # type: ignore
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(out))
        print(f'  [PDF] WeasyPrint → {out.name}')
        return True
    except ImportError:
        pass
    except Exception as exc:
        print(f'  [PDF] WeasyPrint error: {exc}')

    # 2. wkhtmltopdf
    try:
        r = subprocess.run(
            ['wkhtmltopdf', '--enable-local-file-access', '--quiet',
             '--page-size', 'A4',
             '--margin-top', '20mm', '--margin-right', '18mm',
             '--margin-bottom', '22mm', '--margin-left', '18mm',
             str(html_path), str(out)],
            capture_output=True, timeout=60
        )
        if r.returncode == 0 and out.exists():
            print(f'  [PDF] wkhtmltopdf → {out.name}')
            return True
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        print('  [PDF] wkhtmltopdf timed out.')

    # 3. Puppeteer (Node.js)
    puppeteer_js = (
        "const puppeteer = require('puppeteer');\n"
        "(async () => {\n"
        "  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});\n"
        "  const page = await browser.newPage();\n"
        f"  await page.goto('file://{html_path}', {{waitUntil:'networkidle0'}});\n"
        f"  await page.pdf({{path:'{out}',format:'A4',printBackground:true,"
        "margin:{top:'20mm',right:'18mm',bottom:'22mm',left:'18mm'}}});\n"
        "  await browser.close();\n"
        "})();\n"
    )
    tmp_js = html_path.parent / '_wcag_tmp_puppeteer.js'
    try:
        tmp_js.write_text(puppeteer_js, encoding='utf-8')
        r = subprocess.run(['node', str(tmp_js)], capture_output=True, timeout=120)
        if r.returncode == 0 and out.exists():
            print(f'  [PDF] Puppeteer → {out.name}')
            return True
        if r.returncode != 0:
            print(f'  [PDF] Puppeteer error: {r.stderr.decode(errors="replace")[:200]}')
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        print('  [PDF] Puppeteer timed out.')
    finally:
        tmp_js.unlink(missing_ok=True)

    print(
        '  [PDF] No PDF renderer available. Install one to produce PDF output:\n'
        '        pip install weasyprint        (recommended)\n'
        '        brew install wkhtmltopdf       (macOS alternative)\n'
        '        npm install puppeteer          (Node.js alternative)'
    )
    return False


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Generate a WCAG contrast audit report from a saved HTML page.'
    )
    p.add_argument('--html', required=True,
                   help='Path to the locally-saved HTML file to audit')
    p.add_argument('--date', default=None,
                   help='Report date override in YYYY-MM-DD format (defaults to today)')
    p.add_argument('--include-min-css', action='store_true', default=False,
                   help=('Include ALL minified CSS files (*.min.css) in the audit. '
                         'Off by default. Use --include-css to include specific files only.'))
    p.add_argument('--include-css', nargs='+', default=None, metavar='FILENAME',
                   help=('Include specific CSS files by bare filename even if they would '
                         'normally be excluded (e.g. --include-css swiper-bundle.min.css). '
                         'Use after reviewing the Scope & Limitations table in a previous '
                         'report to selectively include only the files you need.'))
    return p.parse_args()


def main():
    args = parse_args()
    html_file = Path(args.html).resolve()
    if not html_file.exists():
        sys.exit(f'ERROR: HTML file not found: {html_file}')

    report_date_iso = args.date or datetime.date.today().isoformat()
    try:
        report_date_fmt = datetime.date.fromisoformat(report_date_iso).strftime('%-d %B %Y')
    except ValueError:
        sys.exit(f'ERROR: Invalid date format: {report_date_iso!r} (expected YYYY-MM-DD)')

    html_dir = html_file.parent
    html_text = html_file.read_text(encoding='utf-8', errors='replace')

    print(f'WCAG-CONTRAST-AUDIT-{SKILL_VERSION}.aiskill | {SKILL_URL}')
    print(f'Input: {html_file.name}')

    site_url = extract_site_url(html_text)
    print(f'Site:  {site_url}')

    include_min = args.include_min_css
    include_css_set: set = set(args.include_css) if args.include_css else set()

    css_files = find_css_files(html_text, html_dir,
                               include_min_css=include_min,
                               include_css=include_css_set)

    # Collect all *.min.css filenames referenced in the HTML for scope disclosure
    all_min_refs = list(dict.fromkeys(
        Path(h).name
        for h in re.findall(r'href=["\']([^"\']+\.min\.css)["\']', html_text, re.I)
    ))

    skipped_names: list = []
    if not include_min:
        # Files that were neither all-included nor explicitly included
        skipped_names = [n for n in all_min_refs if n not in include_css_set]
        if include_css_set:
            explicit_loaded = [n for n in all_min_refs if n in include_css_set]
            if explicit_loaded:
                print(f'Include: {", ".join(explicit_loaded)} (explicitly included via --include-css)')
        if skipped_names:
            print(f'Skip:  {", ".join(skipped_names)} '
                  f'(framework CSS — use --include-css NAME to include individually)')

    css_blocks = []
    css_names = []
    for cf in css_files:
        try:
            css_blocks.append(cf.read_text(encoding='utf-8', errors='replace'))
            css_names.append(cf.name)
        except OSError:
            pass

    # always include inline <style> blocks
    inline_styles = re.findall(r'<style[^>]*>(.*?)</style>', html_text, re.DOTALL | re.I)
    css_blocks.extend(inline_styles)
    if not css_names and inline_styles:
        css_names = ['(inline styles)']
    elif not css_names:
        css_names = ['(none found)']

    # Track which loaded files were explicitly requested (for scope table classification)
    explicit_in_audit: set = {n for n in css_names if n in include_css_set}

    print(f'CSS:   {", ".join(css_names)}')

    pairs = extract_pairs(css_blocks)
    print(f'Pairs: {len(pairs)} extracted')

    results = run_audit(pairs)
    passes = [r for r in results if r['AA_normal'] == 'PASS']
    fails = [r for r in results if r['AA_normal'] == 'FAIL']
    aaa_fails = [r for r in results if r['AAA_normal'] == 'FAIL']
    total = len(results)
    print(f'Audit: {len(passes)} AA pass, {len(fails)} AA fail, {len(aaa_fails)} AAA fail')

    if not _TEMPLATE_PATH.exists():
        sys.exit(f'ERROR: Report template not found: {_TEMPLATE_PATH}')
    template = _TEMPLATE_PATH.read_text(encoding='utf-8')

    exec_sum, exec_detail = build_executive_summary(site_url, total, len(passes), len(fails))
    css_files_label = ', '.join(css_names)

    replacements = {
        '<<<SITE_URL>>>':          _html.escape(site_url),
        '<<<REPORT_DATE>>>':       report_date_fmt,
        '<<<SKILL_VERSION>>>':     SKILL_VERSION,
        '<<<TOTAL_PAIRS>>>':       str(total),
        '<<<PASS_COUNT>>>':        str(len(passes)),
        '<<<FAIL_COUNT>>>':        str(len(fails)),
        '<<<AAA_FAIL_COUNT>>>':    str(len(aaa_fails)),
        '<<<PAIR_COUNT>>>':        str(total),
        '<<<CSS_FILES_AUDITED>>>': _html.escape(css_files_label),
        '<<<SCOPE_FILE_ROWS>>>':   build_scope_rows(css_names, skipped_names,
                                                    explicit_in_audit, site_url),
        '<<<EXECUTIVE_SUMMARY>>>': exec_sum,
        '<<<EXECUTIVE_DETAIL>>>':  exec_detail,
        '<<<RESULTS_TABLE_ROWS>>>': build_table_rows(results),
        '<<<FAIL_INTRO>>>':        build_fail_intro(len(fails)),
        '<<<FAIL_CARDS>>>':        build_fail_cards(fails),
    }

    report_html = template
    for token, value in replacements.items():
        report_html = report_html.replace(token, value)

    safe_domain = re.sub(r'[^\w\-.]', '-', site_url).strip('-')
    out_stem = f'WCAG-Contrast-Audit-Report-{safe_domain}-{report_date_iso}'
    html_out = html_dir / f'{out_stem}.html'
    html_out.write_text(report_html, encoding='utf-8')
    print(f'HTML:  {html_out}')

    convert_to_pdf(html_out)
    print('Done.')


if __name__ == '__main__':
    main()
