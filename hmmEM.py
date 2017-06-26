#encoding=utf-8
import numpy as np
from hmmlearn import hmm
import os
import poiTools as pt
import dictGeneTools as dgt

from sklearn import preprocessing

def hmmEM(poiList,lengthList,lenTrainData):
    dictgt = dgt.reclassifyDict()
    PT = pt.poiTools()
    poiList = PT.poi2newCate(poiList,dictgt)
    if(len(poiList) < sum(lengthList)):
        return -1
    # 寻找长度适中的poi序列作为测试集
    sortedlength = sorted(lengthList)
    idxmedian = sortedlength[int(np.ceil(len(sortedlength)/2))]
    poiTest = []
    poiTrain = []
    lengthNew = []
    idxprev = 0
    for i,length in enumerate(lengthList):
        if(length != idxmedian):
            poiTrain.extend(poiList[idxprev:idxprev+length])
            lengthNew.append(length)
            idxprev = idxprev + length
        else:
            poiTest.extend(poiList[idxprev:idxprev+length])
            idxprev = idxprev + length

    # poiTrain = poiList[0:lenTrainData]
    # poiTest = poiList[lenTrainData:]
    setTrain  = set(poiTrain)
    setTest = set(poiTest)
    if(not setTrain > setTest ):  # 必须保证测试集是训练集的子集
        return -1

    # LabelEncoder 为训练样本序列编码，以满足hmmlearn.fit()的要求，详见云笔记
    le = preprocessing.LabelEncoder()
    le.fit( list(setTrain) )
    trainEncode = le.transform(poiTrain)
    testEncode = le.transform(poiTest)

    X = np.atleast_2d(trainEncode)
    Xtest = np.atleast_2d(testEncode)

    # ohe = OneHotEncoder()
    # ohe.fit(np.array(range(8)).reshape(8,1))
    # poiList = np.array(poiList).reshape(len(poiList),1)
    # poiArray = ohe.transform(poiList).toarray()
    # poiArray = np.atleast_2d(poiArray)
    # #Y = np.atleast_2d(np.array([0,1,2,3,4,5,6,7,8,9,10,11,12]))
    lengthList = np.array(lengthList)
    remodel = hmm.MultinomialHMM(n_components=5)

    modelBest = []
    scoreHighest = -1000000
    for i in range(15):
        # print len(X[0])
        # print sum(lengthNew)
        remodel.fit(X.T,lengthNew)
        modelScore = remodel.score(X.T,lengthNew)
        if(modelScore > scoreHighest):
            scoreHighest = modelScore
            modelBest = remodel
        #print modelScore
    # 现在的测试是不严谨的，没有考虑‘测试集中存在训练集未出现的样例’的情况

    hstate = modelBest.predict(Xtest.T)
    predictTrue = catePredict(modelBest.emissionprob_, hstate, Xtest)
    print predictTrue
    # print 'Xtest = ' + str(Xtest)
    # print hstate
    # print 'emission prob:'
    # print modelBest.emissionprob_
    # print 'transition prob:'
    # print modelBest.transmat_
    # print '10 rounds done'
    return predictTrue

def catePredict(emission,hstate,Xtest):
    result = 0
    row = emission[hstate[-1]].tolist()
    cate = row.index(max(row))
    # print cate
    # print Xtest[0][-1]
    # print Xtest
    if(cate == Xtest[0][-1]):
        result = 1
    return  result


# 遍历所有用户的测试代码
PT = pt.poiTools()
cntAva = 0
dirpath = os.path.abspath('.') + '\\' + 'PoiPtPerUser'
pathDir =  os.listdir(dirpath)
cntUser = 0
cntTrue = 0
for filename in pathDir:
    fileIdx = filename.split('.')
    fileIdx = int(fileIdx[0])
    #print fileIdx
    filepath = os.path.join('%s%s' % (dirpath, filename))
    PoiDataPerUser, Lengths = PT.ReadPoiData(fileIdx)

    if(len(Lengths)>=2):
        lenTestData = 0
        for i in range(len(Lengths)-1):
            lenTestData+= Lengths[i]
        result = hmmEM(PoiDataPerUser, Lengths,lenTestData)
        if(result==-1):
            continue
        elif(result == 1):
            cntUser+=1
            cntTrue+=1
        else:
            cntUser+=1
print float(cntTrue)/cntUser


# # 遍历精选用户的测试代码
# mypt = pt.poiTools()
# cntAva = 0
# filename = os.path.abspath('.') + '\\PoiPtPerUser\\candidateUsers.npy'
# userIdx = np.load(filename )
#
# for fileIdx in userIdx:
#     PoiDataPerUser, Lengths = mypt.ReadPoiData(fileIdx)
#     if(len(Lengths)>=2):    # 其实精选用户的天数都是大于等于 2 的，这个if可以去掉
#         lenTrainData = 0
#         for i in range(len(Lengths)-1):
#             lenTrainData+= Lengths[i]
#         success = hmmEM(PoiDataPerUser, Lengths,lenTrainData)
#         print success
#         print fileIdx