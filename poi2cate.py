#encoding=utf-8
# 用于将某点所关联的POI编号，转换为POI类别编号
# dictPoi: poi编号-poi详细信息 字典

def poi2cate(self,listDay,dictPoi):
    listNew = []
    for i, pt in enumerate(listDay):
        pt = pt.split('|')
        pois = pt[3].split(',')
        if( len(pois[0]) > 1 ):
            for j,poi in enumerate(pois):
                poi = dictPoi.getPoi(poi)
                pois[j] = poi[1]
            if( len(pois)>1 ):
                pt[3] = ','.join(p for p in pois)
            else:
                pt[3] = pois[0]
        pt = '|'.join(ele for ele in pt)
        listNew.append(pt)
    return listNew

