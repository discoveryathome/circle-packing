"""Witnesses for single faults in the exact verifier that tests/test_verifier.py does not catch.

Expected outcomes come from the certificate contract in METHODS.md and the input limits in
src/verify.py's code, not from running verify(). research/verifier-mutation-20261025/
check_witnesses.py re-derives every one with a separate Fraction oracle (its input limits are
copied from verify.py) and recomputes the report minima.
"""
import copy
from fractions import Fraction
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from verify import verify


def cert(q, r, centers):
    return {'schema': 'equal-circle-square/v1', 'n': len(centers), 'denominator': str(q),
            'radius_numerator': str(r), 'centers': [[str(x), str(y)] for x, y in centers]}


def replaced(base, path, value):
    c = copy.deepcopy(base)
    target = c
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return c


def without(base, key):
    return {k: v for k, v in base.items() if k != key}


GRID = cert(4, 1, [(1, 1), (1, 3), (3, 1), (3, 3)])    # four tangent circles, radius 1/4
HALF = cert(2, 1, [(1, 1)])                             # one circle, radius 1/2
BIG = 10**199                                           # 200 decimal characters

# group -> [(label, certificate, expected_n, accepted)]
WITNESSES = {
    # Radius 1/4 on denominator 4: a centre coordinate is admissible exactly when it is 1, 2 or 3.
    'walls': [
        ('tangent to left and bottom', cert(4, 1, [(1, 1)]), None, True),
        ('tangent to right and top', cert(4, 1, [(3, 3)]), None, True),
        ('crosses left wall by one unit', cert(4, 1, [(0, 2)]), None, False),
        ('crosses bottom wall by one unit', cert(4, 1, [(2, 0)]), None, False),
        ('crosses right wall by one unit', cert(4, 1, [(4, 2)]), None, False),
        ('crosses top wall by one unit', cert(4, 1, [(2, 4)]), None, False),
        ('radius 1/2 fills the square', HALF, None, True),
    ],
    # Pairs in both orders, including a later circle left of or below the earlier one, so that
    # coordinate differences are negative.
    'pairs': [
        ('tangent, later circle to the left', cert(4, 1, [(3, 1), (1, 1)]), None, True),
        ('tangent, later circle below', cert(4, 1, [(1, 3), (1, 1)]), None, True),
        ('horizontal overlap', cert(8, 2, [(2, 2), (5, 2)]), None, False),
        ('horizontal overlap, later circle to the left', cert(8, 2, [(5, 2), (2, 2)]), None, False),
        ('diagonal overlap', cert(8, 2, [(2, 2), (4, 5)]), None, False),
        ('diagonal clearance', cert(8, 2, [(2, 2), (5, 5)]), None, True),
    ],
    # Integers are canonical ASCII decimal strings of at most 200 characters. Python's int()
    # accepts every rejected spelling below, so only the string check stands between them and
    # the geometry.
    'integers': [
        ('plus sign', replaced(GRID, ['denominator'], '+4'), None, False),
        ('leading zero', replaced(GRID, ['denominator'], '04'), None, False),
        ('trailing space', replaced(GRID, ['denominator'], '4 '), None, False),
        ('trailing newline', replaced(GRID, ['radius_numerator'], '1\n'), None, False),
        ('leading space in a coordinate', replaced(GRID, ['centers', 0, 0], ' 1'), None, False),
        ('ARABIC-INDIC DIGIT FOUR', replaced(GRID, ['denominator'], '٤'), None, False),
        ('200-character integers', cert(2*BIG, BIG, [(BIG, BIG)]), None, True),
        ('201-character integers', cert(20*BIG, 10*BIG, [(10*BIG, 10*BIG)]), None, False),
    ],
    'instance': [
        ('other schema', replaced(GRID, ['schema'], 'equal-circle-square/v2'), None, False),
        ('missing schema', without(GRID, 'schema'), None, False),
        ('count as JSON float', replaced(GRID, ['n'], 4.0), None, False),
        ('count as JSON true', replaced(HALF, ['n'], True), 1, False),
        ('zero circles', cert(2, 1, []), None, False),
        ('10001 tangent circles', cert(202, 1, [(1+2*(k % 101), 1+2*(k//101)) for k in range(10001)]), None, False),
    ],
    'shape': [
        ('centre as a two-character string', replaced(HALF, ['centers', 0], '11'), None, False),
        ('centre as an object with two keys', replaced(GRID, ['centers', 1], {'1': 0, '3': 0}), None, False),
    ],
}

# Report fields, not an acceptance decision. Radius 2/20. The unique closest pair is (1, 2),
# with squared clearance 5^2 - 4^2 = 9 over 20^2. Circle 1 is the unique closest to a wall,
# one unit from the right side. Neither minimum comes first or last in loop order.
REPORT_CASE = cert(20, 2, [(4, 4), (17, 10), (12, 10), (5, 16)])
REPORT_EXPECTED = {'wall_slack': Fraction(1, 20), 'pair_squared_slack': Fraction(9, 400),
                   'tightest_pair': [1, 2]}


class VerifierFaultWitnesses(unittest.TestCase):
    def check(self, group):
        for label, c, n, accepted in WITNESSES[group]:
            with self.subTest(label):
                if accepted:
                    self.assertIs(verify(copy.deepcopy(c), n)['valid'], True)
                else:
                    with self.assertRaises(ValueError):
                        verify(copy.deepcopy(c), n)

    def test_each_wall(self):
        self.check('walls')

    def test_pair_orientation(self):
        self.check('pairs')

    def test_canonical_integers(self):
        self.check('integers')

    def test_instance_binding(self):
        self.check('instance')

    def test_center_shape(self):
        self.check('shape')

    def test_report_minima(self):
        r = verify(copy.deepcopy(REPORT_CASE), 4)
        got = {'wall_slack': Fraction(int(r['wall_slack_numerator']), int(r['wall_slack_denominator'])),
               'pair_squared_slack': Fraction(int(r['pair_squared_slack_numerator']),
                                              int(r['pair_squared_slack_denominator'])),
               'tightest_pair': r['tightest_pair']}
        self.assertEqual(got, REPORT_EXPECTED)


if __name__ == '__main__':
    unittest.main()
