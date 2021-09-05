import numpy as np
import scipy
import scipy.stats
def topK(k,pred,ground_truth):
    assert k <= len(ground_truth) and k <= len(pred)
    cand_list = ground_truth[:k]
    res = 0 
    for i in range(k):
        if pred[i] in cand_list:
            res += 1
    return res/k

def JSDist(p,q):
    p = np.asfarray(p)
    q = np.asfarray(q)
    M=(p+q)/2
    return 0.5*scipy.stats.entropy(p, M)+0.5*scipy.stats.entropy(q, M)

def KLDist(p,q):
    p = np.asfarray(p)
    q = np.asfarray(q)
    return scipy.stats.entropy(p, q)

def precision():
    raise NotImplementedError

def dcg_at_k( r, k, method = 1 ):
    r = np.asfarray(r)[:k]
    if r.size:
        if method == 0:
            return r[0] + np.sum(r[1:] / np.log2(np.arange(2, r.size + 1)))
        elif method == 1:
            # return np.sum(r / np.log2(np.arange(2, r.size + 2)))
            return np.sum(r / denominator_table[:r.shape[0]])
        else:
            raise ValueError('method must be 0 or 1.')
    return 0.

denominator_table = np.log2( np.arange( 2, 102 ))
def NDCGK(r,k,method=1):
    dcg_max = dcg_at_k(sorted(r, reverse=True), k, method)
    dcg_min = dcg_at_k(sorted(r),k, method)
    #assert( dcg_max >= dcg_min )
    if not dcg_max:
        return 0.
    dcg = dcg_at_k(r, k, method)
    #print dcg_min, dcg, dcg_max
    
    return (dcg - dcg_min) / (dcg_max - dcg_min)

def NDCGK_GT( r, best_r, worst_r, k, method = 1):
    dcg_max = dcg_at_k( sorted( best_r, reverse = True ), k, method )
    if worst_r == None:
        dcg_min = 0.
    else:
        dcg_min = dcg_at_k( sorted( worst_r ), k, method )
    if not dcg_max:
        return 0.
    dcg = dcg_at_k( r, k, method )
    return ( dcg - dcg_min ) / ( dcg_max - dcg_min )

