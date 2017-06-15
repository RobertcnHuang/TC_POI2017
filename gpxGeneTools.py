#encoding=utf-8
# 提供了生成.gpx格式文件的函数，生成的.gpx轨迹文件，主要用于在GpxTrackEditor中分析、研究轨迹
import time
import os
import latlonDistance
import numpy
from collections import namedtuple
import gpsAnalyzeTools as gat

class gpxGeneTools:
    def __init__(self,gpsFile = os.path.abspath('.')+'\data_files\sample3.txt'):
        self.gpsFile = gpsFile
        self.timeStart = int(time.mktime(time.strptime('2016-09-17 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.timeEnd = int(time.mktime(time.strptime('2016-11-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.dayIntvl = 86400   # 一天的时间
        # 定义一部分统计量，不需要可删除
        self.medianDailyPts = []    # 该列表中的每个元素，表示单个用户按天统计，45天的轨迹的gps点数的中位数
        self.countDays = []     # 统计每个用户有多少天（条）的轨迹是可用的

    # 按用户生成轨迹
    def geneByUser(self):
        pathGps = self.gpsFile
        dirTrace = os.path.abspath('.') + '\TraceByUser'  # 按用户生成轨迹
        if (not os.path.exists(dirTrace)):
            os.mkdir(dirTrace)
        f = open(pathGps, "r")
        lines = f.readlines()  # 读取全部内容
        for line in lines:
            tuples = line.split(';')
            fileName = tuples[0][0:32]
            tuples[0] = tuples[0][33:]
            filepath = open(dirTrace + '\\' + fileName + '.gpx', 'w')

            # generate gpx file
            self.gpxPrefix(filepath, fileName)
            self.gpxTrkPt(filepath, tuples)
            self.gpxSuffix(filepath)

    # 按 用户/天 生成轨迹。并添加速度、活动范围、最少gps点数等约束
    def geneByUserDay(self):
        pathGps = self.gpsFile
        dirTrace = os.path.abspath('.') + '\TraceByUserDay'  # 按 用户/日 生成轨迹
        if (not os.path.exists(dirTrace)):
            os.mkdir(dirTrace)
        f = open(pathGps, "r")  # 打开数据文件
        lines = f.readlines()  # 读取全部内容

        for i, line in enumerate(lines):
            line = line.strip('\n')  # 每行的换行符必须去掉，否则会报错
            tuples = line.split(';')
            subdir = dirTrace + '\\' + tuples[0][0:32]  # 获取用户ID
            tuples[0] = tuples[0][33:]
            # 计数: 1.当前gps点序号 2.前一天最后一个gps点序号 3.每个用户有多少天的轨迹可用
            cntTuple,cntTuplePrev,cntDays = 0,0,0
            medianPtsTmp = []  # 统计单用户每天可用轨迹的gps点数，用于最终求中位数
            gpsPt = namedtuple('gpsPt', ['t', 'j', 'w', 'POIs', 'rg'])  # 时间|经度|维度|0~n个POI|行政区域
            ptTmp = gpsPt._make(tuples[0].split('|'))  # 列表方式初始化namedtuple
            # 以日为单位，分析用户轨迹
            for t in range(self.timeStart, self.timeEnd, self.dayIntvl):
                # 计数单日gps点数量
                while t <= time.mktime(time.strptime('2016'+ptTmp.t, '%Y%m%d%H%M')) < t + self.dayIntvl:
                    cntTuple += 1
                    if cntTuple <= len(tuples) - 1:
                        ptTmp = gpsPt._make(tuples[cntTuple].split('|'))
                    else:
                        break

                if (cntTuple - cntTuplePrev >= 20):  # 如果单日轨迹点超过20个，才纳入考虑范围
                    listPerDay = tuples[cntTuplePrev:cntTuple]
                    cntTuplePrev = cntTuple
                    gpsAT = gat.GpsAnalyzeTools(listPerDay) # 实例化一个 轨迹分析 对象
                    pts = self.traceUserDay(gpsAT, t, subdir)
                    del gpsAT # 用完就删，下个循环使用时重新实例化
                    if (pts):
                        medianPtsTmp.append(pts)
                        cntDays += 1
            self.countDays.append(cntDays)
            self.medianDailyPts.append(numpy.median(medianPtsTmp) if medianPtsTmp else 0)
            print i

    # 分析用户单日GPS轨迹的空间、速度等属性，如满足要求，则生成相应.gpx文件
    def traceUserDay(self,gpsAT, timeDate, subdir):
        # 空间+速度滤波
        gpsAT.filterRangeBeijing()
        if ( len(gpsAT.selectedPts) >= 15):
            gpsAT.filterSpeed()
            gpsAT.filterRangeMin()

        # 如果滤波后点数满足要求，则生成gpx文件
        if ( len(gpsAT.selectedPts) >= 10):
            if (not os.path.exists(subdir)):  # 给每一个用户建立文件夹存储45天的轨迹
                os.mkdir(subdir)
            format = '%Y-%m-%d %H:%M:%S'
            timeDate = time.localtime(timeDate) # 轨迹所对应的日期
            dt = time.strftime(format, timeDate)
            dt = dt[:10]
            filepath = open(subdir + '\\' + dt + '.gpx', 'w')
            self.gpxPrefix(filepath, dt)
            self.gpxTrkPt(filepath, gpsAT.selectedPts)
            self.gpxSuffix(filepath)
            return len(gpsAT.selectedPts)
        else:
            return 0

    # 单纯生成轨迹，不分析
    def traceUserDaySimple(self,listPerDay,timeDate,subdir):
        if (not os.path.exists(subdir)):  # 给每一个用户建立文件夹存储45天的轨迹
            os.mkdir(subdir)
        format = '%Y-%m-%d %H:%M:%S'
        timeDate = time.localtime(timeDate)  # 轨迹所对应的日期
        dt = time.strftime(format, timeDate)
        dt = dt[:10]
        filepath = open(subdir + '\\' + dt + '.gpx', 'w')
        self.gpxPrefix(filepath, dt)
        self.gpxTrkPt(filepath, listPerDay)
        self.gpxSuffix(filepath)
        return len(listPerDay),filepath

    # .gpx生成工具：生成gpx文件的前缀
    def gpxPrefix(self,filepath, fileName):
        writeList = ['<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n', \
                     '<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"  creator="Oregon 400t" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"> \n']
        writeList.append('\t<metadata>\n')
        myTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        writeList.append('\t\t<time> ' + myTime + ' </time>\n')
        writeList.append('\t\t<editor> Huang Xingyu </editor>\n')
        writeList.append('\t</metadata>\n\n')
        writeList.append('\t<trk> \n' + '\t\t<name> ' + fileName + ' </name>\n' + '\t\t<trkseg>\n')
        filepath.writelines(writeList)
        filepath.flush()

    # .gpx生成工具：将一段轨迹点写入gpx文件
    def gpxTrkPt(self,filepath, tuples):
        for mytuple in tuples:
            gpsPt = namedtuple('gpsPt',['t','j','w','POIs','rg']) # 时间|经度|维度|0~n个POI|行政区域
            ptTmp = gpsPt._make(mytuple.split('|'))     # 列表方式初始化namedtuple
            timeFormat = '2016-' + ptTmp.t[0:2] + '-' + ptTmp.t[2:4] + 'T' + ptTmp.t[4:6] + ':' \
                         + ptTmp.t[6:8] + ':' + '00Z'
            writeList = ['\t\t\t<trkpt lat = "' + ptTmp.w + '" lon = "' + ptTmp.j + '">\n' \
                         + '\t\t\t\t <ele>0.0</ele>\n' + '\t\t\t\t <time>' \
                         + timeFormat + '</time>\n' \
                         + '\t\t\t </trkpt>\n']
            filepath.writelines(writeList)
            filepath.flush()

    # .gpx生成工具：添加文件后缀，并关闭文件
    def gpxSuffix(self,filepath):
        lineTmp = '\t\t</trkseg>\n\t</trk>\n</gpx>'
        filepath.writelines(lineTmp)
        filepath.close()
    # .gpx生成工具结束