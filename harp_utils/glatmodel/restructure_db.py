#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 14:55:14 2022

@author: tobou
"""
import sqlite3
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timezone
import argparse
import yaml
import os
import sys

def create_synop_params(dbase:str, variables:dict, units:dict, accum:dict) -> None:
    schema = """
CREATE TABLE IF NOT EXISTS "SYNOP_PARAMS" (
   "parameter" TEXT,
  "accum_hours" REAL,
  "units" TEXT
);
    """

    #check first if table exists
    con=sqlite3.connect(dbase)
    query="SELECT name FROM sqlite_master WHERE type='table' AND name='SYNOP_PARAMS'";
    df_check= pd.read_sql(query, con)
    if df_check.empty:
        print(f"Creating SYNOP_PARAMS in {dbase}")
        cursor = con.cursor()
        cursor.execute(schema)
        con.close()
        var_names = [variables[key] for key in variables.keys()]
        var_units = [units[key] for key in variables.keys()]
        var_accum = [accum[key] for key in variables.keys()]
        df_out=pd.DataFrame({"param":var_names,"accum_hours":var_accum,"units":var_units})
        con=sqlite3.connect(dbase)
        df_out.to_sql('SYNOP_PARAMS', con, if_exists='replace', index=False)
        con.close()
    else:
        print(f"SYNOP_PARAMS already exists in {dbase}") #: {df_check}")
        con.close()

def restructure_fcst_db(dbase:str, cfg:dict) -> pd.DataFrame:
    def ts2date(ts):
        return dt.datetime.utcfromtimestamp(ts)
    def date2ts(date,dformat="%Y-%m-%d %H:%M:%S.%f"):
        dtime = dt.datetime.strptime(date,dformat)
        return dtime.replace(tzinfo=timezone.utc).timestamp()
    
    def tryconvert(x):
        try:
            return(df_geo[df_geo['station']==x]['lon'].values[0])
        except:
            return np.nan

    con = sqlite3.connect(cfg['coordinates_path'])
    df_coord= pd.read_sql('SELECT station_id, lat, lon FROM STATIONS;', con)
    con.close()
    print(f"Reading data from {dbase}")
    con = sqlite3.connect(dbase)
    df=pd.read_sql('SELECT * FROM fild7;', con)
    con.close()    
    basename = os.path.basename(dbase)
    basename = basename.replace('.db', '')
    basename = basename.replace('dump_', '')
    basename = basename.split('_')
    yearmonth = basename[0]
    cc=basename[1]
    
    df.drop(axis=1, labels='DATETIME', inplace=True)
    columns= list(df.columns);
    columns.remove('ID');
    columns.remove('TIME');
    
    df_coord.rename(columns={'station_id':'SID'}, inplace=True)
    station_heights_path = cfg["heights_path"]
    print(f'Reading station heights from {station_heights_path}')
    df_heights= pd.read_csv(cfg['heights_path'])
    df_heights['station']//=10000
    df_heights.rename(columns={'station':'SID','height':'model_elevation'}, inplace=True)
    df_heights.drop_duplicates('SID', inplace=True)
    df_geo=pd.merge(df_coord, df_heights, on='SID', validate='1:1')

    df['ID']//=100
    df.rename(columns={'ID':'SID', 'TIME':'validdate'}, inplace=True)
    
    for column_name in columns:
        
        df_out = df[['SID', 'validdate', column_name]].copy()
        
        df_out['p']=np.nan
        
        df_out=pd.merge(df_out, df_geo, on='SID')
        
        df_out['leadtime']=df_out['validdate'].map(lambda x:ts2date(x).time().hour + ts2date(x).time().minute/60 )
        #drop all the fractional times, still to figure out how to use them
        df_out = df_out[df_out["leadtime"]%1 != 0.5]
        df_out["leadtime"] = df_out["leadtime"].astype("int64")
        df_out['fcdate']=df_out['validdate']-df_out['leadtime']*3600
        df_out['fcdate']=df_out['fcdate'].astype('int64')
        

            
        df_out['parameter']=variables[column_name]
        df_out['units']=units[column_name]
        df_out.rename(columns={column_name:'glatmodel_det'}, inplace=True)
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        year = yearmonth[0:4]
        month = yearmonth[4:6]
        dbase_path = os.path.join(cfg['sql_dbs_path'],"FCTABLE",year,month)
        if not os.path.isdir(dbase_path):
            os.makedirs(dbase_path)
        dbase_out=os.path.join(dbase_path,'FCTABLE_'+variables[column_name]+'_'+yearmonth+'_'+cc+'.sqlite')

        if not os.path.isfile(dbase_out):
            schema = """CREATE TABLE FC(fcdate INT, leadtime INT, parameter TEXT, SID INT, lat DOUBLE, lon DOUBLE, model_elevation DOUBLE, p DOUBLE, units TEXT, validdate INT, glatmodel_det DOUBLE);"""
            con=sqlite3.connect(dbase_out)
            print(f"Creating FC table in {dbase_out}")
            cursor = con.cursor()
            cursor.execute(schema)
            cursor = con.cursor()
            schema = """CREATE UNIQUE INDEX index_fcdate_leadtime_SID ON FC(fcdate,leadtime,SID);"""
            cursor.execute(schema)
            print(f"Writing to {dbase_out}")
            #con=sqlite3.connect(dbase_out)
            df_out.to_sql('FC', con, if_exists='replace', index=False)
            con.close()
        else:
            print(f"Writing to {dbase_out}")
            con=sqlite3.connect(dbase_out)
            df_out.to_sql('FC', con, if_exists='replace', index=False)
            con.close()

    return df_out

def restructure_obs_db(dbase:str, year:int, cfg:dict) -> None:
    def ts2date(ts):
        return dt.datetime.utcfromtimestamp(ts)
    def date2ts(date,dformat="%Y-%m-%d %H:%M:%S.%f"):
        dtime = dt.datetime.strptime(date,dformat)
        return dtime.replace(tzinfo=timezone.utc).timestamp()
    
    def tryconvert(x):
        try:
            return(df_geo[df_geo['station']==x]['lon'].values[0])
        except:
            return np.nan
    name = dbase.split("_")[1]    
    if name in BUFR.keys():
        param = BUFR[name]
        print(f"Doing parameter {param}")
    else:
        print(f"{param} not in list of parameters to process")
        return
        
    #i=0
    #for name in list(BUFR.keys()):
    #    if name in dbase:
    #        param = name
    #        i+=1
    #if i==0:
    #    return

    con = sqlite3.connect(cfg['coordinates_path'])
    df_coord = pd.read_sql('SELECT station_id, lat, lon FROM STATIONS;', con)
    con.close()

    con = sqlite3.connect(dbase)
    df_input = pd.read_sql('SELECT ID, TIME, MEAS FROM glatdump;', con)
    con.close()

    df_coord.rename(columns={'station_id':'SID'}, inplace=True)
    df_heights = pd.read_csv(cfg['heights_path'])
    df_heights['station']//=10000
    
    df_heights.rename(columns={'station':'SID','height':'elev'}, inplace=True)
    df_heights.drop_duplicates('SID', inplace=True)
    df_geo = pd.merge(df_coord, df_heights, on='SID', validate='1:1')

    
    df_input.rename(columns={'ID':'SID', 'TIME':'validdate','MEAS': param}, inplace=True)
    df_input.drop_duplicates(['SID', 'validdate'], inplace=True) 
    #print(df_input)
    dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+str(year)+'.sqlite')
    print(f"Writing obs data to {dbase_out}")
    param_type={"validdate":int, "SID": int, "lat": float, "lon":float, "elev":float,
                 "CCtot":float, "D10m":float,"S10m": float, "T2m":float, "Td2m":float, "RH2m":float, "Q2m":float, 
                 "Ps":float, "Pmsl":float, "vis":float, "Tmax":float, "Tmin":float, "AccPcp12h":float, "Cbase":float, "TROAD":float, "Ice_road":float}
    if not os.path.isfile(dbase_out):
         print(f"Creating new obs database {dbase_out}")
         con=sqlite3.connect(dbase_out)
         schema = """
CREATE TABLE IF NOT EXISTS "SYNOP" (
"validdate" INT, "SID" INT, "lat" REAL, "lon" REAL, "elev" REAL,
  "CCtot" REAL, "D10m" REAL, "S10m" REAL, "T2m" REAL, "Td2m" REAL, "RH2m" REAL, "Q2m" REAL, "Ps" REAL, "Pmsl" REAL, "vis" REAL, "Tmax" REAL, "Tmin" REAL, "AccPcp12h" REAL, "Cbase" REAL, "TROAD" REAL, "Ice_road" REAL);"""
         cursor = con.cursor()
         cursor.execute(schema)
         con.close()
    else:    
         print(f"Updating obs database {dbase_out}")
         conn=sqlite3.connect(dbase_out)
         #read the database
         df_out = pd.read_sql('SELECT * FROM SYNOP;', conn)

         #for k,station in enumerate(df_input["SID"]):
         #    date = df_input["validdate"].values[k]
         #    value = df_input[param].values[k]
         #    insert_row = ",".join([station,str(date)+str(value)])
         #    com = '''INSERT OR REPLACE INTO SYNOP (stationID, stationName, lat, lon) VALUES ('''+insert_row+") "
         print("Merging dara before dumping it")
         #this line avoids conflicts with data types when merging
         df_out[param] = df_out[param].astype(param_type[param])
         #print(df_out.dtypes)
         #print(df_input.dtypes)
         df_dump= pd.merge(df_out, df_input, how='outer', on=['SID', 'validdate',param])
         #for k,station in enumerate(df_dump["SID"]):
         #    get_ll = df_geo[df_geo["SID"] == station]
         #    if not get_ll.empty:
         #        df_dump["lat"].values[k] = get_ll["lat"].values[0]
         #        df_dump["lon"].values[k] = get_ll["lon"].values[0]
         #        df_dump["elev"].values[k] = get_ll["elev"].values[0]

         #NOT df_dump = pd.concat(df_out,df_input,on=['SID', 'validdate',param],sort=False)
         #now merge with the lat lon
         #the lat,lon and elev will come from df_geo
         df_dump.drop(labels=['lat','lon','elev'], inplace=True, axis=1)
         df_write=pd.merge(df_dump, df_geo, on='SID', how='inner', validate='m:1')
         #df_dump = df_dump.drop_duplicates(['SID', 'validdate'])#, inplace=True)
         for col in df_write.columns:
             if col not in ["SID","validdate",param]:
                 df_write[col]=df_dump.astype(float)
         df_write.to_sql('SYNOP', conn, if_exists='replace', index = False)
         con.close()
     	 #df_out.to_sql('SYNOP',con,if_exists='replace',index=False)

     	 #df_out.to_sql('SYNOP', con, if_exists='replace', index=False)
         #con.close()
    #try:

    #    df_out = pd.read_sql('SELECT * FROM SYNOP;', con)
    #    df_out.drop(labels=['lat','lon','elev'], inplace=True, axis=1)
    #    
    #    df_out= pd.merge(df_out, df_input, how='outer', on=['SID', 'validdate'])
    #    df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
    #    df_out=pd.merge(df_out, df_geo, on='SID', how='inner', validate='m:1')
    #    
    #    df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
    #    #df_out.dropna(inplace=True)
    #    #df_out=pd.merge(df_input, df_geo, how='outer',on='SID')
    #    try:
    #    	df_out.to_sql('SYNOP', con, if_exists='replace', index=False)
    #    except:
    #    	print("problem saving db")
    #    	return
    #except:
    #    print("output DataFrame does not exist, creating file")
    #    df_out=pd.merge(df_input, df_geo, on='SID', how='inner', validate='m:1')
    #    df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
    #    df_out.dropna(inplace=True)
    #    df_out.to_sql('SYNOP', con, if_exists='fail', index=False) #?
    #    
    #del(df_out)
    #con.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script so useful.')
    parser.add_argument('--param', type=str)
    parser.add_argument('--file', type=str)
    parser.add_argument('--year', type=int)
    parser.add_argument('process_obs', type=int)
    parser.add_argument('process_fcst', type=int)
    args = parser.parse_args()
    variables={'WINDSPEED':'S10m', 'ROAD_TEMPERATURE':'TROAD', 'AIR_TEMPERATURE':'T2m',
               'PRECIP_INTENSITY':'Pcp', 'CLOUDCOVER': 'CCtot', 'CLOUDBASE':'Cbase',
               'DEWPOINT':'Td2m', 'WATER_ON_ROAD':'AccPcp12h', 
               'ICE_ON_ROAD':'Ice_road', 'WIND_DIRECTION':'D10m',
               'PRECIPITATION_TYPE':'Ppcp_type'}
    units={'WINDSPEED':'m/s', 'ROAD_TEMPERATURE': 'degC', 'AIR_TEMPERATURE':'degC', 
           'PRECIP_INTENSITY':'mm', 'CLOUDCOVER':'okta', 'CLOUDBASE':'m',
           'DEWPOINT':'degC', 'WATER_ON_ROAD':'mm', 'ICE_ON_ROAD':'mm',
           'WIND_DIRECTION':'degrees',  'PRECIPITATION_TYPE':'unknown'}
    accum={'WINDSPEED':0.0, 'ROAD_TEMPERATURE': 0.0, 'AIR_TEMPERATURE':0.0,
           'PRECIP_INTENSITY':1.0, 'CLOUDCOVER':0.0, 'CLOUDBASE':0.0,
           'DEWPOINT':0.0, 'WATER_ON_ROAD':1.0, 'ICE_ON_ROAD':1.0,
           'WIND_DIRECTION':0.0,  'PRECIPITATION_TYPE':0.0}
    BUFR={'12200':'T2m', '12201': 'TROAD', '12202':'Td2m', '13213':'AccPcp12h', '11002': 'S10m'}
    
    
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
    if args.process_obs:
        print(f"Doing observations for {args.file}")
        restructure_obs_db(args.file, args.year,cfg)
        dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+str(args.year)+'.sqlite')
        create_synop_params(dbase_out, variables, units, accum)
    if args.process_fcst:
        print(f"Doing forecasts for {args.file}")
        restructure_fcst_db(args.file,cfg)
