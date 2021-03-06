#encoding=utf-8
# 包含3个类，用于读取存储静态数据的文本文件，并生成相应的字典（表）
# class regionCodeDict ： 生成 区域编号-XX省_XX市_XX区 的映射表
# class poiDict ：直接哈希生成 poi编号-poi详细信息 的映射表 （这个是现阶段比较多用到的）
# class poiCateDict：生成 POI类别编号-POI类别汉字名称 的映射表
import os

# 用三级嵌套字典生成的区域编号字典；输入编号可获取区域名称
class regionCodeDict:
    def __init__(self):
        self.dict_1st = {}  # 省、市、区的三级嵌套字典
        self.dict_1st = self.regionCodeGene()

    def regionCodeGene(self):
        codeFile = os.path.abspath('.') + '\data_files\\region_code.conf'
        f = open(codeFile, "r")
        lines = f.readlines()  # 读取全部内容

        for i,line in enumerate(lines):
            line = line.decode('gbk').strip('\n')
            linelist = line.split('\t')
            key_1st = linelist[3][0:2]  # 前两位，省区编号
            self.geneDictHigh(self.dict_1st,key_1st,linelist[0])    # 构造第一级key - value对
            if(key_1st == '11' or key_1st == '12' or key_1st == '31' or key_1st == '50'
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

    def getRegion(self,dict,key,value): # 输入编号，获取区域名称。至多三次递归
        keyTmp = key[0:2]
        if(keyTmp+'x' in dict.keys()):
            value = dict[keyTmp + 'x']
        else:
            print 'Error: No such region!'
            return ''

        if(keyTmp == '11' or keyTmp == '12' or keyTmp == '31' or keyTmp == '50'
                       or keyTmp == '81' or keyTmp == '82'):
            value_tmp = self.getRegionSp(dict[keyTmp],key[3:],value)
        else:
            value_tmp = self.getRegionNorm(dict[keyTmp],key[2:],value)
        if (value != value_tmp):  # 如果更底层的字典能找到相应的key-value，那么将底层于上层的value连接
            value = value + ':' + value_tmp

        return value

    def getRegionSp(self,dict,key,value): # 直辖市、特别行政区
        if (key in dict.keys()):
            value = dict[key]
        return value

    def getRegionNorm(self,dict,key,value):   # 一般省份。至多递归2次
        keyTmp = key[0:2]

        if (keyTmp in dict.keys() and len(key) > 2):
            value = dict[keyTmp + 'x']  # 如果还没到第三级，先把该级的POI大类赋给value
            key = key[2:]
            value_tmp = self.getRegion(dict[keyTmp], key, value)
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
        self.dictPoi = self.poiDictGene()

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
            # key = poi ID, value = [ 区域编号，POI类别，POI名称 ]
            self.dictPoi[linelist[0]]= linelist[1:] # poi编号规则未知，直接用哈希表
            # if(i%100000 == 0):
            #     print i

        print 'Poi dict Generated'
        return self.dictPoi

    def getPoi(self,key):
        return self.dictPoi[key]

# 用三级嵌套字典生成的POI类别字典；输入POI编号可读取相应类别
class poiCateDict:
    def __init__(self):
        self.dictPoiCate = {}
        self.dictPoiCate = self.poiCateGene()

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

    def getCate(self,dict,key,value): # 输入 [POI类别字典,poi编号，获取POI类别名称。至多3次递归
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

class reclassifyDict:
    def __init__(self):
        self.dictReclass = {}
        self.dictReclass = self.reclassDictGene()
        self.cateName = [u'住宅',u'教育',u'游览健身',u'办公',u'休闲娱乐',u'医疗',u'酒店餐饮',u'交通',u'生活服务']  # 共8类，但第一类倾向于抛弃

    def reclassDictGene(self):
        self.dictReclass['10'] = 6  # 美食
        self.dictReclass['11'] = 3  # 公司
        self.dictReclass['12'] = 3  # 机构团体
        self.dictReclass['13'] = 4  # 购物
        self.dictReclass['14'] = 8  # 生活服务  new
        self.dictReclass['16'] = 4  # 娱乐休闲
        self.dictReclass['18'] = 2  # 运动
        self.dictReclass['19'] = 8  # 汽车      new
        self.dictReclass['20'] = 5  # 医疗
        self.dictReclass['21'] = 6  # 酒店
        self.dictReclass['22'] = 2  # 景点
        self.dictReclass['23'] = 4  # 文化
        self.dictReclass['24'] = 1  # 教育学校
        self.dictReclass['25'] = 8  # 银行金融  new
        self.dictReclass['2610'] = 7  # 交通地名    new
        self.dictReclass['2611'] = 8  # 地名地址信息   new
        self.dictReclass['2612'] = 7  # 道路名
        self.dictReclass['2613'] = 2  # 地名：自然
        self.dictReclass['2614'] = 3  # 地名：行政
        self.dictReclass['2615'] = 8  # 门牌信息    new
        self.dictReclass['261600'] = 8  # 地名：热点区域  new
        self.dictReclass['261610'] = 7  # 地名：热点：交通类    new
        self.dictReclass['261611'] = 8  # 地名：热点：Poi类     new
        self.dictReclass['261612'] = 3  # 地名：热点：行政
        self.dictReclass['261613'] = 4  # 地名：热点：商圈
        self.dictReclass['261699'] = 8  # 地名：热点：其他热点区域  new
        self.dictReclass['2699'] = 8  # 地名：其他地名地址   new
        self.dictReclass['27'] = 7  # 基础设施
        self.dictReclass['2800'] = 0  # 住宅  new
        self.dictReclass['2810'] = 0    # 住宅
        self.dictReclass['281100'] = 3  # 产业园区
        self.dictReclass['281200'] = 3  # 商务楼宇
        self.dictReclass['2880'] = 0  # 房产小区附属  new
        self.dictReclass['289900'] = 0
        self.dictReclass['80'] = 8  # 室内及附属设施   new
        self.dictReclass['99'] = 8  # 其他    new
        return self.dictReclass

    # 输入：poi类别编号
    # 输出：重新分类后的POI类别编号
    def getIdx(self,key):
        value = -1
        if( self.dictReclass.has_key(key[0:2]) ):
            value = self.dictReclass[key[0:2]]
        elif( self.dictReclass.has_key(key[0:4]) ):
            value = self.dictReclass[key[0:4]]
        elif( self.dictReclass.has_key(key) ):
            value = self.dictReclass[key]
        return value

    # 输入：重新分类后的类别编号
    # 输出：类别的汉字名称
    def getName(self,key):
        return self.cateName[key]


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