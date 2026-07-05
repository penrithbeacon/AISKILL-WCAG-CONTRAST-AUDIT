#!/usr/bin/env python3
"""
Unit tests for wcag_contrast.py

Tests cover:
1. hex_to_rgb   — 6-digit and 3-digit shorthand
2. linearise    — below and above 0.04045 threshold
3. relative_luminance — black (#000000) and white (#ffffff)
4. contrast_ratio     — black on white (21:1), identical colours (1:1)
5. wcag_level         — AA pass at 4.5:1, AAA fail below 7:1
6. The canonical emerald on dark background pair from this site
"""

import sys, os, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from wcag_contrast import hex_to_rgb, linearise, relative_luminance, contrast_ratio, wcag_level


class TestHexToRgb(unittest.TestCase):
    def test_six_digit(self):
        self.assertEqual(hex_to_rgb('#ffffff'), (255, 255, 255))
        self.assertEqual(hex_to_rgb('#000000'), (0, 0, 0))
        self.assertEqual(hex_to_rgb('#10b981'), (16, 185, 129))

    def test_three_digit(self):
        self.assertEqual(hex_to_rgb('#fff'), (255, 255, 255))
        self.assertEqual(hex_to_rgb('#000'), (0, 0, 0))

    def test_no_hash(self):
        self.assertEqual(hex_to_rgb('e2e8f0'), (226, 232, 240))


class TestLinearise(unittest.TestCase):
    def test_zero(self):
        self.assertAlmostEqual(linearise(0), 0.0)

    def test_full(self):
        self.assertAlmostEqual(linearise(255), 1.0, places=5)

    def test_mid(self):
        v = linearise(128)
        self.assertGreater(v, 0)
        self.assertLess(v, 1)


class TestRelativeLuminance(unittest.TestCase):
    def test_white(self):
        self.assertAlmostEqual(relative_luminance('#ffffff'), 1.0, places=5)

    def test_black(self):
        self.assertAlmostEqual(relative_luminance('#000000'), 0.0, places=5)

    def test_midrange(self):
        lum = relative_luminance('#808080')
        self.assertGreater(lum, 0.0)
        self.assertLess(lum, 1.0)


class TestContrastRatio(unittest.TestCase):
    def test_black_on_white(self):
        self.assertAlmostEqual(contrast_ratio('#000000', '#ffffff'), 21.0, places=1)

    def test_white_on_black(self):
        self.assertAlmostEqual(contrast_ratio('#ffffff', '#000000'), 21.0, places=1)

    def test_identical(self):
        self.assertAlmostEqual(contrast_ratio('#10b981', '#10b981'), 1.0, places=5)


class TestWcagLevel(unittest.TestCase):
    def test_aa_pass(self):
        level = wcag_level(4.5)
        self.assertTrue(level['AA_normal'])
        self.assertTrue(level['AA_large'])

    def test_aaa_fail_below_seven(self):
        level = wcag_level(5.0)
        self.assertTrue(level['AA_normal'])
        self.assertFalse(level['AAA_normal'])

    def test_all_fail(self):
        level = wcag_level(2.9)
        self.assertFalse(level['AA_normal'])
        self.assertFalse(level['AA_large'])
        self.assertFalse(level['AAA_normal'])
        self.assertFalse(level['AAA_large'])


class TestCanonicalPair(unittest.TestCase):
    """Emerald #10b981 on dark bg #0f1117 — the site's primary accent."""
    def test_emerald_on_dark(self):
        ratio = contrast_ratio('#10b981', '#0f1117')
        self.assertGreater(ratio, 4.5)
        self.assertTrue(wcag_level(ratio)['AA_normal'])


if __name__ == '__main__':
    unittest.main()
