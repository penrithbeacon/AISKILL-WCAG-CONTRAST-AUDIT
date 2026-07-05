# AISKILL-WCAG-CONTRAST-AUDIT

**WCAG Contrast Audit** — Audits foreground/background colour pairs against WCAG 2.1/2.2 AA and AAA contrast ratios and generates a professional PDF report from a saved HTML page in one command.

| | |
|---|---|
| Version | `1.0.0` |
| License | `MIT` |
| Author | Anthony Harrison |
| Homepage | https://openaiskillpackage.com/ |
| Spec | [Open AI Skill Package Specification](https://openaiskillpackage.com/) |

---

## What This Skill Does

[Replace this section with a detailed description of what the skill does, when to use it,
and what problem it solves. Be specific — someone reading this README should understand
whether this skill is what they need without having to open the .aiskill file.]

---

## Prerequisites

Before using this skill, ensure the following are available in the AI agent's environment:

- Python 3.8 or later
- [Add any pip packages, e.g. `pip install pyyaml weasyprint`]
- [Add any system tools, e.g. `git`, `gh` CLI]

---

## Quick Start

1. Download `WCAG-CONTRAST-AUDIT-1.0.0.aiskill` from the [Releases](https://github.com/PenrithBeacon/AISKILL-WCAG-CONTRAST-AUDIT/releases) page
2. Give your AI agent the following prompt:

```
Using the Skill Package at /path/to/WCAG-CONTRAST-AUDIT-1.0.0.aiskill,
[describe what you want the skill to do, e.g. 'audit the contrast of /path/to/saved-page.html']
```

---

## Skill Archive Contents

```
WCAG-CONTRAST-AUDIT-1.0.0.aiskill  (ZIP archive)
├── manifest.yaml          # identity & metadata
├── SKILL.md               # AI entry point — execution instructions
├── README.md              # this file (skill-level)
├── CHANGELOG.md           # version history
├── checksums.yaml         # SHA-256 integrity hashes
├── assets/
│   ├── scripts/           # execution scripts
│   │   └── [script].py
│   ├── templates/         # content templates (if any)
│   └── tests/             # unit tests
│       └── test_[script].py
└── inputs/
    └── schema.json        # input schema
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
