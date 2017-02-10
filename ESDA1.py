# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 11:19:19 2017
    淡水魚特有入侵種ESDA

@author: user
"""
import pandas as pd
import pysal as ps
import matplotlib.path as mplPath
import numpy as np
import folium
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time

DATA = pd.read_excel('2017-02-08_re_out_ALLGPS_mod.xlsx')

### Remove wierd names (sea water fishes??)
Name = pd.read_excel('FreshWaterFishNames.xlsx')
N = Name.iloc[:,0].tolist()
BOOL = [i in N for i in DATA.Scientific_name]
DATA = DATA[BOOL]

#Wait until I get the polygons:
Polygons = ps.open('淡水魚分佈區\\CatchmentArea6_WGS84.shp').read() #read shp to get vertices of each polygon

Polygons[0].vertices
Polygons[0].centroid


#ATT = ps.open() # read dbf to get attribute table in order to pick up the proper polygon
#print(ATT.header)
#ATT1 = ATT.by_col('')

# Write the costomized functions##

def PIPC(LAT,LON,polygon):
    '''
    Check whether a vector of points(Lat,Lon) is inside a polygon
    Return a vector of BOOL
    '''
    crd = np.array(polygon)# poly
    bbPath = mplPath.Path(crd)
    pnts = [[i,j] for i,j in zip(LON,LAT)] # points
    r = 0.001 # accuracy
    isIn = [ bbPath.contains_point(pnt,radius=r) or bbPath.contains_point(pnt,radius=-r) for pnt in pnts]
    return isIn

def TEC(polygon,fishname='Acrossocheilus paradoxus',after=2010,before=2020):
    '''
    Total effort calculator & fish appearance calculator
    '''
    BOOL = np.array(DATA.Year<=before) & np.array(DATA.Year>=after)
    TMP = DATA[BOOL]
    
    TMP3 = TMP.drop_duplicates(subset=['Latitude','Longitude','Year','Month','Source'],keep='first')
    TE = sum(PIPC(TMP3.Latitude,TMP3.Longitude,polygon))
    # Calculate fish appearance
    TMP4 = TMP[TMP.Scientific_name==fishname]
    FA = sum(PIPC(TMP4.Latitude,TMP4.Longitude,polygon))
    return (FA,TE)
    
def FMAP(fishname='Acrossocheilus paradoxus',after=2010,before=2020,PNG = False):
    '''
    Show the points on map given species name and range of year
    '''
    DC1 = DATA[DATA.Scientific_name==fishname]

    BOOL = [(DC1.Year<=before).tolist()[i] and (DC1.Year>=after).tolist()[i] for i in range(len(DC1))]
    DC1_1 = DC1[BOOL]

    map_object = folium.Map(location=[24, 121], zoom_start=8, tiles="Stamen Terrain")
    for i in range(len(DC1_1)):
        marker = folium.features.Marker([DC1_1.Latitude.iloc[i], DC1_1.Longitude.iloc[i]], popup=str(DC1_1.Year.iloc[i])[:-2]+' '+DC1_1.Source.iloc[i]+' '+str(DC1_1.Latitude.iloc[i])+' '+str(DC1_1.Longitude.iloc[i]))
        map_object.add_children(marker)
    if not os.path.exists(fishname):
        os.makedirs(fishname)
    if PNG == True:
        folium.Map.save(map_object, "TEMP.html")
        fn="TEMP.html"
        tmpurl='file:///{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)                
        binary = FirefoxBinary('C://Program Files (x86)//Mozilla Firefox//firefox.exe')
        browser = webdriver.Firefox(firefox_binary=binary)
        
        browser.get(tmpurl)
        time.sleep(8)
        browser.save_screenshot(fishname+"/"+str(after)+"_"+str(before)+"_"+str(datetime.now())[0:10]+".png")
        browser.quit()
    else:        
        folium.Map.save(map_object, fishname+"/"+str(after)+"_"+str(before)+"_"+str(datetime.now())[0:10]+".html")

## CASE 1 Acrossocheilus paradoxus 台灣石賓
## 西部特有種入侵東部，如今已是全台廣泛分布
#FMAP('Acrossocheilus paradoxus',before=2020,after=2010,PNG=True)

## 努力量問題必須校正，早期東部沒有分布點位可能是當時的調查完全集中在西部，
## 這個可能性一定要釐清

#test1 = TEC(Polygons[0].vertices)
#print(test1)
def OUTTABLE(fishname='Acrossocheilus paradoxus',output=False):
    O = []
    for i,j in enumerate(['I','II','III','IV','V']):
        K = []
        K1 = []
        for Y in [[1800,1989],[1990,1995],[1996,2000],[2001,2002],[2003,2004],[2005,2006],[2007,2008],[2009,2010],[2011,2012],[2013,2020]]:
            TTT = TEC(Polygons[i].vertices,fishname=fishname,after = Y[0],before = Y[1])
            K.append(TTT[0])
            K1.append(TTT[1])
        O.append(pd.Series(K,name='R_'+j+'_FA'))
        O.append(pd.Series(K1,name='R_'+j+'_TE'))
    
    OUT = pd.DataFrame(O)
    OUT.columns = ['1800~1989','1990~1995','1996~2000','2001~2002','2003~2004','2005~2006','2007~2008','2009~2010','2011~2012','2013~']
    if output == True:        
        OUT.to_excel(str(datetime.now())[0:10]+'_'+fishname+'_Otable.xlsx')    
    
    return OUT    
    


#OUTTABLE('Acrossocheilus paradoxus')
#OUTTABLE('Spinibarbus hollandi')
#OUTTABLE('Opsariichthys pachycephalus')
#OUTTABLE('Rhinogobius candidianus')   
'''
FMAP('Spinibarbus hollandi',before=2020,after=2010,PNG=True)
FMAP('Spinibarbus hollandi',before=2009,after=2007,PNG=True)
FMAP('Spinibarbus hollandi',before=2006,after=2004,PNG=True)
FMAP('Spinibarbus hollandi',before=2003,after=2001,PNG=True)
FMAP('Spinibarbus hollandi',before=2000,after=1998,PNG=True)
FMAP('Spinibarbus hollandi',before=1997,after=1950,PNG=True)
'''

##Opsariichthys pachycephalus 粗首鱲 入侵東部##
'''
FMAP('Opsariichthys pachycephalus',before=2020,after=2010,PNG=True)
FMAP('Opsariichthys pachycephalus',before=2009,after=2007,PNG=True)
FMAP('Opsariichthys pachycephalus',before=2006,after=2004,PNG=True)
FMAP('Opsariichthys pachycephalus',before=2003,after=2001,PNG=True)
FMAP('Opsariichthys pachycephalus',before=2000,after=1998,PNG=True)
FMAP('Opsariichthys pachycephalus',before=1997,after=1950,PNG=True)
'''
##Rhinogobius candidianus 明潭吻鰕虎??##

#FMAP('Rhinogobius candidianus',before=2020,after=2010,PNG=True)
#FMAP('Rhinogobius candidianus',before=2009,after=2007,PNG=True)
#FMAP('Rhinogobius candidianus',before=2006,after=2004,PNG=True)
#FMAP('Rhinogobius candidianus',before=2003,after=2001,PNG=True)
#FMAP('Rhinogobius candidianus',before=2000,after=1998,PNG=True)
#FMAP('Rhinogobius candidianus',before=1997,after=1950,PNG=True)