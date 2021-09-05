import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
from discreteMarkovChain import markovChain #pip install discreteMarkovChain
from numpy import linalg as LA
import time
import random
import json
import math
import os
from os.path import join as pjoin
from construct import read_graph_file,construct_chain
def cal_stable_distribution(mc:markovChain,activity_map:dict):
    mc.computePi('power')
    Pi_State = mc.pi
    Pi_Activity = dict()
    for i in range(len(Pi_State)):
        Pi_Activity[activity_map[i]] = 0
    for i in range(len(Pi_State)):
        Pi_Activity[activity_map[i]] += Pi_State[i]
    return Pi_State,Pi_Activity
def cal_hitting_time(mc:markovChain,hittingset = [0]):
    # targets:
    P = mc.getTransitionMatrix()
    one = np.ones(mc.size)
    one[hittingset] = 0
    mask = np.zeros(mc.size)
    for i in range(mc.size):
        if i in hittingset:
            mask[i]=1

    k1 = np.zeros(mc.size)
    k2 = one + P.dot(k1)
    i = 0
    while(LA.norm(k1-k2)/max((LA.norm(k2)*LA.norm(k1)),1)>1e-6) and i < 2000:
        k1=k2
        k2 = one + P.dot(k1)
        np.putmask(k2, mask, 0)
        i += 1
    return k2
def cal_stopping_time(mc:markovChain,origin = [0]):
    P = mc.getTransitionMatrix()
    P = P.T
    one = np.ones(mc.size)
    one[origin] = 0
    mask = np.zeros(mc.size)
    for i in range(mc.size):
        if i in origin:
            mask[i]=1

    k1 = np.zeros(mc.size)
    k2 = one + P.dot(k1)
    i = 0
    time1 = time.perf_counter()
    while (LA.norm(k1-k2)/max((LA.norm(k2)*LA.norm(k1)),1)>1e-8 and i < 5000):
        k1=k2
        k2 = one + P.dot(k1)
        np.putmask(k2, mask, 0)
        i += 1
    return k2
def cal_mixing_time(mc:markovChain,threshold = 1e-6):
    k1 = np.zeros(mc.size)
    k1[0] = 1
    P = mc.getTransitionMatrix()
    P = P.T
    k2 = P.dot(k1)
    iter_time = 1
    curve = []
    dist = LA.norm(k1-k2)
    curve.append(dist)
    while dist > threshold and iter_time < 1000:
        k1 = k2
        k2 = P.dot(k1)
        iter_time += 1
        dist = LA.norm(k1-k2)
        curve.append(dist)
    return curve
def cal_hitting_time_in_activity(mc:markovChain,activity_map:dict):
    reverse_map = dict()
    for v in activity_map.values():
        reverse_map[v] = []

    for key,value in activity_map.items():
        reverse_map[value].append(key)
    result = dict()
    for key,value in reverse_map.items():
        result[key] = cal_hitting_time(mc,value)
    return result

def calculation(transition_pairs,state_num,activity_map):
    t1 = time.perf_counter()
    t2 = time.perf_counter()
    mc = construct_chain(transition_pairs,state_num)
    t3 = time.perf_counter()
    state_stable,act_stable = cal_stable_distribution(mc,activity_map)
    t4 = time.perf_counter()
    mix_time_curve = cal_mixing_time(mc,threshold=1e-8)
    t5 = time.perf_counter()
    hit_times = np.zeros(shape = (state_num,state_num))
    for i in range(state_num):
        hit_times[i] = cal_hitting_time(mc,hittingset=[i])
    
    hit_times = hit_times.transpose()
    t6 = time.perf_counter()
    hit_times_in_activity =  cal_hitting_time_in_activity(mc,activity_map)
    t7 = time.perf_counter()
    stop_times = cal_stopping_time(mc)
    t8 = time.perf_counter()
    # print('mix time curve',mix_time_curve)
    # print('hit times',hit_times)
    # print('stop time',stop_times)
    # print('hit times in act',hit_times_in_activity)
    # print(state_stable,act_stable)

    # print('total {} s, read file {} s, construct chain {}s, calculate stable distribution {} s, calculate mixing curve {} s, calculate communication {} s, calculate activity communication {} s, calculate stopping time {} s'.format(t8-t1,t2-t1,t3-t2,t4-t3,t5-t4,t6-t5,t7-t6,t8-t7))
    return mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity
