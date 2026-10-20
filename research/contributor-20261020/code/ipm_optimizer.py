"""Diagnostic variant: explicitly select HiGHS interior-point LP method."""
"""Heuristic search only. Exact acceptance lives in verify.py, not here."""
import hashlib, json, math, time, warnings
import numpy as np
from scipy.optimize import linprog, OptimizeWarning
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import coo_matrix


def score(p):
    return float(np.min(pdist(p))) if len(p)>1 else math.inf


def to_unit_circles(p):
    d=score(p); r=d/(2*(1+d))
    return r+(1-2*r)*np.clip(p,0,1)


def from_certificate(c):
    q=int(c['denominator']); r=int(c['radius_numerator'])/q
    return np.clip((np.array(c['centers'],dtype=float)/q-r)/(1-2*r),0,1)


def graph(p, tolerance=2e-5):
    n=len(p);d=score(p)
    i,j=np.triu_indices(n,1)
    mask=np.linalg.norm(p[i]-p[j],axis=1)<d*(1+tolerance)
    edges={(int(a),int(b)) for a,b in zip(i[mask],j[mask])}
    walls={(int(k),2*n+axis*2+side) for k in range(n) for axis in range(2)
           for side in range(2) if abs(p[k,axis]-side)<d*tolerance}
    return edges|walls


def relax(p, max_steps=35, seconds=5.0):
    """Sequential supporting-plane LPs. Rebuild pairs every iteration.

    With coordinate displacement <= trust, pair distance can fall by <=2sqrt(2)trust.
    Therefore omit only pairs initially farther than d_upper+2sqrt(2)trust.
    Full floating-point distances rank all LP outputs. Certification is independent.
    """
    p=np.clip(np.array(p,dtype=float),0,1); n=len(p)
    best=p.copy(); best_d=score(best)
    i,j=np.triu_indices(n,1)
    reference=1/math.sqrt(n); trust=.18*reference
    started=time.monotonic(); failures=0; steps=0; stationary=0
    for k in range(max_steps):
        remaining=seconds-(time.monotonic()-started)
        if remaining<=0: break
        diff=p[i]-p[j]; distances=np.linalg.norm(diff,axis=1)
        d=float(distances.min()); upper=d+.3*reference
        mask=distances <= upper+2*math.sqrt(2)*trust+1e-12
        a,b=i[mask],j[mask]; norms=distances[mask]
        if np.any(norms<1e-14):
            failures+=1;break
        u=diff[mask]/norms[:,None]; m=len(a); rr=np.arange(m)
        mat=coo_matrix((np.concatenate([-u[:,0],-u[:,1],u[:,0],u[:,1],np.ones(m)]),
                       (np.tile(rr,5),np.concatenate([2*a,2*a+1,2*b,2*b+1,np.full(m,2*n)]))),
                      shape=(m,2*n+1)).tocsr()
        bounds=list(zip(np.maximum(-trust,-p.ravel()),np.minimum(trust,1-p.ravel())))+[(0,upper)]
        obj=np.zeros(2*n+1);obj[-1]=-1
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',OptimizeWarning)
            result=linprog(obj,A_ub=mat,b_ub=norms,bounds=bounds,method='highs-ipm',
                           options={'primal_feasibility_tolerance':1e-10,
                                    'dual_feasibility_tolerance':1e-10,
                                    'time_limit':max(.01,remaining),'threads':1})
        steps+=1
        if not result.success:
            failures+=1;break
        new=np.clip(p+result.x[:-1].reshape(n,2),0,1); new_d=score(new)
        if new_d>best_d: best,best_d=new.copy(),new_d
        stationary=stationary+1 if abs(new_d-d)<2e-11 else 0
        p=new
        if stationary>=3: break
    return best,{'lp_steps':steps,'lp_failures':failures,'seconds':time.monotonic()-started}


def perturb(p,rng,mode):
    p=p.copy();n=len(p);d=score(p)
    if mode=='local':
        p+=rng.normal(0,.035*d,p.shape)
    elif mode=='contact':
        # Break several contacts through a cluster rotation and a vacancy relocation.
        k=int(rng.integers(n));distance=np.linalg.norm(p-p[k],axis=1)
        ids=np.argsort(distance)[:min(7,n)]
        angle=float(rng.choice([-1,1]))*.35
        rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
        p[ids]=(p[ids]-p[k])@rot+p[k]
        if rng.random()<.5:
            keep=np.delete(p,k,axis=0); samples=rng.random((1024,2))
            clearance=np.linalg.norm(samples[:,None,:]-keep[None,:,:],axis=2).min(axis=1)
            p[k]=samples[int(np.argmax(clearance))]
    elif mode=='basin':
        ids=rng.choice(n,max(2,n//8),replace=False)
        p[ids]+=rng.normal(0,.35*d,(len(ids),2))
    else: raise ValueError(mode)
    return np.clip(p,0,1)


def neighboring(p,n,rng):
    p=p.copy()
    if len(p)==n+1:
        # Random deletion biases toward dense core to unlock a vacancy.
        dist=squareform(pdist(p)); degree=(dist<score(p)*1.05).sum(axis=1)
        candidates=np.flatnonzero(degree>=np.median(degree))
        return np.delete(p,int(rng.choice(candidates)),axis=0)
    if len(p)==n-1:
        samples=np.vstack([rng.random((2048,2)),[[0,0],[0,1],[1,0],[1,1]]])
        clearance=np.linalg.norm(samples[:,None,:]-p[None,:,:],axis=2).min(axis=1)
        return np.vstack([p,samples[int(np.argmax(clearance))]])
    raise ValueError('neighbor must differ by one circle')


def lattice(n,rng):
    candidates=[]
    for cols in range(max(2,int(math.sqrt(n))-2),int(math.sqrt(n))+4):
        rows=math.ceil(n/cols)
        p=np.array([(x+.5*(y%2),y*math.sqrt(3)/2) for y in range(rows) for x in range(cols)],float)
        p=p[rng.permutation(len(p))[:n]]
        p-=p.min(axis=0);p/=p.max()
        candidates.append(p)
    return max(candidates,key=score)
