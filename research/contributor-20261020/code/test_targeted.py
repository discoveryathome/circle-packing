"""Numerical sanity checks for the new method, separate from exact acceptance."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'frozen'))
import numpy as np
from scipy.optimize import check_grad
from targeted import energy_gradient, elastic, propose

class TestRepair(unittest.TestCase):
    def test_gradient(self):
        x=np.array([[.1,.1],[.18,.12],[.45,.5],[.5,.55]]).ravel()
        error=check_grad(lambda z:energy_gradient(z,.12)[0],lambda z:energy_gradient(z,.12)[1],x)
        self.assertLess(error,1e-4)
    def test_zero_for_no_overlap(self):
        e,g=energy_gradient(np.array([.1,.1,.9,.9]),.1)
        self.assertEqual(e,0);self.assertTrue(np.all(g==0))
    def test_repair_lowers_energy(self):
        p=np.array([[.1,.1],[.15,.1],[.5,.5],[.55,.5]])
        q,stats=elastic(p,.1,1,np.random.default_rng(2))
        self.assertLess(energy_gradient(q.ravel(),stats['target'])[0],energy_gradient(p.ravel(),stats['target'])[0])
        self.assertTrue(np.all((q>=0)&(q<=1)))
    def test_all_moves_valid_and_deterministic(self):
        import json
        from optimizer import from_certificate
        p=from_certificate(json.loads((Path(__file__).resolve().parents[1]/'inputs/n400.json').read_text()))
        for attempt in range(7):
            a,mode=propose(p,p,np.random.default_rng(42),attempt)
            b,_=propose(p,p,np.random.default_rng(42),attempt)
            self.assertEqual(a.shape,p.shape);self.assertTrue(np.all(np.isfinite(a)))
            self.assertTrue(np.all((a>=0)&(a<=1)));self.assertTrue(np.array_equal(a,b),mode)
if __name__=='__main__':unittest.main()
