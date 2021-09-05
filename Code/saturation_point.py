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
import joblib
import math
import sys


def saturation_estimation(mc_json,trace_json):
    # predict whether the tool is saturated.
    pred = trace_json['prediction']['a_order']
    # print(len(pred))
    tot_effort = len(trace_json['ground_truth']['s_growth'])
    gt = trace_json['ground_truth']['a_order']
    TOT_END = trace_json['ground_truth']['TOT_TRANS']
    bottleneck = 0
    for ht in mc_json[0][5].values():
        bottleneck = max(np.max(ht),bottleneck)
    bottleneck = bottleneck + 20
    stp = sorted(pred,key=lambda x: (x[1],x[0]))
    gaps = [stp[i+1][1]-stp[i][1] for i in range(len(stp)-1)]
    gaps.sort()
    pred_saturated = gaps[-1]
    sature_point = 2*pred_saturated + 20
    
    gt_gaps = [gt[i+1][1]-gt[i][1] for i in range(len(gt)-1)]
    gt_gaps.append(TOT_END-gt[-1][1])
    def get_stopping_point(threshold,adpative = False):
        ff = 0
        tt = threshold
        for x in gt_gaps:
            ff += 1
            tt = threshold/max((1 if not adpative else 1-1.25*ff/(len(pred)-1)),0.125)
            if x > tt:
                break
        ret1 = 0
        saved_efforts = 0
        if ff < len(gt_gaps):
            ret1 = gt[ff][1]-tt
            saved_efforts = 0=
        else:
            saved_efforts = max(min(3000-tt,TOT_END-gt[ff-1][1]-tt),0)
        print('threshold {}, missrate {}, saved {} time'.format(threshold,1-ff/len(gt_gaps),saved_efforts)) 
        return 1-ff/len(gt_gaps),max(0,threshold-gt[-1][1]),saved_efforts,tt-gt[-1][1],ret1,threshold
    
    thold = max(sature_point,bottleneck)
    x1 = get_stopping_point(thold,adpative=True)
    # print('sature point {}, saturation missed {}, wasted {}. next_missed {}.'.format())
    # print('bottleneck {}, missed {}, wasted {}, next_missed {}.'.format())
    # x2 = get_stopping_point(bottleneck,adpative=True)
    # if x1 != 0:
    #     print(x1,x2)
    # print(gaps,gt_gaps)
    # print(pred_saturated,true_saturated)
    return x1


def batch_saturate(mc_file,root,app):
    monkey_mc_file,super_mc_file = mc_file
    mk_res = []
    major_mk = 0
    mk_wasted = 0
    mk_succ = 0
    for i in range(1,4):
        monkey_trace_org = joblib.load(pjoin(root,app,'all--randmonkey--'+str(i)+'.json'))
        mk_res.append(saturation_estimation(monkey_mc_file,monkey_trace_org))
        if mk_res[-1][0] <= 0.1:
            major_mk += 1
            mk_wasted += mk_res[-1][2]
    if major_mk >=2:
        mk_succ = 1
        mk_wasted / major_mk
    else:
        mk_wasted = 0
        
    
    sp_res = []
    major_sp = 0
    sp_wasted = 0
    sp_succ = 0
    for i in range(1,4):
        super_trace_org = joblib.load(pjoin(root,app,'all--supermonkey--'+str(i)+'.json'))
        sp_res.append(saturation_estimation(super_mc_file,super_trace_org))
        if sp_res[-1][0] <= 0.1:
            major_sp += 1
            sp_wasted += sp_res[-1][2]
    if major_sp >= 2:
        sp_succ = 1
        sp_wasted / major_sp
    else:
        sp_wasted = 0
    return mk_succ,sp_succ,mk_wasted,sp_wasted
def batch_distinct(root):

    files = os.listdir(root)
    sat = [[],[],[],[]]
    app_cnt = 0
    succ_app = 0
    for app in files:
        if app in ['SpriteMethodTest', 'weightchart', 'SpriteText', 'gestures', 'orgwikipedia', 'comeverysoftautoanswer', 'orgbeidebomber', 'orgjfedorfrozenbubble', 'comgluegadgethndroid', 'Amazed', 'comzoffccapplicationsaagtl', 'chblinkenlightsbattery', 'fileexplorer', 'DivideAndConquer', 'netcounter', 'aarddictandroid', 'RandomMusicPlayer', 'soundboard', 'baterrydog', 'beppareitswiftpfree', 'Triangle', 'LolcatBuilder', 'incmpmyLock', 'huvszaadsdroid', 'orgsmertyzooborns','comgluegadgethndroid','gestures', 'Triangle', 'SpriteText', 'comzoffccapplicationsaagtl','msword','mybabypiano']:
            # print('ignored')
            continue
        else:
            app_cnt += 1
            print('appname: ',app)
        monkey_mc_file = joblib.load(pjoin(root,app,'all-randmonkey-mc.json'))
        super_mc_file = joblib.load(pjoin(root,app,'all-supermonkey-mc.json'))
        mc_file = (monkey_mc_file,super_mc_file)
        mr,sr,mw,sw = batch_saturate(mc_file,root,app)
        sat[0].append(mr)
        sat[1].append(sr)
        sat[2].append(mw)
        sat[3].append(sw)
        if len(mc_monkey) <2:
            continue
    # saturation
    scc = [0,0,0,0]
    for i in range(4):
        for x in sat[i]:
            scc[i] += x
    print('Monkey Avg Precision: {}, Avg Savetime {}; WCTester Avg Precision {}, Avg Savetime {}'.format(scc[0]/app_cnt,scc[2]/app_cnt,scc[1]/app_cnt,scc[3]/app_cnt))


if __name__ == '__main__':
    iroot = None
    oroot = None

    output_file_path_root = None
    for cater in ['opensource','industrial']:
        ofp = pjoin(output_file_path_root,cater+'.txt')
        fffff = open(ofp, "w")
        sys.stdout = fffff 
        if cater == 'opensource':
            batch_distinct(oroot)
        else:
            batch_distinct(iroot)
        fffff.close()
