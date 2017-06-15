#encoding=utf-8
# 20170614 hxy
# 输入：两个点的经纬度坐标（第一点为向量起点，第二点为终点）
# 输出：两点确定的线段与“北”方向的夹角[-180,180]，一二象限为正，三四象限为负

import math
import latlonDistance as dist

def calcAngle(cd1,cd2):
    distHypo = dist.distance(cd1,cd2)
    distShort = dist.distance(cd1,[cd2[0],cd1[1]])
    if(not distHypo == 0):
        angle = math.acos(distShort/distHypo) * 180 / math.pi
    else:
        angle = 0

    if(cd1[0] < cd2[0] and cd1[1]<=cd2[1]): # 第一象限
        angleNorm = angle
    elif(cd1[0]>=cd2[0] and cd1[1]<cd2[1]): # 第四象限
        angleNorm = angle - 90
    elif(cd1[0]>cd2[0] and cd1[1]>=cd2[1]): # 第三象限
        angleNorm = -angle - 90
    else:
        angleNorm = angle + 90  # 第二象限

    return angleNorm