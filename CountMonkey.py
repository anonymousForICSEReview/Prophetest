import os
import json


def BuildGraph(appName, monkeyName,fileGraphPath,stateFilePath):
    if os.path.exists(fileGraphPath+"transition"):
        os.mkdir(fileGraphPath+"transition")
    with open(fileGraphPath+'final-' + appName + '.json', 'r') as load_f:
        recordGraph = json.load(load_f)
    recordHashToNum = {}
    recordHashToActId = {}
    recordNumToHash = recordGraph['state_map']
    for key in recordNumToHash.keys():
        recordHashToNum[recordNumToHash[key]] = key
    recordNumToActId = recordGraph['act_map']
    for key in recordNumToActId.keys():
        recordHashToActId[recordNumToHash[key]] = recordNumToActId[key]
    dirList = os.listdir(stateFilePath)
    for dir in dirList:
        if dir.find(monkeyName) < 0:
            continue
        if dir.find(appName) < 0:
            continue
        fileList = os.listdir(stateFilePath + dir)
        fileList = sorted(fileList)
        returnList = []
        for i in range(0, len(fileList) - 1):
            fileName = fileList[i]
            if fileName.endswith(".json"):
                with open(stateFilePath + dir + "/" + fileName, 'r') as load_f:
                    load_dict = json.load(load_f)
                returnMap = {}
                currHash = load_dict['newValue']
                if currHash is None:
                    continue
                if currHash in recordHashToNum.keys():
                    returnMap[currHash] = (recordHashToNum[currHash], recordHashToActId[currHash])
                else:
                    returnMap[currHash] = (-1, load_dict['act_id'])
                returnList.append(returnMap)
        print(len(returnList))
        filename = fileGraphPath+"transition/" + appName + "-" + dir + '.json'
        with open(filename, 'w') as file_obj:
            json.dump(returnList, file_obj)


if __name__ == '__main__':
    appList = ['goodrx', 'absworkoutdailyfitness', 'mirrorzoomexposure', 'youtube', 'mybabypiano', 'linewebtoon',
               'trivago', 'duolingo', 'filtersforselfie', 'marvelcomics', 'msword', 'googletranslate', 'zedge',
               'sketchdrawpaint', 'dictionarymerriamwebster']
    monkeyList = ['randmonkey']
    for l in appList:
        for ll in monkeyList:
            BuildGraph(l, ll)
