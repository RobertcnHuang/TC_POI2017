#encoding=utf-8
# 输入：两点的经纬度坐标 coordx = [lon,lat]
# 输出：两点距离 以 km 为单位
from math import sin, cos, sqrt, atan2, radians

def distance(coord1, coord2):
	R = 6373.0
	lon1 = radians(coord1[0])
	lat1 = radians(coord1[1])
	lon2 = radians(coord2[0])
	lat2 = radians(coord2[1])

	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distance = R * c
	return distance

'''
firstCoord = [float(x) for x in raw_input("First Coord: ").split(',')]
secondCoord = [float(x) for x in raw_input("Second Coord: ").split(',')]
print str(distance(firstCoord, secondCoord)) + " km"
'''