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
def model_accuracy(root,tool):
    cater = 'industry'
    if root.find('opensource') >= 0:
        cater='opensource'
    tl = 'monkey'
    if tool.find('super') >=0:
        tl = 'wctester'
    cutting_off = 4
    ofp = pjoin(output_file_path_root,cater+'-'+tl+'-'+str(int(100/cutting_off))+'.txt')
    fff = open(ofp, "w")
    sys.stdout = fff 
    files = os.listdir(root)
    for app in files:
        if app in ['SpriteMethodTest', 'weightchart', 'SpriteText', 'gestures', 'orgwikipedia', 'comeverysoftautoanswer', 'orgbeidebomber', 'orgjfedorfrozenbubble', 'comgluegadgethndroid', 'Amazed', 'comzoffccapplicationsaagtl', 'chblinkenlightsbattery', 'fileexplorer', 'DivideAndConquer', 'netcounter', 'aarddictandroid', 'RandomMusicPlayer', 'soundboard', 'baterrydog', 'beppareitswiftpfree', 'Triangle', 'LolcatBuilder', 'incmpmyLock', 'huvszaadsdroid', 'orgsmertyzooborns','comgluegadgethndroid','gestures', 'Triangle', 'SpriteText', 'comzoffccapplicationsaagtl','msword','mybabypiano']:
            # print('ignored')
            continue
        for i in range(1,4):
            trace_org = joblib.load(pjoin(root,app,tool+str(i)+'.json'))
            predicts = trace_org['eval']['activity']
            # print(predicts['eval_act_alloc'])
            js = predicts['eval_act_alloc']['JSDistance']
            
            if len(predicts['eval_act_alloc']['NDCG']) > 4:
                ndcg = predicts['eval_act_alloc']['NDCG'][int(len(predicts['eval_act_alloc']['NDCG'])/4)]
            else:
                ndcg = 'None'
            # top5 = predicts['eval_act_alloc']['TopK']
            print(js,ndcg)
    fff.close()

if __name__ == '__main__':
    model_accuracy(oroot,tools[0])
    model_accuracy(oroot,tools[1])
    model_accuracy(iroot,tools[0])
    model_accuracy(iroot,tools[1])