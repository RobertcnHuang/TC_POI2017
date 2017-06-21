#encoding=utf-8
# Part1. 读取txt格式的原始数据，将其切分成以 用户/日 为单位的一段段数据
# Part2. 对每段 用户/日 的数据，先根据点数规模、速度、覆盖范围等进行筛选预处理
# Part3. 核心部分，进行空间、序列聚类，并做角度滤波，最终输出一个聚合点（团簇）的list
from dbscan_master.dbscan import dbscan
import time
import os
import numpy as np
import subprocess
import matplotlib.cm as cm
from PIL import Image
from collections import Counter
import matplotlib.pyplot as plt
from pylab import *
import gpsAnalyzeTools as gat
import gpxGeneTools as ggt
import pointsMap as PM
import calcAngle as CA
import clusterStruct as clst
import dictGeneTools as dgt
import poi2cate as p2c

class pointCluster:
    def __init__(self, gpsFile=os.path.abspath('.') + '\data_files\sample3.txt'):
        self.gpsFile = gpsFile
        self.timeStart = int(time.mktime(time.strptime('2016-09-17 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.timeEnd = int(time.mktime(time.strptime('2016-11-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.dayIntvl = 86400  # 一天的时间
        self.dictPoi = dgt.poiDict()

    # 主程序
    def main(self):
        # Part1. 读取文件
        pathGps = self.gpsFile
        f = open(pathGps, "r")  # 打开数据文件
        lines = f.readlines()  # 读取全部内容
        dirTrace = os.path.abspath('.') + '\TraceByUserDay'  # 按 用户/日 生成轨迹
        if (not os.path.exists(dirTrace)):
            os.mkdir(dirTrace)
        gpxGT = ggt.gpxGeneTools()
        allUserPoiPt = [] # 记录全部用户的全部poi点，每一个用户的poi点是一个list

        for i, line in enumerate(lines):
            line = line.strip('\n')  # 每行的换行符必须去掉，否则会报错
            gpsPtsPerUser = line.split(';')
            userID = gpsPtsPerUser[0][0:32]
            gpsPtsPerUser[0] = gpsPtsPerUser[0][33:]
            ptTmp = gpsPtsPerUser[0].split('|')
            cntTuple, cntTuplePrev = 0, 0  # 计数: 1.当前gps点序号 2.前一天最后一个gps点序号
            userPoiAll = [] # 双层list，里层的是用户单日的poi list

            for t in range(self.timeStart, self.timeEnd, self.dayIntvl):
                # Part1. 切分为 用户/日, 并计数单日gps点数量
                while t <= time.mktime(time.strptime('2016'+ptTmp[0], '%Y%m%d%H%M')) < t + self.dayIntvl:
                    cntTuple += 1
                    if cntTuple <= len(gpsPtsPerUser) - 1:
                        ptTmp = gpsPtsPerUser[cntTuple].split('|')
                    else:
                        break

                # Part2. 根据点数规模、速度、覆盖范围等因素，对单日轨迹进行筛选预处理
                if (cntTuple - cntTuplePrev >= 15):  # 如果单日轨迹点超过20个，才纳入考虑范围
                    listPerDay = gpsPtsPerUser[cntTuplePrev:cntTuple]
                    #cntTuplePrev = cntTuple
                    gpsAT = gat.gpsAnalyzeTools(listPerDay) # 实例化一个 轨迹分析 对象
                    gpsAT.filterRangeBeijing()
                    if (len(gpsAT.selectedPts) >= 5): # 15
                        gpsAT.filterSpeed(120,200)
                        gpsAT.filterRangeMin()

                    # Part3. 核心部分：空间、序列聚类，及角度滤波
                    if ( len(gpsAT.selectedPts) >= 5): # 只关注点数足够的轨迹 10
                        #self.showTrack(dirTrace, userID, gpxGT, gpsAT.selectedPts, t)
                        resultCluster = self.spatialCluster(gpsAT.selectedLon,gpsAT.selectedLat)
                        clstList = self.seqtialCluster(gpsAT.selectedPts,resultCluster)
                        clstListOut = self.angleFilter(clstList)

                        # # 输出聚类后的轨迹.gpx
                        # gpsList = []
                        # for clst in clstListOut:
                        #     gpsTmp = clst.ptAll[0][0:8]+'|'+ str(clst.center[0]) + '|' + str(clst.center[1]) +'||'
                        #     gpsList.append(gpsTmp)
                        #self.showTrack(dirTrace, userID+'CLST', gpxGT, gpsList, t)

                        # 这个循环输出的clstListOut 为前级输出，在此添加HMM等后续的代码
                        for clst in clstListOut:
                            clst.ptAll = p2c.poi2cate(clst.ptAll,self.dictPoi)
                            if( clst.hasPoi() ):
                                clst.ptWithPoi = p2c.poi2cate(clst.ptWithPoi, self.dictPoi)

                        # 记录用户单日产生的poi，存在一个list中
                        ptWithPoiDay = self.extractPoiPt(clstListOut)
                        if(len(ptWithPoiDay)>0):
                            userPoiAll.append(self.extractPoiPt(clstListOut))

                    del gpsAT  # 用完就删，下个循环使用时重新实例化

                cntTuplePrev = cntTuple
            # # 将每个用户的poi点存入文件
            # if( len(userPoiAll) > 0):
            #     self.savePoiPtPerUser(userPoiAll, i)

            allUserPoiPt.append(userPoiAll)

        # print

        print len(allUserPoiPt)
        print("all done")
        return allUserPoiPt

    # 空间聚类（DBSCAN）
    # 输入：轨迹点的经纬度坐标，（DBSCAN的参数）
    # 输出：对轨迹点的密度聚类结果 & 聚类结果可视化
    def spatialCluster(self,lonList,latList,min_points = 2, eps = 0.0018):
        matLonLat = np.matrix([lonList, latList])
        resultCluster = dbscan(matLonLat, eps, min_points)
        # # 聚类结果可视化，可注释掉
        #PM.points_map(np.transpose(matLonLat), resultCluster)
        return resultCluster

    # 序列聚类（将空间聚类的结果结合时序信息，对空间聚类做拆分）
    # 输入：gps序列, 序列中每个点的聚类标签
    # 输出：一个cluster的list，每个cluster代表一个聚合点。cluster的细节详见其py文件
    def seqtialCluster(self,ptList,resultCluster):
        clstList = []
        prevClst = resultCluster[0]
        prevIdx = 0
        for i,curClst in enumerate(resultCluster):
            if(i):
                if(prevClst != curClst or curClst == 0 or i == len(resultCluster)-1):
                    newClst = clst.clusterStruct(ptList[prevIdx:i])
                    clstList.append(newClst)
                    del newClst
                    prevClst = curClst
                    prevIdx = i
        return clstList

    # 根据轨迹段落之间的夹角，滤除没有关联POI的折返点
    # 输入：前级产生的聚合点序列
    # 输出：经过角度滤波后的聚合点序列
    def angleFilter(self,clstList,angleTh = 150):
        markList = [1]*len(clstList)
        angle1st = 0
        angle2nd = 0
        for i,curClst in enumerate(clstList):
            if(i==0):
                prevClst = curClst
            elif(i==1):
                angle2nd = CA.calcAngle( clstList[i-1].getCenter(),clstList[i].getCenter() )
            else:
                angle1st = angle2nd
                angle2nd = CA.calcAngle( clstList[i-1].getCenter(),clstList[i].getCenter() )
                angleInclude = abs(angle1st - angle2nd)
                angleInclude = angleInclude if angleInclude <= 180 else 360 -angleInclude
                # 这三行代码是核心逻辑。对于线段AB,BC，如果折返角 <AB,BC> 过大，且中间点B没有关联POI，那么删除中间点B
                if(angleInclude > angleTh):
                    if(not clstList[i-1].hasPoi()):
                        markList[i-1] = 0
        filteredList = []
        for i,clst in enumerate(clstList):
            if(markList[i]):
                filteredList.append(clstList[i])

        return filteredList

    # 从一个团簇中提取含有poi的gps点: 输入一个cluster的list，输出一个含有poi的gps点的list
    def extractPoiPt(self,clstList):
        poiList = []
        for clst in clstList:
            if(clst.hasPoi()):
                poiList.extend(clst.ptWithPoi)
        return poiList

    # 将gps轨迹保存至subdir，并调用gpstrackEditor.exe显示轨迹，主要用于聚类代码的调试
    def showTrack(self,dir,userID,gpxGT,ptList,time):
        subdir = dir + '\\' + userID
        l,filepath = gpxGT.traceUserDaySimple(ptList,time,subdir)
        procOpen = '\"' + 'C:\Program Files (x86)\GPS Track Editor\GpsTrackEditor.exe' + '\" ' + filepath.name
        subprocess.Popen(procOpen)    # 调用外部可视化软件，将上方路径替换为本地安装GpsTrackEditor的路径即可

    def savePoiPtPerUser(self, clstListList, userNumber):
        UserPoiPts = os.path.abspath('.') + '\PoiPtPerUser'
        if (not os.path.exists(UserPoiPts)):
            os.mkdir(UserPoiPts)
        # 每个用户文件的路径名称
        userfilepath = UserPoiPts + '\\' + str(userNumber) + '.npy'
        np.save(userfilepath, clstListList)
        return "Save ok!"

    def readPoiPtPerUser(self, userNumber, filename=os.path.abspath('.') + '\PoiPtPerUser'):
        # userNumber 表示用户编号，即1,2,3,4,5....
        userfilepath = filename + '\\' + str(userNumber) + '.npy'
        UserPoiPts = np.load(userfilepath)
        return UserPoiPts

# console
# import pointCluster
# PC = pointCluster.pointCluster()
# allUserPoiPts = PC.main()

pc = pointCluster()
allUserPoiPts = pc.main()

# haspoi = 0
# cntpoi = 0
# for user in allUserPoiPts:
#     if (len(user) > 0):
#         haspoi += 1
#         for day in user:
#             cntpoi+=len(day)
#
# print 'total poi = ' + str(cntpoi)
# print 'user with poi = ' + str(haspoi)
#
# lenDay = []
# for user in allUserPoiPts:
#     if(len(user)):
#         lenDay.append(len(user))
# print max(lenDay)