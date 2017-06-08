#encoding=utf-8
import os
# 该文件中的类，用于读取存储静态数据的文本文件，并生成相应的字典（表）

# 用三级嵌套字典生成的区域编号字典；输入编号可获取区域名称
class regionCodeDict:
    def __init__(self):
        self.dict_1st = {}  # 省、市、区的三级嵌套字典

    def regionCodeGene(self):
        codeFile = os.path.abspath('.') + '\data_files\\region_code.conf'
        f = open(codeFile, "r")
        lines = f.readlines()  # 读取全部内容

        for i,line in enumerate(lines):
            line = line.decode('gbk').strip('\n')
            linelist = line.split('\t')
            key_1st = linelist[3][0:2]  # 前两位，省区编号
            self.geneDictHigh(self.dict_1st,key_1st,linelist[0])    # 构造第一级key - value对
            if(key_1st == '11' or key_1st == '12' or key_1st == '31' or key_1st == '50' \
                       or key_1st == '81' or key_1st == '82'): # 直辖市和特别行政区是特例
                key_2nd = linelist[5][3:]
                self.geneDictLow(self.dict_1st[key_1st],key_2nd,linelist[2])    # 直辖市、特别行政区直接构造底层 key - value对
            else:
                key_2nd = linelist[4][2:4]  # 中间两位，市级编号
                key_3rd = linelist[5][4:]   # 最后两位，区级编号
                self.geneDictHigh(self.dict_1st[key_1st], key_2nd, linelist[1]) # 非直辖市...需要构造地级市一层的key-value对
                self.geneDictLow(self.dict_1st[key_1st][key_2nd],key_3rd,linelist[2])

        print 'Region Dict Done'
        return self.dict_1st

    def geneDictHigh(self, dict, key, value):
        if (not key in dict.keys()):
            dict[key] = {}
            dict[key+'x'] = value

    def geneDictLow(self, dict, key, value):
        if (not key in dict.keys()):
            dict[key] = value

    def getCate(self,dict,key,value): # 输入编号，获取区域名称。至多三次递归
        keyTmp = key[0:2]
        if(keyTmp+'x' in dict.keys()):
            value = dict[keyTmp + 'x']
        else:
            print 'Error: No such region!'
            return ''

        if(keyTmp == '11' or keyTmp == '12' or keyTmp == '31' or keyTmp == '50' \
                       or keyTmp == '81' or keyTmp == '82'):
            value_tmp = self.getCateSp(dict[keyTmp],key[3:],value)
        else:
            value_tmp = self.getCateNorm(dict[keyTmp],key[2:],value)
        if (value != value_tmp):  # 如果更底层的字典能找到相应的key-value，那么将底层于上层的value连接
            value = value + ':' + value_tmp

        return value

    def getCateSp(self,dict,key,value): # 直辖市、特别行政区
        if (key in dict.keys()):
            value = dict[key]
        return value

    def getCateNorm(self,dict,key,value):   # 一般省份。至多递归2次
        keyTmp = key[0:2]

        if (keyTmp in dict.keys() and len(key) > 2):
            value = dict[keyTmp + 'x']  # 如果还没到第三级，先把该级的POI大类赋给value
            key = key[2:]
            value_tmp = self.getCate(dict[keyTmp], key, value)
            if (value != value_tmp):  # 如果更底层的字典能找到相应的key-value，那么将底层于上层的value连接
                value = value + ':' + value_tmp
        elif (keyTmp in dict.keys()):
            value = dict[keyTmp]

        return value
''' console command, for debug
import DictGeneTools
region = DictGeneTools.regionCodeDict()
dictRegion = region.regionCodeGene()
str = region.getCate(dictRegion,'110106','')
print str
'''

# 直接用哈希表简单粗暴生成POI字典
class poiDict:
    def __init__(self):
        self.dictPoi = {} # poi 字典

    def poiDictGene(self):
        codeFile = os.path.abspath('.') + '\data_files\\poiMap.txt'
        f = open(codeFile, "r")
        lines = f.readlines()  #

        for i,line in enumerate(lines):
            try:
                line = line.decode('gbk').strip('\n')   # 有些中文字符decode时可能报错
            except:
                print line # for debug
            linelist = line.split('\t')
            # key = poi ID, value = 区域编号，POI类别，POI名称
            self.dictPoi[linelist[0]]= linelist[1:] # poi编号规则未知，直接用哈希表
            if(i%100000 == 0):
                print i

        print 'Poi dict Done'
        return self.dictPoi

# 用三级嵌套字典生成的POI类别字典；输入POI编号可读取相应类别
class poiCateDict:
    def __init__(self):
        self.dictPoiCate = {}

    def poiCateGene(self):
        codeFile = os.path.abspath('.') + '\data_files\\poiCategories.txt'
        f = open(codeFile, "r")
        lines = f.readlines()  #

        for i,line in enumerate(lines[1:]):
            line = line.decode('gbk').strip('\n').strip('\t')
            linelist = line.split('\t')
            key_1st = linelist[0][0:2]  # 前两位，一级类别

            if(len(linelist) == 6):
                self.geneDictHigh(self.dictPoiCate, key_1st, linelist[1])  # 构造第一级key - value对
                key_2nd = linelist[2][2:4]
                value_2nd = linelist[3].split(':')[1]
                self.geneDictHigh(self.dictPoiCate[key_1st], key_2nd, value_2nd)  #
                key_3rd = linelist[4][4:]
                value_3rd = linelist[5].split(':')[2]
                self.geneDictLow(self.dictPoiCate[key_1st][key_2nd],key_3rd,value_3rd)  #
            elif(len(linelist) == 4):
                self.geneDictHigh(self.dictPoiCate, key_1st, linelist[1])  # 构造第一级key - value对
                key_2nd = linelist[2][2:4]
                value_2nd = linelist[3].split(':')[1]
                self.geneDictHigh(self.dictPoiCate[key_1st], key_2nd, value_2nd)  #
            elif(len(linelist) == 2):
                self.geneDictHigh(self.dictPoiCate,key_1st,linelist[1])    # 构造第一级key - value对

        print 'PoiCate Dict Done'
        return self.dictPoiCate

    def geneDictHigh(self, dict, key, value):
        if (not key in dict.keys()):
            dict[key] = {}
            dict[key+'x'] = value

    def geneDictLow(self, dict, key, value):
        if (not key in dict.keys()):
            dict[key] = value

    def getCate(self,dict,key,value): # 输入编号，获取POI类别名称。至多3次递归
        keyTmp = key[0:2]

        if(keyTmp in dict.keys() and len(key)>2):
            value = dict[keyTmp + 'x']  # 如果还没到第三级，先把该级的POI大类赋给value
            key = key[2:]
            value_tmp = self.getCate(dict[keyTmp],key,value)
            if(value != value_tmp): # 如果更底层的字典能找到相应的key-value，那么将底层于上层的value连接
                value = value + ':' + value_tmp
        elif(keyTmp in dict.keys()):
            value = dict[keyTmp]

        return value

''' console commands, for debug
import DictGeneTools
cate = DictGeneTools.poiCateDict()
dictCate = cate.poiCateGene()
str = cate.getCate(dictCate,'270000','')
print str
str = cate.getCate(dictCate,'271200','')
print str
str = cate.getCate(dictCate,'271299','')
print str
'''