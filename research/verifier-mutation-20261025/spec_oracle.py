"""Accept/reject oracle for equal-circle-square/v1 certificates, written from the contract.

Geometry follows METHODS.md, "Rigorous feasible-coordinate certificate": coordinates X/Q,
radius R/Q, R <= X,Y <= Q-R, and (Xi-Xj)^2+(Yi-Yj)^2 >= 4R^2, tangency allowed, with
exact Fractions. The input limits (N in 1..10000, canonical decimal strings of at most 200
characters) are not in METHODS.md; they are copied from the code of src/verify.py and are
labelled as such, so agreement on them is not independent. This module does not import
src/verify.py.
"""
from fractions import Fraction

SCHEMA = 'equal-circle-square/v1'
MAX_N = 10000            # from src/verify.py, not METHODS.md
MAX_DIGITS = 200         # from src/verify.py, not METHODS.md
DIGITS = '0123456789'


def canonical_integer(value):
    """Return the int for a canonical ASCII decimal string, else None."""
    if not isinstance(value, str) or not value or len(value) > MAX_DIGITS:
        return None
    body = value[1:] if value[0] == '-' else value
    if not body or any(ch not in DIGITS for ch in body):
        return None
    if len(body) > 1 and body[0] == '0':
        return None
    return int(body) * (-1 if value[0] == '-' else 1)


def accepts(c, expected_n=None):
    """True if the contract accepts certificate c for the requested count."""
    if not isinstance(c, dict) or c.get('schema') != SCHEMA:
        return False
    n = c.get('n')
    if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n > MAX_N:
        return False
    if expected_n is not None and n != expected_n:
        return False
    q = canonical_integer(c.get('denominator'))
    big_r = canonical_integer(c.get('radius_numerator'))
    if q is None or big_r is None or q <= 0 or big_r <= 0:
        return False
    centers = c.get('centers')
    if not isinstance(centers, list) or len(centers) != n:
        return False
    radius = Fraction(big_r, q)
    points = []
    for p in centers:
        if not isinstance(p, list) or len(p) != 2:
            return False
        xy = [canonical_integer(v) for v in p]
        if None in xy:
            return False
        x, y = (Fraction(v, q) for v in xy)
        if not (radius <= x <= 1 - radius and radius <= y <= 1 - radius):
            return False
        points.append((x, y))
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            if dx * dx + dy * dy < (2 * radius) ** 2:
                return False
    return True
