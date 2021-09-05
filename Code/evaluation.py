import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
from discreteMarkovChain import markovChain #pip install discreteMarkovChain
from numpy import linalg as LA
import time
import random
import json
import math
from metrics import topK,NDCGK,NDCGK_GT,JSDist,KLDist
import os
from os.path import join as pjoin

def eval_time_activity(preds,stats):
    
    time_allocation_activity = sorted(preds['a_cnt'].items(),key = lambda kv:(kv[1], kv[0]),reverse=True)
    true_activity_cnt = sorted(stats['a_cnt'].items(),key = lambda kv:(kv[1], kv[0]),reverse=True)
    pred_alloc_act = set([item[0] for item in time_allocation_activity])
    gt_alloc_act = set([item[0] for item in true_activity_cnt])
    counted_act = pred_alloc_act & gt_alloc_act
    counted_act = list(counted_act)
    counted_act.sort()
    p = np.asfarray([preds['a_cnt'][itm] for itm in counted_act])
    q = np.asfarray([stats['a_cnt'][itm] for itm in counted_act])
    p = p/p.sum()
    q = q/q.sum()
    jsdist = JSDist(p,q)
    pp = []
    qq = []
    for a in preds['a_cnt'].keys():
        pp.append(preds['a_cnt'][a])
        qq.append(stats['a_cnt'].get(a,0))
    pp = np.asfarray(pp)
    qq = np.asfarray(qq)
    pp = pp/pp.sum()
    qq = qq/qq.sum()
    fjsdist = JSDist(pp,qq)
    pred_alloc_list = [item[0] for item in time_allocation_activity if item[0] in counted_act]
    # case 1: do not filter the act appear in gt but not in prediction
    # which means we treat the not predicted activity as prediction failure.
    gt_alloc_list_not_filter = [item[0] for item in true_activity_cnt] 
    # case 2:  filter the act appear in gt but not in prediction
    gt_alloc_list_filter = [item[0] for item in true_activity_cnt if item[0] in counted_act] 
    filter_k_max = min(len(pred_alloc_list),len(gt_alloc_list_filter))
    not_filter_k_max = min(len(pred_alloc_list),len(gt_alloc_list_not_filter))
    topKRecordFilter = []
    topKRecordNotFilter = []
    for k in range(1,filter_k_max+1):
        topKRecordFilter.append(topK(k,pred_alloc_list,gt_alloc_list_filter))
    for k in range(1,not_filter_k_max+1):
        topKRecordNotFilter.append(topK(k,pred_alloc_list,gt_alloc_list_not_filter))

    rel = []
    regularizer = len(pred_alloc_act|gt_alloc_act)+1
    for i in range(len(time_allocation_activity)):
        score = 0
        for j in range(len(gt_alloc_list_not_filter)):
            if time_allocation_activity[i][0] == gt_alloc_list_not_filter[j]:
                nb = j
                score = regularizer/(regularizer+abs(j-i)*abs(j-i))
                break
        rel.append(score)
    NDCGRecord = []
    best_r = [1 for _ in range(len(counted_act))]
    best_r.extend([0 for _ in range(len(time_allocation_activity)-len(counted_act))])
    worst_r = [0 for _ in range(len(time_allocation_activity))]
    for k in range(1,len(time_allocation_activity)+1):
        NDCGRecord.append(NDCGK_GT(rel,best_r,worst_r,k))
    return {'JSDistance':jsdist,'FullJSDistance':fjsdist,'topKFilter':topKRecordFilter,'topKNotFilter':topKRecordNotFilter,'NDCG':NDCGRecord}

def eval_order_activity(preds,stats):
    pred_act_visit_order = preds['a_order']
    gt_act_visit_order = stats['a_order']
    def cluster(inpt):
        return inpt
        if len(inpt) == 1:
            return [(inpt[0][0],inpt[0][1],0)]
        CLUSTER_GRP = min(5,len(inpt))
        res = [0]
        for i in range(1,len(inpt)):
            res.append(inpt[i][1]-inpt[i-1][1])
        res.sort(reverse=True)
        res.extend([0])
        # print(CLUSTER_GRP)
        # print(res)
        # if res[CLUSTER_GRP] == res[CLUSTER_GRP-1]:
        #     print('more group than needed!')
        #     CLUSTER_GRP  = CLUSTER_GRP -1
        # if res[CLUSTER_GRP] == res[CLUSTER_GRP-1]:
        #     print('unable to solve')
        # while res[CLUSTER_GRP] <= 1:
        #     CLUSTER_GRP -= 1
        #     if CLUSTER_GRP ==1:
        #         break
        res = res[CLUSTER_GRP]
        DELI = 0
        outpt = [(inpt[0][0],inpt[0][1],DELI)]
        for i in range(1,len(inpt)):
            if inpt[i][1] - inpt[i-1][1] >= res:
                DELI += 1
            outpt.append((inpt[i][0],inpt[i][1],DELI))
        return outpt
    pred_act_visit_order = cluster(pred_act_visit_order)
    pred_set = set(item[0] for item in pred_act_visit_order)
    gt_act_visit_order = cluster(gt_act_visit_order)
    gt_set = set(item[0] for item in gt_act_visit_order)
    common_set = gt_set&pred_set
    regularizer = 5
    NDCGRecord = []
    rel = []
    for i in range(len(pred_act_visit_order)):
        score = 0
        for j in range(len(gt_act_visit_order)):
            item = pred_act_visit_order[i]
            cand = gt_act_visit_order[j]
            if item[0]==cand[0]:
                score = 1/(1+abs(i-j)*abs(i-j))
                break
        rel.append(score)
    k_max = min(len(pred_act_visit_order),len(gt_act_visit_order))
    best_r = [1 for _ in range(len(common_set))]
    best_r.extend([0 for _ in range(k_max-len(common_set))])
    worst_r = [0 for _ in range(k_max)]
    for k in range(1,len(pred_act_visit_order)+1):
        NDCGRecord.append(NDCGK_GT(rel,best_r,worst_r,k))
    pred_a =  [x[0] for x in preds['a_order']]
    gt_a = [x[0] for x in stats['a_order'] if x[0] in pred_a]
    filter_pred_a = [x for x in pred_a if x in gt_a]
    FilterTopK = []
    FullTopK = []
    for k in range(1,len(gt_a)+1):
        FilterTopK.append(topK(k,filter_pred_a,gt_a))
        FullTopK.append(topK(k,pred_a,gt_a))
    # print({'NDCG':NDCGRecord,'FullTopK':FullTopK,'FilterTopK':FilterTopK})
    return {'NDCG':NDCGRecord,'FullTopK':FullTopK,'FilterTopK':FilterTopK}
    
def eval_growth_activity(preds,stats):
    pred_growth = preds['a_growth']
    gt_growth = stats['a_growth']
    return {'pred_curve':pred_growth,'gt_curve':gt_growth}

def eval_act(preds,stats):
    act_time_alloc_eval_results = eval_time_activity(preds,stats)
    act_order_eval_results = eval_order_activity(preds,stats)
    act_growth_eval_results = eval_growth_activity(preds,stats)
    return {'eval_act_alloc':act_time_alloc_eval_results,\
    'eval_act_order':act_order_eval_results,\
    'eval_act_growth':act_growth_eval_results}
def evaluation(state_map,preds,stats):
    a_eval_dict = eval_act(preds,stats)
    s_eval_dict = eval_s(state_map,preds,stats)
    return {'activity':a_eval_dict,'state':s_eval_dict}

def eval_s(state_map,preds,stats):
    s_alloc = eval_time_state(state_map,preds,stats)
    s_ord = eval_order_state(state_map,preds,stats)
    s_gh = eval_growth_state(state_map,preds,stats)
    return {'eval_state_alloc':s_alloc,\
    'eval_state_order':s_ord,\
    'eval_state_growth':s_gh
    }
def eval_time_state(state_map,preds,stats):
    pred_state_cnt = preds['s_cnt']
    gt_state_cnt = stats['s_cnt']
    common = []
    for i in range(len(pred_state_cnt)):
        if i in gt_state_cnt:
            common.append(i)
    p_pre = []
    fp_pre = []
    q_pre = []
    fq_pre = []
    for i in range(len(pred_state_cnt)):
        fp_pre.append(pred_state_cnt[i])
        fq_pre.append(gt_state_cnt.get(i,0))
    for x in common:
        p_pre.append(pred_state_cnt[x])
        q_pre.append(gt_state_cnt[x])
    p = np.asfarray(p_pre)
    q = np.asfarray(q_pre)
    p = p/p.sum()
    q = q/q.sum()
    jsdist = JSDist(p,q)
    fp = np.asfarray(fp_pre)
    fq = np.asfarray(fq_pre)
    fq = fq/fq.sum()
    fp = fp/fp.sum()
    fjsdist = JSDist(fp,fq)
    pred_s = [(i,pred_state_cnt[i]) for i in range(len(pred_state_cnt))]
    pred_s = sorted(pred_s,key = lambda kv:(kv[1], kv[0]),reverse=True)
    pred_s = [itm[0] for itm in pred_s]
    gt_s = sorted(gt_state_cnt.items(),key = lambda kv:(kv[1], kv[0]),reverse=True)
    gt_s = [itm[0] for itm in gt_s]
    gt_s = [x for x in gt_s if x!= -1]
    filter_pred_s = [x for x in pred_s if x in gt_s]
    max_k = min(len(pred_s),len(gt_s))
    topKFilter = []
    topKNotFilter = []
    for k in range(1,max_k+1):
        topKNotFilter.append(topK(k,pred_s,gt_s))
    for k in range(1,len(gt_s)+1):
        topKFilter.append(topK(k,filter_pred_s,gt_s))
    return {'JSDistance':jsdist,'FullJSDistance':fjsdist,'topKFilter':topKFilter,'topKNotFilter':topKNotFilter}
def eval_order_state(state_map,preds,stats):
    pred_order = preds['s_order']
    gt_order = stats['s_order']
    pred_s = [x[0] for x in pred_order]
    gt_s = [x[0] for x in gt_order if x[0]!= -1]
    filter_pred_s = [x for x in pred_s if x in gt_s]
    FilterTopK = []
    FullTopK = []
    for k in range(1,min(len(gt_s)+1,100)):
        FilterTopK.append(topK(k,filter_pred_s,gt_s))
        FullTopK.append(topK(k,pred_s,gt_s))
    return {'FullTopK':FullTopK,'FilterTopK':FilterTopK}

def eval_growth_state(state_map,preds,stats):
    return 



def statistic(ground_truth):
    json_dict = None
    with open(ground_truth,'r') as f:
        json_dict = json.load(f)
        
    activity_visit_cnt = dict()
    state_visit_cnt = dict()
    state_visit_order = []
    activity_visit_order = []
    state_visit_growth = [0]
    activity_visit_growth = [0]
    newly_state = set()
    counter = 0

    for  single_dict in json_dict:
        assert len(single_dict.items()) == 1
        Hash,Value = list(single_dict.items())[0]
        item = {'activity':Value[1],'state':int(Value[0])}
        if item['activity'] in activity_visit_cnt:
            activity_visit_cnt[item['activity']] += 1
            activity_visit_growth.append(activity_visit_growth[-1])
        else:
            activity_visit_cnt[item['activity']] = 1
            activity_visit_order.append((item['activity'],counter))
            activity_visit_growth.append(activity_visit_growth[-1]+1)
        
        if item['state'] == -1:
            newly_state.add(Hash)
        if item['state'] in state_visit_cnt:
            state_visit_cnt[item['state']] += 1
            state_visit_growth.append(state_visit_growth[-1])
        else:
            state_visit_cnt[item['state']]  = 1
            state_visit_order.append((item['state'],counter))
            state_visit_growth.append(state_visit_growth[-1]+1)
        counter += 1
    # activity_visit_order.append(('END',counter))
    # state_visit_order.append(('END',counter))
    stats = {'a_cnt':activity_visit_cnt,'s_cnt':state_visit_cnt,\
        'a_order':activity_visit_order,'s_order':state_visit_order,\
        'a_growth':activity_visit_growth,'s_growth':state_visit_growth,'TOT_TRANS':counter}
    return stats
