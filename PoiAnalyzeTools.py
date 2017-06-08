#encoding=utf-8
from collections import namedtuple
import DictGeneTools as dgt

class PoiAnalyzeTools:
    def __init__(self,dictTool):
        #self.listDay = listDay
        #self.poiCD = dgt.poiCateDict()
        self.dictTool = dictTool
        self.gpsPt = namedtuple('gpsPt', ['t', 'j', 'w', 'POIs', 'rg'])  # 时间|经度|维度|0~n个POI|行政区域

    def poi2cate(self,listDay):
        listNew = []
        #dictCate = self.poiCD.poiCateGene()
        for i, pt in enumerate(listDay):
            #pt = self.gpsPt._make(pt.split('|'))  # 列表方式初始化namedtuple
            pt = pt.split('|')
            pois = pt[3].split(',')
            if( len(pois[0]) > 1 ):
                for j,poi in enumerate(pois):
                    poi = self.dictTool.getPoi(poi)
                    #poi = poi.split('\t')[1]
                    #poi = self.poiCD.getCate(dictCate,poi[1],'')
                    pois[j] = poi[1]
                if( len(pois)>1 ):
                    pt[3] = ','.join(p for p in pois)
                else:
                    pt[3] = pois[0]
            pt = '|'.join(ele for ele in pt)
            listNew.append(pt)
        return listNew

