"""Independent exact accounting of logged improvements; standard library only."""
from fractions import Fraction as F

def gate(r):return max(F(1,10**10),r/F(10**8))
def check_trial(row,certificate,start,incumbent):
    r=F(certificate['radius_numerator'])/int(certificate['denominator'])
    if certificate['n']!=row['n']:raise ValueError('trial count mismatch')
    if r!=F(row['radius']):raise ValueError('logged radius differs from witness')
    if start!=F(row['base_radius']):raise ValueError('logged input radius differs from frozen input')
    if bool(row['above_start_gate'])!=(r-start>gate(start)):raise ValueError('false above-input classification')
    if bool(row['meaningful'])!=(r-incumbent>gate(start)):raise ValueError('false new-incumbent classification')
    return max(r,incumbent)
