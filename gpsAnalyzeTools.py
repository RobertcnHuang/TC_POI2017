#encoding=utf-8
# 提供分析gps轨迹的各类函数
# filterRangeBeijing() 去除不在北京六环范围内的点
# filterRangeMin() 判断轨迹的跨度是否足够大，如果跨度太小，则抛弃轨迹（返回一个空list）
# filterSpeed() 去除速度不满足要求的点
import time
import os
import latlonDistance
import numpy
from collections import namedtuple

class gpsAnalyzeTools:
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

    #  如果轨迹跨越的范围不够大，则抛弃轨迹
    def filterRangeMin(self,kmRange = 2):
        if (  latlonDistance.distance([max(self.selectedLon), max(self.selectedLat)], [min(self.selectedLon), min(self.selectedLat)]) < kmRange ):
            self.selectedPts = []

    # 速度滤波的增强版，满足速度要求之外(120km/h)，需要满足每次两个移动点之间大于20米
    # 事实上，120km 的阈值可能偏高，不过可以为定位偏差留一些裕量出来
    def filterSpeed(self,speedMax = 120,distMin = 0.02):
        #speedMax = 150
        self.marks.append(0)    # 起始点总是要取到的
        ptPre = [self.selectedLat[0],self.selectedLon[0],self.selectedTime[0]]
        for i, lat in enumerate(self.selectedLat[1:]):
            dist = latlonDistance.distance([ptPre[0],ptPre[1]],[self.selectedLon[i],self.selectedLat[i]])
            # TODO 准确考虑同一分钟内的gps点。现在暂且将时间间隔设为60s
            t = ( self.selectedTime[i] - ptPre[2] )/3600 if self.selectedTime[i] - ptPre[2] > 0 else 60
            if (dist > distMin and dist/t <= speedMax):
                ptPre = [self.selectedLat[i],self.selectedLon[i],self.selectedTime[i]]
                self.marks.append(i)
        self.selectedPts = [self.selectedPts[i] for i in self.marks]
        self.selectedLat = [self.selectedLat[i] for i in self.marks]
        self.selectedLon = [self.selectedLon[i] for i in self.marks]
        self.marks = [] # 清零marks供下次使用
