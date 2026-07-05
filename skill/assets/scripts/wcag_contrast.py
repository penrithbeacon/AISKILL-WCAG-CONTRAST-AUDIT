#!/usr/bin/env python3
"""
WCAG 2.1/2.2 Contrast Ratio Calculator

Computes contrast ratios between foreground/background colour pairs.
Supports hex colour notation (#rrggbb or #rgb).

Usage:
    python3 wcag_contrast.py --pairs "#0f1117,#e2e8f0" "#10b981,#0f1117"
    python3 wcag_contrast.py --csv pairs.csv
    python3 wcag_contrast.py --fg "#0f1117" --bg "#e2e8f0"

WCAG thresholds:
    AA  normal text: 4.5:1
    AA  large text:  3.0:1
    AAA normal text: 7.0:1
    AAA large text:  4.5:1
"""

import argparse, csv, json, sys


def hex_to_rgb(hex_color: str) -> tuple:
    """Parse #rrggbb or #rgb hex colour to (r, g, b) in [0, 255]."""
    h = hex_color.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex colour: {hex_color!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def linearise(channel: float) -> float:
    """Convert 8-bit sRGB channel [0,255] to linear light."""
    c = channel / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Compute WCAG relative luminance for a hex colour."""
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * linearise(r) + 0.7152 * linearise(g) + 0.0722 * linearise(b)


def contrast_ratio(fg: str, bg: str) -> float:
    """Compute WCAG contrast ratio between two hex colours."""
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_level(ratio: float) -> dict:
    """Return AA and AAA pass/fail for normal and large text."""
    return {
        'AA_normal':  ratio >= 4.5,
        'AA_large':   ratio >= 3.0,
        'AAA_normal': ratio >= 7.0,
        'AAA_large':  ratio >= 4.5,
    }


def format_row(fg: str, bg: str, label: str = '') -> dict:
    """Return a result dict for a colour pair."""
    ratio = contrast_ratio(fg, bg)
    level = wcag_level(ratio)
    return {
        'label':      label,
        'foreground': fg,
        'background': bg,
        'ratio':      round(ratio, 2),
        'AA_normal':  'PASS' if level['AA_normal']  else 'FAIL',
        'AA_large':   'PASS' if level['AA_large']   else 'FAIL',
        'AAA_normal': 'PASS' if level['AAA_normal'] else 'FAIL',
        'AAA_large':  'PASS' if level['AAA_large']  else 'FAIL',
    }


def print_table(rows: list) -> None:
    """Print results as an ASCII table."""
    headers = ['Foreground', 'Background', 'Ratio', 'AA Normal', 'AA Large', 'AAA Normal', 'AAA Large']
    col_keys = ['foreground', 'background', 'ratio', 'AA_normal', 'AA_large', 'AAA_normal', 'AAA_large']
    widths = [max(len(str(r[k])) for r in rows + [dict(zip(col_keys, headers))]) for k in col_keys]
    sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    def row_str(values):
        return '|' + '|'.join(f' {str(v):<{w}} ' for v, w in zip(values, widths)) + '|'
    print(sep)
    print(row_str(headers))
    print(sep)
    for r in rows:
        print(row_str([r[k] for k in col_keys]))
    print(sep)


def main() -> int:
    parser = argparse.ArgumentParser(description='WCAG contrast ratio auditor')
    parser.add_argument('--fg',    help='Foreground colour (hex)')
    parser.add_argument('--bg',    help='Background colour (hex)')
    parser.add_argument('--pairs', nargs='+', help='Colour pairs as "fg,bg" strings')
    parser.add_argument('--csv',   help='CSV file with fg,bg columns')
    parser.add_argument('--json',  action='store_true', help='Output as JSON')
    args = parser.parse_args()

    pairs = []
    if args.fg and args.bg:
        pairs.append((args.fg, args.bg, ''))
    if args.pairs:
        for p in args.pairs:
            parts = p.split(',')
            if len(parts) >= 2:
                pairs.append((parts[0].strip(), parts[1].strip(), parts[2].strip() if len(parts) > 2 else ''))
    if args.csv:
        with open(args.csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pairs.append((row['fg'].strip(), row['bg'].strip(), row.get('label', '').strip()))

    if not pairs:
        parser.print_help()
        return 1

    rows = [format_row(fg, bg, label) for fg, bg, label in pairs]

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print_table(rows)

    fails = [r for r in rows if r['AA_normal'] == 'FAIL']
    if fails:
        print(f"\n{len(fails)} pair(s) fail WCAG AA (normal text). Review required.")
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
