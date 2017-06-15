#encoding=utf-8
# 20170614
# @author: hxy
# 用于保存每个聚合点（团簇）的信息
import time

class clusterStruct:

    def __init__(self,ptList):
        self.IsCluster = 1 if len(ptList)>1 else 0  # 指示该簇是密度聚类产生的真团簇，还是伪团簇（噪声点）
        self.ptAll = ptList     # 记录簇中的所有点
        self.center = self.setCenter()  # 簇的几何中心坐标 [lon,lat]
        self.ptWithPoi = self.findPoi() # 记录该簇中，含有POI的点的时间、坐标、POI编号，便于后续单独分析POI序列的跳转
        self.HasPoi = 1 if len(self.ptWithPoi) > 0 else 0  # 指示该聚合点中的gps点是否含有POI信息
        self.timeHead = self.getUnixTime(self.ptAll[0])     # 簇中第一个点的采样时间
        self.timeTail = self.getUnixTime(self.ptAll[-1])    # 最后一个点的采样时间
        print self.HasPoi

    # 判断该聚合点是真团簇（点数大于等于DBSCAN的min_Point），还是伪团簇（噪声点）
    def isCluster(self):
        return self.IsCluster

    # 判断该聚合点是否包含任意POI信息
    def hasPoi(self):
        return self.HasPoi

    # 用于初始化，返回计算并返回团簇几何中心经纬度坐标 [lon,lat]
    def setCenter(self):
        lon = 0
        lat = 0
        for pt in self.ptAll:
            pt = pt.split('|')
            lon += float(pt[1])
            lat += float(pt[2])
        lon /= len(self.ptAll)
        lat /= len(self.ptAll)
        self.center = [lon, lat]
        return self.center

    # 获取团簇的中心点坐标
    def getCenter(self):
        return self.center

    # 用于初始化，返回以秒计的Unix时间
    def getUnixTime(self,pt):
        pt = pt.split('|')
        return time.mktime(time.strptime('2016'+pt[0], '%Y%m%d%H%M'))

    # 用于初始化，找到gps序列中，附着有Poi信息的点
    def findPoi(self):
        ptListTmp = []
        for pt in self.ptAll:
            ptTuple = pt.split('|')
            if( len(ptTuple[3])>1 ):
                ptListTmp.append(pt)
        return ptListTmp