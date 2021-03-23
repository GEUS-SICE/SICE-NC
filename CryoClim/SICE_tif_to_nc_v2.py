# -*- coding: utf-8 -*-
"""
@author: Adrien Wehrlé and Jason Box, GEUS (Geological Survey of Denmark and Greenland)

useful:
https://unidata.github.io/netcdf4-python/netCDF4/index.html
https://pyhogs.github.io/intro_netcdf4.html
https://stackoverflow.com/questions/35071673/netcdf4-for-python-successful-save-failed-to-visualize


Aggregate daily MODIS .tif files into yearly .nc files. 

Each .nc file currently contains two groups:
    - root_grp: geodata (lat, lon, time)
    - vars_grp: BBA values per day

"""
import numpy as np
import rasterio
from netCDF4 import Dataset
import os
import glob
import matplotlib.pyplot as plt
import pandas as pd
import datetime

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

JB=1

# output path
opath='/Users/jason/0_dat/SICE_Greenland_L3_1km_NetCDF/'
os.system('mkdir -p '+opath)

# discovery metadata input file
fn='/Users/jason/Dropbox/AW/SICE_AW_JEB/CryoClim/discovery_metadata_SICE.txt'
# fn='/Users/jason/Dropbox/AW/SICE_AW_JEB/CryoClim/discovery_metadata_MODIS.txt'
df = pd.read_csv(fn, sep='\t')
# print(df)

if JB:
    #longitude and latitude rasters to convert EPS3413 to EPSG4326
    coordinates_4326_x=rasterio.open('/Users/jason/Dropbox/AW/SICE_AW_JEB/CryoClim/ancil/lon_1km_1487x2687.tif').read(1)
    coordinates_4326_y=rasterio.open('/Users/jason/Dropbox/AW/SICE_AW_JEB/CryoClim/ancil/lat_1km_1487x2687.tif').read(1)
else:
    #longitude and latitude rasters to convert EPS3413 to EPSG4326
    coordinates_4326_x=rasterio.open('H:\\MODIS_Greenland_L3_1km_1485_2684\\lon_1km_1485x2684.tif').read(1)
    coordinates_4326_y=rasterio.open('H:\\MODIS_Greenland_L3_1km_1485_2684\\lat_1km_1485x2684.tif').read(1)

v=np.where(coordinates_4326_y!=0.)
latmax=np.nanmax(coordinates_4326_y[v]) ; latmin=np.nanmin(coordinates_4326_y[v])
v=np.where(coordinates_4326_x!=0.)
lonmax=np.nanmax(coordinates_4326_x[v]) ; lonmin=np.nanmin(coordinates_4326_x[v])

# ----- general metadata loading (lon, lat, time)

# for year in range(2017,2020):
for year in range(2018,2020):
    
    #load daily outputs 
    folder_name='H:\\MOD10A1_albedo\\'+str(year)+'\\'
    if JB: folder_name='/Users/jason/0_dat/S3/SICE_v13v14_BBAemp_AK_hybrid_gapless/'

    daily_list_that_year=sorted(list(glob.glob(folder_name+str(year)+'*')))
    # print(daily_list_that_year)
    # x()
    #create nc file
    ofile='C:/Users/Pascal/Desktop/Greenland_1km_albedo_days_April-October_'+str(year)+'.nc'
    if JB: ofile=opath+'Greenland_1km_albedo_days_April-October_'+str(year)+'.nc'
    os.system('/bin/rm '+ofile)
    
    root_grp = Dataset(ofile,'w', format='NETCDF4')
    
    #create two groups from root (for coordinates and variables)
    coords_grp = root_grp.createGroup('Coordinates')
    vars_grp= root_grp.createGroup('Variables')
    
    #create dimensions (specifies the dimensions of the data)
    coords_grp.createDimension('Longitude', None)
    coords_grp.createDimension('Latitude', None)
    
    #create dimension and variable
    coords_grp.createDimension('xx', np.shape(coordinates_4326_x)[0])
    coords_grp.createDimension('yy', np.shape(coordinates_4326_x)[1])
    
    #create variables (pre-allocates NetCDF variables)
    longitude = coords_grp.createVariable('Longitude', 'f4', ('xx', 'yy'), zlib=True) #zlib compression level is 4 by default (9 maximum)
    latitude = coords_grp.createVariable('Latitude', 'f4', ('xx', 'yy'), zlib=True)
    
    #add local attributes to variable instances
    longitude.units = 'degrees east'
    latitude.units = 'degrees north'
    
    #pass the data
    latitude[:,:] = np.flipud(coordinates_4326_y)
    longitude[:,:] = np.flipud(coordinates_4326_x)
    
    #add global attributes after https://adc.met.no/node/4
    cc=0
    root_grp.id = df.attribute[cc] ; cc+=1
    print(df.attribute[cc])
    root_grp.naming_athority = df.attribute[cc] ; cc+=1
    print(df.attribute[cc])
    root_grp.title = df.attribute[cc] ; cc+=1
    print(df.attribute[cc])
    root_grp.summary = df.attribute[cc] ; cc+=1
    print(df.attribute[cc])
    root_grp.keywords = df.attribute[cc] ; cc+=1
    root_grp.geospatial_lat_min=str("%.3f"%latmin) ; cc+=1
    root_grp.geospatial_lat_max=str("%.3f"%latmax) ; cc+=1
    root_grp.geospatial_lon_max=str("%.3f"%lonmin) ; cc+=1
    root_grp.geospatial_lon_min=str("%.3f"%lonmax) ; cc+=1
    root_grp.time_coverage_start = str(year)+'-04-01T15:00:00Z' ; cc+=1
    root_grp.time_coverage_end = str(year)+'-10-31T15:00:00Z' ; cc+=1
    root_grp.Conventions = df.attribute[cc] ; cc+=1
    root_grp.history = df.attribute[cc] ; cc+=1
    root_grp.source = df.attribute[cc] ; cc+=1
    root_grp.processing_level = df.attribute[cc] ; cc+=1
    d = modification_date(folder_name)
    print(d)
    root_grp.date_created = d.strftime("%Y")+'-'+d.strftime("%M")+'-'+d.strftime("%d")+'T'+d.strftime("%I")+":"+d.strftime("%M")+":"+d.strftime("%S")+'Z' ; cc+=1
    root_grp.group=df.attribute[cc] ; cc+=1
    root_grp.creator_institution=df.attribute[cc] ; cc+=1
    root_grp.creator_name=df.attribute[cc] ; cc+=1

    root_grp.creator_email=df.attribute[cc] ; cc+=1
    root_grp.creator_url=df.attribute[cc] ; cc+=1
    root_grp.institution=df.attribute[cc] ; cc+=1
    root_grp.publisher_name=df.attribute[cc] ; cc+=1
    root_grp.publisher_email=df.attribute[cc] ; cc+=1
    root_grp.publisher_url=df.attribute[cc] ; cc+=1
    root_grp.project=df.attribute[cc] ; cc+=1
        
    # -------------------------------------- daily albedo loading
    # print(daily_list_that_year)
    n_files=len(daily_list_that_year)
    cc=0
    for i,date in enumerate(daily_list_that_year):
        if i>=0:
            ymd=daily_list_that_year[i][-14:-4]
            print(i,ymd,year,'remaining',n_files-i)
            #read daily albedo emp
            BBA=daily_list_that_year[i]#+'/'+ymd+'.tif'
            BBA_emp_data_reader=rasterio.open(BBA)
            BBA=BBA_emp_data_reader.read(1)
            #read daily albedo sw
            # BBA_sn_data=BBA_emp_data
            # if os.path.isfile(daily_list_that_year[i]+'/albedo_bb_planar_sw.tif'):
            #     BBA_sn=daily_list_that_year[i]+'/albedo_bb_planar_sw.tif'
            #     BBA_sn_data_reader=rasterio.open(BBA_sn)
            #     BBA_sn_data=BBA_sn_data_reader.read(1)

            # v=np.where((BBA_emp_data<0.565)&(np.isfinite(BBA_emp_data)))
            # v=np.isnan(BBA_emp_data)
            # BBA_emp_data[v]=1.
            v=BBA>1
            BBA[v]=np.nan
            #store variable name 
            
            #create dimension and variable
            if cc==0:
                vars_grp.createDimension('x', np.shape(coordinates_4326_x)[0])
                vars_grp.createDimension('y', np.shape(coordinates_4326_x)[1])
            
            temp=pd.to_datetime(ymd,format="%Y-%m-%d")
            date_object=temp.strftime("%j")
            
            variable = vars_grp.createVariable(date_object, 'f4', ('x', 'y'), zlib=True)

            #pass the data    
            BBA=np.flipud(BBA)
            #pass the data
            variable[:]=BBA
            cc+=1
            
        
        # close .nc file
    root_grp.close()
    
    
    # ----- .nc file reading (example)
    
    # f = Dataset(ofile,'r')
    # plt.figure()
    # # plt.plot(f.groups['Coordinates'].variables['Longitude'][:].data)
    # # plt.imshow(f.groups['Variables'].variables['190'][:].data)
    # print(f)
