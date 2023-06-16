#!/usr/bin/env python
import yaml
import sqlite3
import pandas as pd
import os
import numpy as np
import sys
variables={'WINDSPEED':'S10m', 'ROAD_TEMPERATURE':'TROAD', 'AIR_TEMPERATURE':'T2m'}
units={'WINDSPEED':'m/s', 'ROAD_TEMPERATURE': 'degC', 'AIR_TEMPERATURE':'degC'}
accum={'WINDSPEED':0.0, 'ROAD_TEMPERATURE': 0.0, 'AIR_TEMPERATURE':0.0}

#merge the different variables in one file
with open("config.yml", "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
year="2023"
obstable_path=cfg["obstable_path"]

merge_list=[]
for var in ["TROAD","T2m","S10m"]:
    dbase = os.path.join(obstable_path,"_".join(["OBSTABLE",var,year])+".sqlite")
    print(f"Opening {dbase}")
    conn=sqlite3.connect(dbase)
    synop_df=pd.read_sql("SELECT * FROM SYNOP", conn)
    #This should be done before in the creation of the base synop tables!
    synop_df.drop_duplicates(["validdate","SID"],inplace=True)
    merge_list.append(synop_df)
    conn.close()

synop_data = pd.concat(merge_list,sort=False).fillna(np.nan)
#synop_params = synop_data.drop_duplicates(['parameter'],keep='last')
print("Before writing the merged data set looks like this")
print(synop_data.columns)
print(synop_data)

#create new database
dbase = os.path.join(obstable_path,"OBSTABLE_"+year+".sqlite")
conn = sqlite3.connect(dbase)

#create the SYNOP_PARAMS 
schema_synop_params = """
CREATE TABLE IF NOT EXISTS "SYNOP_PARAMS" (
   "parameter" TEXT,
  "accum_hours" REAL,
  "units" TEXT
); """
cursor = conn.cursor()
cursor.execute(schema_synop_params)


#write the data to SYNOP table
base_cols=["validdate","SID", "lat","lon","elev"]
var_cols=[v for v in synop_data.columns if v not in base_cols]
write_cols = base_cols + var_cols
synop_data[write_cols].to_sql(name="SYNOP",con=conn,if_exists="replace",index=False)

dupli = synop_data[synop_data[['validdate',"SID"]].duplicated() == True]
if not dupli.empty():
    for k,date in enumerate(dupli["validate"]):
        for var in var_cols:
            if dupli[var] == 

import pdb
pdb.set_trace()

#create indices (note: I need SYNOP to exist already!)
schema_index = """CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"""
cursor.execute(schema_index)

#write the data to SYNOP_PARAMS
var_names = [variables[key] for key in variables.keys()]
var_units = [units[key] for key in variables.keys()]
var_accum = [accum[key] for key in variables.keys()]
synop_params=pd.DataFrame({"parameter":var_names,"accum_hours":var_accum,"units":var_units})
synop_params.to_sql(name="SYNOP_PARAMS",con=conn,if_exists="replace",index=False)

#close connection
conn.close()
