"""Session-designed moves plus differentiable overlap repair; heuristic only.

Penalty relaxation is a standard packing technique (Lai et al., 2023).
This implementation and its move mixture are experimental, not a new algorithm claim.
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree, Voronoi, QhullError
from optimizer import score, from_certificate, neighboring

def energy_gradient(flat, target):
    p=flat.reshape(-1,2); n=len(p)
    pairs=cKDTree(p).query_pairs(target,output_type='ndarray')
    if len(pairs)==0:return 0.0,np.zeros_like(flat)
    a,b=pairs.T; delta=p[a]-p[b]; dist=np.maximum(np.linalg.norm(delta,axis=1),1e-15)
    overlap=1-dist/target
    forces=(-2*overlap/(target*dist))[:,None]*delta
    grad=np.column_stack([np.bincount(a,weights=forces[:,k],minlength=n)-np.bincount(b,weights=forces[:,k],minlength=n) for k in range(2)])
    return float(overlap@overlap),grad.ravel()

class BudgetStop(Exception): pass

def elastic(p, best_distance, seconds, rng):
    start=time.monotonic(); last=p.ravel().copy(); calls=0; iterations=0
    target=best_distance*(1+float(rng.choice([1e-6,1e-5,1e-4])))
    def fun(x):
        nonlocal calls
        calls+=1
        return energy_gradient(x,target)
    def callback(x):
        nonlocal last,iterations
        last=x.copy();iterations+=1
        if time.monotonic()-start>=seconds:raise BudgetStop
    stopped=False
    try:
        result=minimize(fun,last,method='L-BFGS-B',jac=True,bounds=[(0,1)]*len(last),callback=callback,
                        options={'maxiter':1000,'maxcor':12,'ftol':1e-16,'gtol':1e-10,'maxls':30})
        last=result.x;status=str(result.message)
    except BudgetStop:
        stopped=True;status='wall budget'
    return last.reshape(-1,2),{'seconds':time.monotonic()-start,'iterations':iterations,'function_calls':calls,'target':target,'energy':energy_gradient(last,target)[0],'status':status,'budget_stop':stopped}

def propose(best,current,rng,attempt):
    if attempt==0:return best.copy(),'polish'
    mode=['micro','patch','shear','vacancy','neighbor-remove','neighbor-insert'][(attempt-1)%6]
    p=best.copy() if attempt%3 else current.copy();n=len(p);d=score(best)
    if mode=='micro':
        p+=rng.normal(0,float(rng.choice([.0002,.001,.004]))*d,p.shape)
    elif mode=='patch':
        pairs=cKDTree(p).query_pairs(d*1.001,output_type='ndarray')
        degrees=np.bincount(pairs.ravel(),minlength=n)
        wall=((p<d*.001)|(p>1-d*.001)).sum(axis=1);degrees+=wall
        candidates=np.flatnonzero((degrees>=2)&(degrees<=4))
        k=int(rng.choice(candidates)) if len(candidates) else int(rng.integers(n))
        ids=cKDTree(p).query(p[k],k=min(12,n))[1]
        p[ids]+=rng.normal(0,.02*d,(len(ids),2))
    elif mode=='shear':
        axis=int(rng.integers(2));center=float(rng.random());width=float(rng.uniform(2,5))*d
        weight=np.maximum(0,1-np.abs(p[:,axis]-center)/width)
        p[:,1-axis]+=weight*float(rng.choice([-1,1]))*.03*d
    elif mode=='vacancy':
        pairs=cKDTree(p).query_pairs(d*1.01,output_type='ndarray');degrees=np.bincount(pairs.ravel(),minlength=n)
        k=int(rng.choice(np.flatnonzero(degrees>=np.median(degrees))))
        keep=np.delete(p,k,axis=0)
        samples=rng.random((2048,2))
        try:
            vertices=Voronoi(keep).vertices
            vertices=vertices[np.all((vertices>=0)&(vertices<=1),axis=1)]
            samples=np.vstack([samples,vertices])
        except QhullError:pass
        # Exclude the removed circle's old pocket to force a real relocation.
        samples=samples[np.linalg.norm(samples-p[k],axis=1)>.5*d]
        clearance=cKDTree(keep).query(samples)[0]
        p[k]=samples[int(np.argmax(clearance))]
    else:
        source_n=n+(1 if mode=='neighbor-remove' else -1)
        path=Path(__file__).resolve().parents[3]/'certificates'/'baseline'/f'n{source_n}.json'
        p=neighboring(from_certificate(json.loads(path.read_text())),n,rng)
    return np.clip(p,0,1),mode
