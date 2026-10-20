import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from optimizer import relax,score,neighboring,perturb,to_unit_circles
from certify import make_certificate
from verify import verify

class SolverTests(unittest.TestCase):
    def test_recover_four_corners(self):
        p=np.array([[.03,.04],[.03,.95],[.95,.04],[.97,.97]])
        q,stats=relax(p,max_steps=15,seconds=10)
        self.assertGreater(score(q),.999999)
        c=make_certificate(to_unit_circles(q),{})
        self.assertTrue(verify(c,4)['valid'])
    def test_neighbor_counts_and_seed(self):
        p=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
        for n in [3,5]:
            q=neighboring(p,n,np.random.default_rng(123))
            self.assertEqual(q.shape,(n,2));self.assertGreater(score(q),0)
        for mode in ['local','contact','basin']:
            a=perturb(p,np.random.default_rng(1),mode)
            b=perturb(p,np.random.default_rng(1),mode)
            np.testing.assert_array_equal(a,b)
            self.assertFalse(np.array_equal(a,p))
if __name__=='__main__':unittest.main()
