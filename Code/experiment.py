import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
from discreteMarkovChain import markovChain #pip install discreteMarkovChain
from numpy import linalg as LA
import time
import random
import joblib
import math
import os
from os.path import join as pjoin

from predict import prediction
from evaluation import evaluation,statistic
from calculate import calculation
from construct import read_graph_file

from selection import judge

def get_chain(path):
    transition_pairs,state_num,activity_map,state_map,tot_act = read_graph_file(path)
    if len(transition_pairs) == 0:
        return ((-1,-1),(-1,-1))
    mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity = calculation(transition_pairs,state_num,activity_map)
    twoargs = ((mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity),(transition_pairs,state_num,activity_map,state_map,tot_act))
    return twoargs

def process(args,vice_args,ground_truth):
    stats = statistic(ground_truth)
    transition_pairs,state_num,activity_map,state_map,tot_act = vice_args
    mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity = args #calculation(transition_pairs,state_num,activity_map)
    if len(stats['a_order'])==0:
        return None
    start_point = {'a_start':stats['a_order'][0][0],'s_start':stats['s_order'][0][0]}
    preds = prediction(tot_act,mix_time_curve,hit_times,stop_times,state_stable,act_stable,hit_times_in_activity,start_point)
    # print(preds)
    evals = evaluation(state_map,preds,stats)
    return {'ground_truth':stats,'prediction':preds,'eval':evals}

def batch_process(root_path,category = 'Industry',output_path_root,cache = True,mc_only = False):
    graph_SRC = category.split('-')[-2]
    category = category.split('-')[0]
    tool_indicator = None
    if root_path.find('Monkey')>=0:
        tool_indicator = 'rand'
    else:
        tool_indicator = 'super'
    tool = '-'+tool_indicator+'monkey-'
    os.makedirs(output_path_root,exist_ok = True)
    files = os.listdir(root_path)
    apps = set()
    for file in files:
        if file.find('final-')>=0:
            res = file.split('-')
            res = res[1].split('.')
            apps.add(res[0])
    apps = list(apps)
    apps.sort(reverse=False)
    abnormal_apps = []
    for app in apps:
        print(app)
        if app in ABNORMAL_APP:
            continue
        op_path = pjoin(output_path_root,category,app)
        args = None
        vice_args = None
        if os.path.exists(pjoin(op_path,graph_SRC+tool+'mc.json')):
            if cache:
                print('cached markov chain')
                args,vice_args = joblib.load(pjoin(op_path,graph_SRC+tool+'mc.json'))
            else:
                print('overwrite markov chain')
                path = root_path+'/final-'+ app + '.json'
                targ = get_chain(path)
                args,vice_args = targ
                joblib.dump(targ,pjoin(op_path,graph_SRC+tool+'mc.json'))
        else:
            os.makedirs(op_path,exist_ok = True)
            path = pjoin(root_path,'final-'+ app + '.json')
            targ = get_chain(path)
            args,vice_args = targ
            joblib.dump(targ,pjoin(op_path,graph_SRC+tool+'mc.json'))
        if mc_only:
            continue # if only construct markov chain
        if args[0] == -1:
            print('empty markov chain, continue')
            abnormal_apps.append(app)
            continue
        if len(args[4]) == 1:
            #only one activity:
            print('single activity, continue')
            abnormal_apps.append(app)
            continue
        for i in range(1,4):
            bgt = time.perf_counter()
            ground_truth = pjoin(root_path,'zhuanyi',app + tool + app+'-'+str(i)+'.json')
            if os.path.exists(pjoin(op_path,graph_SRC+'-'+tool+'-'+str(i)+'.json')):
                if cache:
                    print('cached! continue')
                    continue
                else:
                    print('overwrite!')
            result = process(args,vice_args,ground_truth)
            if result != None:
                result['proc_time'] = time.perf_counter()-bgt
                joblib.dump(result,pjoin(op_path,graph_SRC+'-'+tool+'-'+str(i)+'.json'))
            else:
                abnormal_apps.append(app)
                print('empty ground truth')
    abnormal_apps = list(set(abnormal_apps))
    return abnormal_apps



global_root = os.getcwd()# replace with your global path

def run_predict(graph_source,category,cache=True,mc_only=False):
    filter = []
    for sc in graph_source:
        res = batch_process(root_path = pjoin(global_root,sc),category,output_path_root = pjoin(global_root,'experimental_results'),cache=False,mc_only=mc_only)
        filter.extend(res)
    print(filter)
    return filter

def artifact_eval_industry():
    rasie NotImplementedError
industry_source = ['ArtifactEvaluation/IndustryMarkovChainMonkey','ArtifactEvaluation/IndustryMarkovChainWCTester']
open_source = ['ArtifactEvaluation/OpensourceMarkovChainMonkey','Opensource']
ABNORMAL_APP = ['SpriteMethodTest', 'weightchart', 'SpriteText', 'gestures', 'orgwikipedia', 'comeverysoftautoanswer', 'orgbeidebomber', 'orgjfedorfrozenbubble', 'comgluegadgethndroid', 'Amazed', 'comzoffccapplicationsaagtl', 'chblinkenlightsbattery', 'fileexplorer', 'DivideAndConquer', 'netcounter', 'aarddictandroid', 'RandomMusicPlayer', 'soundboard', 'baterrydog', 'beppareitswiftpfree', 'Triangle', 'LolcatBuilder', 'incmpmyLock', 'huvszaadsdroid', 'orgsmertyzooborns','comgluegadgethndroid','gestures', 'Triangle', 'SpriteText', 'comzoffccapplicationsaagtl','msword','mybabypiano']
