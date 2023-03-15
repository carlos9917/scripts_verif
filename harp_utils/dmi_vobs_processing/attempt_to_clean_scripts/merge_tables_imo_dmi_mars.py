#!/usr/bin/env python
"""
Merge the table DMI_MARS with the IMO table
IMO data takes precedence
"""
import sqlite3
import pandas as pd
import os
import numpy as np
from typing import List, Set, Dict, Tuple

def get_dmi_mars(dbase:str) -> Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    con=sqlite3.connect(dbase)
    cursor=con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    synop=pd.read_sql("SELECT * FROM SYNOP", con)
    temp=pd.read_sql("SELECT * FROM TEMP", con)
    synop_params = pd.read_sql("SELECT * FROM SYNOP_params", con)
    temp_params = pd.read_sql("SELECT * FROM TEMP_params", con)
    con.close()
    return synop,temp,synop_params,temp_params

#### IMO
def get_imo(dbase:str) -> Tuple[pd.DataFrame,pd.DataFrame]:
    con=sqlite3.connect(dbase)
    cursor=con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #note: no TEMP data in DMI data
    synop_imo=pd.read_sql("SELECT * FROM SYNOP", con)
    synop_params_imo = pd.read_sql("SELECT * FROM SYNOP_params", con)
    con.close()
    return synop_imo, synop_params_imo

def merge_all(dbase:str, 
              synop:pd.DataFrame,
              synop_imo: pd.DataFrame,
              temp:pd.DataFrame,
              synop_params:pd.DataFrame,
              synop_params_imo:pd.DataFrame,
              temp_params:pd.DataFrame) -> None:
    # merge imo and mars. There is only synop in imo source
    #merge synop. IMO is kept
    df_synop = pd.concat([synop,synop_imo],sort=False).fillna(np.nan)
    merge_synop = df_synop.drop_duplicates(['validdate','SID'],keep='last')
    
    df_synop_params=pd.concat([synop_params,synop_params_imo],sort=False)
    merge_synop_params = df_synop_params.drop_duplicates(['parameter'],keep='last')
    
    list_of_variables=",".join(df_synop.columns.to_list())
    list_vars = ",".join(df_synop.columns.to_list())
    
    #Create the new database with the merged data
    con = sqlite3.connect(dbase)
    merge_synop.to_sql(name="SYNOP",con=con,if_exists="replace",index=False)
    merge_synop_params.to_sql(name="SYNOP_PARAMS",con=con,if_exists="replace",index=False)
    create_index="CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"
    con.execute(create_index)
    
    #Write the TEMP data
    temp.to_sql(name="TEMP",con=con,if_exists="replace",index=False)
    create_index="CREATE UNIQUE INDEX index_validdate_SID_p ON TEMP(validdate,SID,p)"
    con.execute(create_index)
    temp_params.to_sql(name="TEMP_PARAMS",con=con,if_exists="replace",index=False)
    
    con.close()

if __name__ == "__main__":
    dbase="/data/projects/nckf/danra/vfld/vobs_to_merge/OBSTABLE_MERGED/OBSTABLE_DMI_MARS_2022.sqlite"
    synop,temp,synop_params,temp_params = get_dmi_mars(dbase)
    dbase=os.path.join("/data/projects/nckf/danra/vfld/vobs_to_merge","IMO","OBSTABLE_2022.sqlite")
    synop_imo, synop_params_imo = get_imo(dbase)
    # new database
    dbase = "/data/projects/nckf/danra/vfld/vobs_to_merge/OBSTABLE_MERGED/OBSTABLE_2022.sqlite"
    merge_all(dbase,synop,synop_imo,temp,synop_params,synop_params_imo,temp_params)
