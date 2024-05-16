import pandas as pd
df_glat=pd.read_csv("glatmodel_data.csv")
df_r01=pd.read_csv("R01_data.csv")

import pdb
pdb.set_trace()

station=100001
stations=[100001, 100100, 100200, 100300, 100400, 100500, 100501, 100600, 100601, 100700] 
stations = [100001, 100100, 100200, 100300, 100400, 100500, 100501, 100600, 100601, 100700, 100800, 100900]
#select a particular station
#df_glat_sel = df_glat[df_glat["site_ID"] == station]
#df_r01_sel = df_r01[df_glat["site_ID"] == station]

#if not doing selection before...
#df_glat_sel = df_glat[df_glat['site_ID'].isin(stations)]
#df_r01_sel = df_r01[df_r01['site_ID'].isin(stations)]
#simple concatenation by merging them together
#frames=[df_glat_sel, df_r01_sel]
frames=[df_glat, df_r01]
result = pd.concat(frames)
#result = pd.concat(frames,axis=1)
#select only 4 stations to process
#result = result
result.to_csv("merged_r01_glat.csv",index=False)
