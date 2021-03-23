# -*- coding: utf-8 -*-
"""
@author: Adrien Wehrlé, GEUS (Geological Survey of Denmark and Greenland)
"""

from osgeo import gdal, gdalconst
import rasterio
import time

target_crs_fn='/Users/jason/Dropbox/S3/ancil/SICE/BBA_emp.tif'

src_fn = '/Users/jason/Dropbox/S3/ancil/SICE/Greenland_mask_SICE.tif'
ofile = '/Users/jason/Dropbox/S3/ancil/SICE/mask_1km_1487x2687.tif'

src_fn='/Users/jason/Dropbox/S3/ancil/lat.tif'
ofile = '/Users/jason/Dropbox/S3/ancil/SICE/lat_1km_1487x2687.tif'

src_fn='/Users/jason/Dropbox/S3/ancil/lon.tif'
ofile = '/Users/jason/Dropbox/S3/ancil/SICE/lon_1km_1487x2687.tif'

src_fn='/Users/jason/Dropbox/S3/ancil/elev.tif'
ofile = '/Users/jason/Dropbox/S3/ancil/SICE/elev_1km_1487x2687.tif'

start_time = time.time()

print("start")
#source
src = gdal.Open(src_fn, gdalconst.GA_ReadOnly)
src_proj = src.GetProjection()
src_geotrans = src.GetGeoTransform()

#raster to match
match_ds = gdal.Open(target_crs_fn, gdalconst.GA_ReadOnly)
match_proj = match_ds.GetProjection()
match_geotrans = match_ds.GetGeoTransform()
wide = match_ds.RasterXSize
high = match_ds.RasterYSize

#output/destination
dst = gdal.GetDriverByName('Gtiff').Create(ofile, wide, high, 1, gdalconst.GDT_Float32)
dst.SetGeoTransform( match_geotrans )
dst.SetProjection( match_proj)

print("run")
#run
gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_NearestNeighbour) #.GRA_Bilinear
del dst # Flush

#print("final")
islands=rasterio.open(target_crs_fn)
profile=islands.profile
islands_data=islands.read(1)
#islands_data+=260
#sectors_data=rasterio.open(ofile).read(1)
#v=(islands_data!=260)
#sectors_data[v]=islands_data[v]

wo=0
if wo:
    with rasterio.open(ofile, 'w', **profile) as dst:
        dst.write(dst, 1)

import os
ofile2 = '/tmp/x.tif'
msg='gdal_translate -co COMPRESS=DEFLATE '+ofile+' '+ofile2
print(msg)
os.system(msg)
os.system('/bin/mv '+ofile2+' '+ofile)
print("done")

end_time = time.time()

dt=end_time - start_time
print("time: "+str("%8.1f"%dt).lstrip()+'s')