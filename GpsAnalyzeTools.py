#encoding=utf-8
import time
import os
import latlonDistance
import numpy
from collections import namedtuple

class GpsAnalyzeTools:
    def __init__(self,listPerDay):
        #self.PtsDaily = listPerDay
        self.selectedLat, self.selectedLon, self.selectedTime, self.selectedPts, self.marks= [],[],[],[],[]
        self.selectedPts = listPerDay
        self.gpsPt = namedtuple('gpsPt', ['t', 'j', 'w', 'POIs', 'rg'])  # 时间|经度|维度|0~n个POI|行政区域
        for pt in listPerDay:
            pt = self.gpsPt._make(pt.split('|'))
            self.selectedLon.append(float(pt.j))
            self.selectedLat.append(float(pt.w))
            self.selectedTime.append(time.mktime(time.strptime('2016' + pt.t, '%Y%m%d%H%M')))

    # 1. 过滤超出城市范围的点，认为 39.7~40.2  116.1~116.7 是城市内的活动范围，超出此范围认为出城。
    # 2. 并过滤活动范围在 2 km 以内的轨迹(其实判断的方法并不严格)
    def filterRangeBeijing(self):
        for i,pt in enumerate(self.selectedPts):
            ptPre = pt
            pt = self.gpsPt._make(pt.split('|'))  # 列表方式初始化namedtuple
            if (116.1 < float(pt.j) < 116.7 and 39.7 < float(pt.w) < 40.2):
                self.marks.append(i)
        self.selectedPts = [self.selectedPts[i] for i in self.marks]
        self.selectedLat = [self.selectedLat[i] for i in self.marks]
        self.selectedLon = [self.selectedLon[i] for i in self.marks]
        self.marks = [] # 清零marks供下次使用

    def filterRangeMin(self):
        if (  latlonDistance.distance([max(self.selectedLat), max(self.selectedLon)], [min(self.selectedLat), min(self.selectedLon)]) < 2 ):
            self.selectedPts = []

    # 速度滤波的增强版，满足速度要求之外(150km/h)，需要满足每次两个移动点之间大于100米
    # TODO（之后可用时鸿志的聚类算法？）
    def filterSpeed(self):
        speedMax = 150
        self.marks.append(0)    # 起始点总是要取到的
        ptPre = [self.selectedLat[0],self.selectedLon[0],self.selectedTime[0]]
        for i, lat in enumerate(self.selectedLat[1:]):
            dist = latlonDistance.distance([ptPre[0],ptPre[1]],[self.selectedLat[i],self.selectedLon[i]])
            # TODO 准确考虑同一分钟内的gps点。现在暂且将时间间隔设为60s
            t = ( self.selectedTime[i] - ptPre[2] )/3600 if self.selectedTime[i] - ptPre[2] > 0 else 60
            if (dist > 0.1 and dist/t <= speedMax):
                ptPre = [self.selectedLat[i],self.selectedLon[i],self.selectedTime[i]]
                self.marks.append(i)
        self.selectedPts = [self.selectedPts[i] for i in self.marks]
        self.selectedLat = [self.selectedLat[i] for i in self.marks]
        self.selectedLon = [self.selectedLon[i] for i in self.marks]
        self.marks = [] # 清零marks供下次使用
