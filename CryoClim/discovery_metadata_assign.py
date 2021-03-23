#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 07:49:58 2020

@author: jeb
"""

import pandas as pd

fn='/Users/jason/Dropbox/AW/SICE_AW_JEB/CryoClim/discovery_metadata_MODIS.txt'
df = pd.read_csv(fn, sep='\t')
print(df)

n_atts=len(df)

for i in range(0,n_atts):
    if df.attribute[i]!='BLANK':
        print(i,df.attribute[i])
        root_grp.df.name[i]=df.attribute[i]
        
root_grp.geospatial_lat_min=latmin
root_grp.geospatial_lat_max=latmax
root_grp.geospatial_lon_max=lonmax
root_grp.geospatial_lon_min=lonmin
