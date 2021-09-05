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


groot = os.getcwd()
iroot = pjoin(groot,'industry')

oroot = pjoin(goort,'opensource')
output_file_path_root = pjoin(goort,'output')
tools = ['all--randmonkey--','all--supermonkey--']

def tool_selection(root):
    cater = 'industry'
    if root.find('opensource') >= 0:
        cater='opensource'
    ofp = pjoin(output_file_path_root,cater+'selection.txt')
    files = os.listdir(root)
    def obtain_all_activity(app,tool):
        activities = set()
        for i in range(1,4):
            trace_org = joblib.load(pjoin(root,app,tool+str(i)+'.json'))
            gt = trace_org['ground_truth']['a_cnt']
            # print(tool,'TOT_TRANS,',trace_org['ground_truth']['TOT_TRANS'])
            for key in gt.keys():
                activities.add(key)
        return activities
    def get_bottleneck(app,tool):
        ret = 0
        for i in range(1,4):
            trace_org = joblib.load(pjoin(root,app,tool+str(i)+'.json'))
            
            btneck = trace_org['prediction']['a_hmax']
            stps = trace_org['prediction']['a_order']
            stp = max([stps[i+1][1]-stps[i][1] for i in range(len(stps)-1)])
            # stp = max()
            ret += max(min(btneck,2*stp),20)
        return ret/3

    def predict_likely_visited_activity(app,tool):
        activities = set()
        for i in range(1,4):
            trace_org = joblib.load(pjoin(root,app,tool+str(i)+'.json'))
            pred = trace_org['prediction']['a_cnt']
            for key, value in pred.items():
                if value > 1e-2:
                    activities.add(key)
        return activities
    true_cnt = 0
    app_cnt = 0
    monkey_advant = 0
    wc_advant = 0
    files.sort()
    for app in files:
        
        if app in ['SpriteMethodTest', 'weightchart', 'SpriteText', 'gestures', 'orgwikipedia', 'comeverysoftautoanswer', 'orgbeidebomber', 'orgjfedorfrozenbubble', 'comgluegadgethndroid', 'Amazed', 'comzoffccapplicationsaagtl', 'chblinkenlightsbattery', 'fileexplorer', 'DivideAndConquer', 'netcounter', 'aarddictandroid', 'RandomMusicPlayer', 'soundboard', 'baterrydog', 'beppareitswiftpfree', 'Triangle', 'LolcatBuilder', 'incmpmyLock', 'huvszaadsdroid', 'orgsmertyzooborns','comgluegadgethndroid','gestures', 'Triangle', 'SpriteText', 'comzoffccapplicationsaagtl','msword','mybabypiano']:
            # print('ignored')
            continue
        else:
            None
        ma = obtain_all_activity(app,tools[0])
        wa = obtain_all_activity(app,tools[1])
        maps = get_bottleneck(app,tools[0])
        wap = get_bottleneck(app,tools[1])
        if len(ma) > len(wa):
            monkey_advant += 1
        if len(wa) > len(ma):
            wc_advant += 1 
        # print(len(ma),len(wa))
        # print(len(maps)/len(wap),len(maps&wap)/len(maps|wap))
        # print(maps/wap)
        pred = maps/wap >= 1
        label= len(ma)/len(wa) >= 1
        label_mark = r'\xmark'
        if not pred^label :
            true_cnt += 1
            label_mark = r'\cmark'
        app_cnt += 1
        true_label = 0
        monkey_mark = r'\cmark'
        wc_mark = r'\xmark'
        if pred == 1:
            wc_mark = r'\cmark'
            monkey_mark = r'\xmark'
        print('app {}, prediction {} (1: monkey 0:wctester), ground truth {} ((1: monkey 0:wctester))'.format(app,int(pred),int(label)))
    print('Average Results: on {} apps ({}\%) Monkey wins, on {} apps ({}\%) WCTester wins, Selection Accuracy {}.'.format(app_cnt-wc_advant,1-wc_advant/app_cnt,wc_advant,wc_advant/app_cnt,true_cnt/app_cnt))
    # fff = open(ofp, "w")
    # sys.stdout = fff 

tool_selection(iroot)