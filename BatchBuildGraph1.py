import os
import json
from GetHash import hash_element
import math


def computeArea(strArea):
    strArea = strArea.lstrip("[")
    strArea = strArea.rstrip("]")
    tempStrList = strArea.split("][")
    tempStrList1 = tempStrList[0].split(',')
    tempStrList2 = tempStrList[1].split(',')
    a = int(tempStrList1[0])
    b = int(tempStrList1[1])
    c = int(tempStrList2[0])
    d = int(tempStrList2[1])
    area = (c - a) * (d - b)
    return area

def dfsGetAllElem(dictt):
    if "is_source" in dictt.keys():
        global controlAreaStr
        controlAreaStr = dictt['bound']
    if "ch" not in dictt.keys():
        return
    listTemp = dictt['ch']
    for l in listTemp:
        if str(l) == "{}":
            continue
        dfsGetAllElem(l)


def BuildGraph(appName, projectDir, outputDir):
    returnMap = {}
    recordacidMap = {}
    listFile = os.listdir(projectDir)
    for dir in listFile:
        if dir.find(appName) < 0:
            continue
        listt = os.listdir(projectDir + dir)
        listt = sorted(listt)
        for i in range(0, len(listt)):
            fileName = listt[i]
            if fileName.endswith(".json"):
                with open(projectDir + dir + "/" + fileName, 'r') as load_f:
                    load_dictState = json.load(load_f)
                if load_dictState['newValue'] is None:
                    continue
                recordacidMap[load_dictState['newValue']] = load_dictState['act_id']

    stateMap = {}
    act_map = {}
    ta = 0
    recordtempMap = {}
    for fileName in recordacidMap.keys():
        stateMap[ta] = fileName
        act_map[ta] = recordacidMap[fileName]
        recordtempMap[fileName] = ta
        ta += 1
    returnMap['state_map'] = stateMap
    returnMap['act_map'] = act_map
    returnMap['state_num'] = len(recordacidMap.keys())
    recordFinalMap = {}
    for dir in listFile:
        if dir.find(appName) < 0:
            continue
        listt = os.listdir(projectDir + dir)
        listt = sorted(listt)
        for i in range(0, len(listt) - 1):
            fileName = listt[i]
            if fileName.endswith(".json"):
                with open(projectDir + dir + "/" + fileName, 'r') as load_f:
                    load_dictState = json.load(load_f)
                recordacidMap[load_dictState['newValue']] = load_dictState['act_id']
                global controlAreaStr
                controlAreaStr = ""
                dfsGetAllElem(load_dictState)
                hashControl = hash_element(load_dictState)

                if not listt[i + 1].endswith(".json"):
                    continue
                with open(projectDir + dir + "/" + listt[i + 1], 'r') as load_f1:
                    load_dictNextState = json.load(load_f1)
                if load_dictState['newValue'] is None or load_dictNextState['newValue'] is None:
                    continue
                stateArea = computeArea(load_dictState['bound'])
                if stateArea == 0:
                    continue
                if load_dictState['bound'] == "" or controlAreaStr == "":
                    if load_dictState['ua_type'] == 100:
                        nextStateHash = stateArea * 0.1
                        at = math.sqrt(nextStateHash)
                        controlAreaStr = "[0,0][" + str(at).split(".")[0] + "," + str(at).split(".")[0] + "]"
                    elif load_dictState['ua_type'] == 0:
                        controlAreaStr = "[0,0][150,150]"
                    else:
                        controlAreaStr = "[0,0][100,100]"

                controlArea = computeArea(controlAreaStr)

                if load_dictState['newValue'] not in recordFinalMap.keys():
                    listTemp = []
                    listTemp.append(
                        (str(load_dictNextState['newValue']) + "\t" + str(hashControl), controlArea * 1.0 / stateArea))
                    recordFinalMap[load_dictState['newValue']] = listTemp
                else:
                    listTemp = recordFinalMap[load_dictState['newValue']]
                    if (str(load_dictNextState['newValue']) + "\t" + str(hashControl),
                        controlArea * 1.0 / stateArea) not in listTemp:
                        listTemp.append((str(load_dictNextState['newValue']) + "\t" + str(hashControl),
                                         controlArea * 1.0 / stateArea))
                backArea = computeArea("[0,0][100,100]")
                if load_dictNextState['newValue'] not in recordFinalMap.keys():
                    listTemp = []
                    listTemp.append((load_dictState['newValue'], backArea * 1.0 / stateArea))
                    recordFinalMap[load_dictNextState['newValue']] = listTemp
                else:
                    listTemp = recordFinalMap[load_dictNextState['newValue']]
                    if (load_dictState['newValue'], backArea * 1.0 / stateArea) not in listTemp:
                        recordFinalMap[load_dictNextState['newValue']].append(
                            (load_dictState['newValue'], backArea * 1.0 / stateArea))
    recordTempMap = {}
    for key in recordFinalMap:
        recordTempMap[key] = {}
        recordUse = []
        tempList = recordFinalMap[key]
        for templ in tempList:
            nextStateHash = templ[0].split("\t")[0]
            if nextStateHash not in recordUse:
                recordTempMap[key][nextStateHash] = templ[1]
                recordUse.append(nextStateHash)
            else:
                currentPr = recordTempMap[key][nextStateHash]
                recordTempMap[key][nextStateHash] = currentPr + templ[1]
            if nextStateHash == key:
                continue
    transition = []
    for key in recordTempMap.keys():
        tempMap = recordTempMap[key]
        totPr = 0.1
        for templ in tempMap.keys():
            if templ == key:
                continue
            totPr += tempMap[templ]
        for templ in tempMap.keys():
            if templ == key:
                continue
            if key not in recordtempMap.keys():
                continue
            if recordtempMap[key] is None:
                continue
            if templ is None:
                continue
            transition.append((recordtempMap[key], recordtempMap[templ], tempMap[templ] / totPr))
        transition.append((recordtempMap[key], recordtempMap[key], 0.1 / totPr))
    returnMap['transition'] = transition
    filename = outputDir + '/' + 'final-' + appName + '.json'
    with open(filename, 'w') as file_obj:
        json.dump(returnMap, file_obj)


import time

if __name__ == '__main__':
    outputDir = ""
    inputDir = ""
    methodList = ['randmonkey', 'supermonkey', 'randape', 'stoatx']
    appList = ['goodrx', 'absworkoutdailyfitness', 'mirrorzoomexposure', 'youtube', 'mybabypiano', 'linewebtoon',
               'trivago', 'duolingo', 'filtersforselfie', 'marvelcomics', 'msword', 'googletranslate', 'zedge',
               'sketchdrawpaint', 'dictionarymerriamwebster']
    f = open(outputDir + "buildgraphtime.txt", 'w')
    for l in appList:
        start = time.time()
        BuildGraph(l, inputDir, outputDir)
        end = time.time()
        f.write(l + "\t" + str(end - start) + "\n")
    f.close()
