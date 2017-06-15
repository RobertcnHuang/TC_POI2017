# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 20:28:18 2017
show poits on the map
cord: 需要可视化的经纬度 array
cluster： 可视化标注的标签 数字形式
@author: SHZ
@edited by Hxy on 20170613
"""

from PIL import Image
from pylab import *
import numpy as np
from collections import Counter

def points_map(cord, cluster):
    im = array(Image.open('beijingmap.png'))[:,:,:]
    figure(figsize=(8, 8))
    imshow(im)
    
    left = 115.9914730000
    top = 40.1849620000
    right = 116.7820540000
    bottom = 39.6141080000
    
    n_clusters=len(Counter(cluster))
    numColor = max(cluster) + 1
    colors = cm.rainbow(np.linspace(0, 1, numColor))

    clus_num=np.zeros(n_clusters)
    for i in range(n_clusters):
        clus_num[i]=sum(cluster==i)
    clus_sorted=np.array(sorted(zip(clus_num, range(len(cord))),reverse=True))
    
    x = (cord[:,0]-left)/(right-left)*im.shape[1]
    y = im.shape[0]-(cord[:,1]-bottom)/(top-bottom)*im.shape[0]
    

    for i in range(cord.shape[0]):
        if(cluster[i] in clus_sorted[:,1]):
            plt.text(x[i], y[i], '%i' % (cluster[i]),
             size=5, horizontalalignment='center',
             bbox=dict(alpha=.5, facecolor=colors[cluster[i]]))
                            
                            
    xlim([0,im.shape[1]])
    ylim([im.shape[0],0])

    xticks( arange(0) )
    yticks( arange(0) )

    plt.show()

if __name__ == '__main__':
#    matfn=u'cluster.mat'  
#    data=sio.loadmat(matfn)
#    cluster=data['cluster'][0]
#    cord=data['cord']
    points_map(np.array([[ 116.39101482,   39.90549862],[ 116.23757429,   39.82986086]]),np.array([0,1]))
#    points_map(cord, cluster)