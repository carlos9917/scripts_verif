#!/usr/bin/env python
"""
Merge the table DMI_MARS with the IMO table
IMO data takes precedence
Input: merged dbase from DMI and MARS data: OBSTABLE_DMI_MARS_{YEAR}.sqlite
Output: merged dbase with IMO and the sqlite file above
"""
import sqlite3
import pandas as pd
import os
import numpy as np
import sys

LOCAL_PATH="/ec/res4/scratch/nhd/verification/DMI_data/vobs"
if len(sys.argv) == 1:
    print("Path for the databases and year not provided")
    sys.exit(1)
else:
    LOCAL_PATH=sys.argv[1]
    YEAR=sys.argv[2]
    print(f"CLI provided path for the data and year: {LOCAL_PATH}, {YEAR}")


dbase=os.path.join(LOCAL_PATH,f"OBSTABLE_DMI_MARS_{YEAR}.sqlite")
con=sqlite3.connect(dbase)
cursor=con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
synop_mars=pd.read_sql("SELECT * FROM SYNOP", con)
temp_mars=pd.read_sql("SELECT * FROM TEMP", con)
synop_params_mars = pd.read_sql("SELECT * FROM SYNOP_params", con)
temp_params_mars = pd.read_sql("SELECT * FROM TEMP_params", con)
con.close()

#### IMO
source="IMO"
dbase=os.path.join(LOCAL_PATH,source,f"OBSTABLE_{YEAR}.sqlite")
con=sqlite3.connect(dbase)
cursor=con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#note: no TEMP data in DMI data
synop_imo=pd.read_sql("SELECT * FROM SYNOP", con)
synop_params_imo = pd.read_sql("SELECT * FROM SYNOP_params", con)
con.close()

# merge imo and mars. There is only synop in imo source
#merge synop. IMO is kept
df_synop = pd.concat([synop_mars,synop_imo],sort=False).fillna(np.nan)
merge_synop = df_synop.drop_duplicates(['validdate','SID'],keep='last')

df_synop_params=pd.concat([synop_params_mars,synop_params_imo],sort=False)
merge_synop_params = df_synop_params.drop_duplicates(['parameter'],keep='last')

list_of_variables=",".join(df_synop.columns.to_list())
list_vars = ",".join(df_synop.columns.to_list())

#Create the new database with the merged data
# new database
dbase = os.path.join(LOCAL_PATH,f"OBSTABLE_{YEAR}.sqlite")
con = sqlite3.connect(dbase)
merge_synop.to_sql(name="SYNOP",con=con,if_exists="replace",index=False)
merge_synop_params.to_sql(name="SYNOP_PARAMS",con=con,if_exists="replace",index=False)
create_index="CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"
con.execute(create_index)

#Write the TEMP data
temp_mars.to_sql(name="TEMP",con=con,if_exists="replace",index=False)
create_index="CREATE UNIQUE INDEX index_validdate_SID_p ON TEMP(validdate,SID,p)"
con.execute(create_index)
temp_params_mars.to_sql(name="TEMP_PARAMS",con=con,if_exists="replace",index=False)

con.close()
