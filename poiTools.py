#encoding=utf-8
'''
This is the POIs Tools, Including 
POIs reading and saving and preprocessing part
Creat Date: 2017/06/21
@arthor: Xingxin Liu
'''
# print (__doc__)
import numpy as np
import os
from itertools import chain

'''
2个问题：
1.数据集本身问题
2.滤波算法问题
'''

class poiTools:
    def __init__(self):
        self.UserAllData = []
        # self.username = userNumber


    def ReadPoiData(self,userNumber):
        # AllUserAllDay = []
        Lengths = []
        userPoiPtsPath = os.path.abspath('.') + '\PoiPtPerUser' + '\\' + str(userNumber) + '.npy'
        if (not os.path.exists(userPoiPtsPath)):
            print "Error: User is not existent!"

        else:
            userPoiPtData = np.load(userPoiPtsPath)
            # print userPoiPtData
            for i in range(0,len(userPoiPtData)):
                Lengths.append(len(userPoiPtData[i]))
            # print userPoiPtData
            # print len(userPoiPtData)
            userdata = list(chain(*userPoiPtData))
            PoiDataPerUser = []

            for data in userdata:
                tuples = data.split('|')
                # print int(tuples[3].split(',')[0])

                PoiDataPerUser.append([int(tuples[3].split(',')[0])])

            # print "User Number:", userNumber, "  PoiCate Number:", len(PoiDataPerUser), \
            #     '  Different PoiCate Number:', len(set(PoiDataPerUser))

            print Lengths
            print PoiDataPerUser

        return  PoiDataPerUser, Lengths


    def savePoiPtPerUser(self, clstListList, userNumber):
        UserPoiPts = os.path.abspath('.') + '\PoiPtPerUser' + '\\' + str(userNumber)
        if (not os.path.exists(UserPoiPts)):
            os.mkdir(UserPoiPts)

        # 每个用户文件的路径名称
        userfilepath = UserPoiPts + '\\'  + '.npy'
        np.save(userfilepath, clstListList)
        return "Save ok!"


    def readPoiPtPerUser(self, userNumber, filename = os.path.abspath('.') + '\PoiPtPerUser'):
        # userNumber 表示用户编号，即1,2,3,4,5....
        userfilepath = filename + '\\' +  str(userNumber) + '.npy'
        UserPoiPts = np.load(userfilepath)
        return  UserPoiPts

    #added by Huang X.Y.
    # 输入：gps点的list
    # 输出：gps点的list，poi编号替换为了poi类别编号
    def poi2cate(self, listDay, dictPoi):
        listNew = []
        for i, pt in enumerate(listDay):
            pt = pt.split('|')
            pois = pt[3].split(',')
            if (len(pois[0]) > 1):
                for j, poi in enumerate(pois):
                    poi = dictPoi.getPoi(poi)
                    pois[j] = poi[1]
                if (len(pois) > 1):
                    pt[3] = ','.join(p for p in pois)
                else:
                    pt[3] = pois[0]
            pt = '|'.join(ele for ele in pt)
            listNew.append(pt)
        return listNew

    # added by Huang X.Y.
    # 输入：poi类别编号的list
    # 输出：重新分类后的poi类别编号的list
    def poi2newCate(self,listPoi, dictReclass):
        listReclass = []
        for poi in listPoi:
            newcate = dictReclass.getIdx(poi)
            if (newcate >= 0):
                listReclass.append(newcate)
        return listReclass

# myhmm = poiTools()
# myhmm.ReadPoiData(602)
