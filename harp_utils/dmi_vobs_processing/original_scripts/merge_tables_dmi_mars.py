#!/usr/bin/env python

"""
Merge tables from DMI and MARS
DMI data takes precedence
"""
import sqlite3
import pandas as pd
import os
import numpy as np
model="MARS"
dbase=os.path.join("/data/projects/nckf/danra/vfld/vobs_to_merge",model,"OBSTABLE_2023.sqlite")
con=sqlite3.connect(dbase)
cursor=con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
synop_mars=pd.read_sql("SELECT * FROM SYNOP", con)
temp_mars=pd.read_sql("SELECT * FROM TEMP", con)
synop_params_mars = pd.read_sql("SELECT * FROM SYNOP_params", con)
temp_params_mars = pd.read_sql("SELECT * FROM TEMP_params", con)
con.close()

#### DMI
model="DMI"
dbase=os.path.join("/data/projects/nckf/danra/vfld/vobs_to_merge",model,"OBSTABLE_2023.sqlite")
con=sqlite3.connect(dbase)
cursor=con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#note: no TEMP data in DMI data
synop_dmi=pd.read_sql("SELECT * FROM SYNOP", con)
synop_params_dmi = pd.read_sql("SELECT * FROM SYNOP_params", con)
con.close()

# merge dmi and mars. There is only synop in dmi source
#merge synop. DMI is kept
df_synop = pd.concat([synop_mars,synop_dmi],sort=False).fillna(np.nan)
merge_synop = df_synop.drop_duplicates(['validdate','SID'],keep='last')

df_synop_params=pd.concat([synop_params_mars,synop_params_dmi],sort=False)
merge_synop_params = df_synop_params.drop_duplicates(['parameter'],keep='last')

list_of_variables=",".join(df_synop.columns.to_list())
list_vars = ",".join(df_synop.columns.to_list())

#Create the new database with the merged data
# new database
dbase = "/data/projects/nckf/danra/vfld/vobs_to_merge/OBSTABLE_MERGED/OBSTABLE_DMI_MARS_2023.sqlite"
create_table = """
CREATE TABLE IF NOT EXISTS SYNOP ("""+list_vars+""",PRIMARY KEY (validdate,SID));
"""
con = sqlite3.connect(dbase)
merge_synop.to_sql(name="SYNOP",con=con,if_exists="replace",index=False)
merge_synop_params.to_sql(name="SYNOP_PARAMS",con=con,if_exists="replace",index=False)
create_index="CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"
con.execute(create_index)
temp_mars.to_sql(name="TEMP",con=con,if_exists="replace",index=False)
create_index="CREATE UNIQUE INDEX index_validdate_SID_p ON TEMP(validdate,SID,p)"
con.execute(create_index)
temp_params_mars.to_sql(name="TEMP_PARAMS",con=con,if_exists="replace",index=False)

con.close()
#df_synop.to_sql(name="SYNOP_params",con=con,if_exists="replace",index=False)
#con.execute('ALTER TABLE SYNOP ADD PRIMARY KEY (validdate, SID);')
#df_synop.to_sql(name='SYNOP', con=con)
#create_synop_params="CREATE TABLE SYNOP_params(parameter VARCHAR, accum_hours REAL, units VARCHAR)"
#fillup this table
#for col in df_synop.columns:

