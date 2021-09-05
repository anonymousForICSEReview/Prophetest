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
def mock():
    max_state = 10000
    max_connect = 20
    max_act = 100
    transition_pairs = [(i,(j+i)%max_state,1/max_connect) for j in range(max_connect) for i in range(max_state)]
    state_num = max_state
    activity_map = {i:random.randint(0,max_act) for i in range(max_state)}
    return transition_pairs,state_num,activity_map


def prediction(tot_act,mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity,start_point):
    # mix time analysis
    None == None

    # hit time analysis: predict visit order
    initialize = start_point['s_start']
    activity_visit_order = []
    for key,value in hit_times_in_activity.items():
        activity_visit_order.append((key,value[initialize]))
    activity_visit_order.sort(key=lambda x:x[1])
    
    state_visit_order = [(i,stop_times[i]) for i in range(len(stop_times))]
    if initialize != 0:
        target_time = hit_times[initialize]
        state_visit_order = [(i,target_time[i]) for i in range(len(target_time))]
    state_visit_order.sort(key=lambda x:(x[1],x[0]))
    
    # coverage growth analysis:
    act_hmax = 0
    for ht in hit_times_in_activity.values():
        act_hmax = max(np.max(ht),act_hmax)
    cs = np.arange(0.05, 1-1/(tot_act+1), 0.05)
    alpha = 1
    beta = 0.8
    gamma = 0
    activity_growth = [alpha*2*act_hmax*math.ceil(math.log(1/(1-beta*c),2))-gamma for c in cs ]

    state_hmax = 0 #TODO
    for ht in hit_times:
        state_hmax = max(np.max(ht),state_hmax)
    state_growth = []
    # bugdet allocation analysis: 
    # simply the stable distribution

    preds = {'a_order':activity_visit_order,'s_order':state_visit_order,\
    'a_cnt':act_stable,'s_cnt':state_stable,\
    'a_growth':activity_growth,'s_growth':state_growth,\
    'a_hmax':act_hmax,'s_hmax':state_hmax}
    return preds


    

    

 

