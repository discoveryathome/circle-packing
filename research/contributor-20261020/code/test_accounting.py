import unittest
from fractions import Fraction as F
from check_accounting import check_trial
class Accounting(unittest.TestCase):
    def setup_values(self):
        c={'n':500,'denominator':'1000000000000000','radius_numerator':'20000000001000'}
        r={'n':500,'radius':'0.020000000001','base_radius':'0.02','above_start_gate':False,'meaningful':False}
        return r,c,F('0.02')
    def test_tiny_exact_gain_is_a_tie(self):
        r,c,s=self.setup_values();self.assertGreater(check_trial(r,c,s,s),s)
    def test_reject_false_tiny_improvement(self):
        r,c,s=self.setup_values();r['meaningful']=True
        with self.assertRaises(ValueError):check_trial(r,c,s,s)
    def test_reject_invented_radius(self):
        r,c,s=self.setup_values();r['radius']='0.020001'
        with self.assertRaises(ValueError):check_trial(r,c,s,s)
    def test_reject_changed_baseline(self):
        r,c,s=self.setup_values();r['base_radius']='0.019'
        with self.assertRaises(ValueError):check_trial(r,c,s,s)
    def test_reject_wrong_count(self):
        r,c,s=self.setup_values();r['n']=501
        with self.assertRaises(ValueError):check_trial(r,c,s,s)
if __name__=='__main__':unittest.main()
