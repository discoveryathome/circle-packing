import sys
import unittest
from decimal import localcontext
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from certify import make_certificate
from verify import verify


class CertifierRoundingTests(unittest.TestCase):
    def test_decimal_just_above_half_grid(self):
        x = '0.2500000000000005'+'0'*84+'1'
        c = make_certificate([[x, '0.5']], {})
        self.assertEqual(c['centers'][0][0], '250000000000001')
        self.assertEqual(c['radius_numerator'], '250000000000001')
        self.assertTrue(verify(c, 1)['valid'])

    def test_decimal_just_below_odd_half_grid(self):
        x = '0.2500000000000014'+'9'*85
        c = make_certificate([[x, '0.5']], {})
        self.assertEqual(c['centers'][0][0], '250000000000001')

    def test_half_even_ties(self):
        for x, expected in [('0.2500000000000005', '250000000000000'),
                            ('0.2500000000000015', '250000000000002')]:
            with self.subTest(x=x):
                self.assertEqual(make_certificate([[x, '0.5']], {})['centers'][0][0], expected)

    def test_valid_coarse_grid_just_above_half(self):
        x = '0.25'+'0'*80+'1'
        c = make_certificate([[x, '0.5']], {}, scale=2)
        self.assertEqual(c['centers'], [['1', '1']])
        self.assertEqual(c['radius_numerator'], '1')

    def test_rounding_ignores_decimal_exponent_context(self):
        with localcontext() as ctx:
            ctx.Emax = 9
            c = make_certificate([['0.5', '0.5']], {})
        self.assertEqual(c['radius_numerator'], '500000000000000')


if __name__ == '__main__':
    unittest.main()
