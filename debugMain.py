#encoding=utf-8
<<<<<<< HEAD:debugMain.py
# debug用的，没啥用了
import time
import os
import latlonDistance
import numpy as np
from collections import namedtuple
import gpsAnalyzeTools as gat
import dictGeneTools as dgt
import poi2cate as pat

class poiMatchingMain:
    def __init__(self,gpsFile = os.path.abspath('.')+'\data_files\sample3.txt'):
        self.gpsFile = gpsFile
        self.timeStart = int(time.mktime(time.strptime('2016-09-17 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.timeEnd = int(time.mktime(time.strptime('2016-11-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.dayIntvl = 86400  # 一天的时间
        self.gpsPt = namedtuple('gpsPt', ['t', 'j', 'w', 'POIs', 'rg'])  # 时间|经度|维度|0~n个POI|行政区域
        self.poiDictTool = dgt.poiDict()

    def main(self):
        pathGps = self.gpsFile
        f = open(pathGps, "r")  # 打开数据文件
        lines = f.readlines()  # 读取全部内容

        for i, line in enumerate(lines):
            line = line.strip('\n')  # 每行的换行符必须去掉，否则会报错
            tuples = line.split(';')
            userID = tuples[0][0:32]
            tuples[0] = tuples[0][33:]
            cntTuple, cntTuplePrev = 0, 0   # 计数: 1.当前gps点序号 2.前一天最后一个gps点序号

            ptTmp = self.gpsPt._make(tuples[0].split('|'))  # 列表方式初始化namedtuple
            # 以日为单位，分析用户轨迹
            for t in range(self.timeStart, self.timeEnd, self.dayIntvl):
                # 计数单日gps点数量
                while t <= time.mktime(time.strptime('2016'+ptTmp.t, '%Y%m%d%H%M')) < t + self.dayIntvl:
                    cntTuple += 1
                    if cntTuple <= len(tuples) - 1:
                        ptTmp = self.gpsPt._make(tuples[cntTuple].split('|'))
                    else:
                        break

                if (cntTuple - cntTuplePrev >= 20):  # 如果单日轨迹点超过20个，才纳入考虑范围
                    listPerDay = tuples[cntTuplePrev:cntTuple]
                    cntTuplePrev = cntTuple
                    gpsAT = gat.gpsAnalyzeTools(listPerDay) # 实例化一个 轨迹分析 对象
                    gpsAT.filterRangeBeijing()
                    if (len(gpsAT.selectedPts) >= 15):
                        gpsAT.filterSpeed()
                        gpsAT.filterRangeMin()

                    if ( len(gpsAT.selectedPts) >= 10): # 只关注点数足够的轨迹
                        listPerDay = pat.poi2cate(gpsAT.selectedPts,self.poiDictTool)
                        print listPerDay
                    del gpsAT  # 用完就删，下个循环使用时重新实例化
                    print listPerDay



poiMM = poiMatchingMain()
poiMM.main()
'''
# 按用户/日生成轨迹
=======
import GpxGeneTools as ggt

>>>>>>> parent of e6ec028... new edition:main.py
tool =  ggt.GpxGeneTools()
#tool.geneByUser()
tool.geneByUserDay()
print str(sum(tool.countDays)) +' available traces in total'