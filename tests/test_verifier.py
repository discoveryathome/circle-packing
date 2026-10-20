import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from verify import verify
from certify import make_certificate

class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.c={'schema':'equal-circle-square/v1','n':4,'denominator':'4',
                'radius_numerator':'1','centers':[['1','1'],['1','3'],['3','1'],['3','3']]}
    def test_tangent_grid(self):
        self.assertEqual(verify(self.c,4)['pairs_checked'],6)
    def test_wall(self):
        self.c['centers'][0][0]='0'
        with self.assertRaises(ValueError): verify(self.c)
    def test_overlap_one_integer_unit(self):
        self.c['denominator']='4000000000000000'
        self.c['radius_numerator']='1000000000000000'
        self.c['centers']=[[str(int(v)*10**15) for v in p] for p in self.c['centers']]
        self.c['centers'][1][1]='2999999999999999'
        with self.assertRaises(ValueError): verify(self.c)
    def test_duplicates(self):
        self.c['centers'][1]=self.c['centers'][0]
        with self.assertRaises(ValueError): verify(self.c)
    def test_wrong_count(self):
        with self.assertRaises(ValueError): verify(self.c,5)
        self.c['n']=3
        with self.assertRaises(ValueError): verify(self.c)
    def test_malformed(self):
        for field,value in [('radius_numerator','0'),('denominator','0'),('denominator','-4'),
                            ('radius_numerator','NaN'),('radius_numerator',1),('n',True)]:
            c=copy.deepcopy(self.c); c[field]=value
            with self.assertRaises(ValueError): verify(c)
    def test_single(self):
        c=make_certificate([['0.5','0.5']],{})
        self.assertTrue(verify(c)['valid'])
    def test_certifier_irrational_distance(self):
        c=make_certificate([['0.2','0.2'],['0.5','0.5']],{})
        self.assertTrue(verify(c)['valid'])
        c['radius_numerator']=str(int(c['radius_numerator'])+1)
        with self.assertRaises(ValueError): verify(c)

if __name__=='__main__': unittest.main()
