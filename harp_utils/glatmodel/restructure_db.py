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
#NOTE: CCtot from observations is on % in the road model data. TODO: convert in sqlite file
BUFR={'12200':'T2m', '12201': 'TROAD', '12202':'Td2m', '13213':'AccPcp12h', '11002': 'S10m',
       '20010':'CCtot','11001':'D10m'} #20200 is skystatus, but that does not exist

def check_the_dates(df_out:pd.DataFrame) -> None:
    """
    Attempt to check the initial dates for each station
    """
    real_dates=pd.DataFrame({"date":[ts2date(ts) for ts in df_out['validdate']],
                                  "validdate":df_out["validdate"],
                                  "SID":df_out["SID"]})
    #check all stations
    stations = real_dates.drop_duplicates(["SID"])["SID"]
    #df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
    print(f"First dates")
    select_first_date=[]
    #print(real_dates["date"].values[0])
    #print(type(real_dates["date"].values[0]))
    for station in stations:
        dates=real_dates[real_dates["SID"] == station]
        dates.sort_values(by="date",inplace=True)
        begins=dates["date"].iloc[0]
        print(f"First date for {station} = {begins}")
        #convert ns64 date to datetime object
        dates["date"] = dates["date"].dt.date
        fdate=dt.datetime.strftime(dates["date"].values[0],"%Y%m%d")
        set_start_date = dt.datetime(int(fdate[0:4]),int(fdate[4:6]),int(fdate[6:8]),0,0)
        ts_start_date = set_start_date.replace(tzinfo=timezone.utc).timestamp()
        select_first_date.append(set_start_date)
        print(f"{station} should start on {set_start_date}")
        dates["validdate"] = [d - ts_start_date for d in dates["validdate"]]
        dates['leadtime']=dates['validdate'].map(lambda x:ts2date(x).time().hour + ts2date(x).time().minute/60 )
        print(dates.head(10))
    print(f"Final selection of first date :{set(select_first_date)}")

def date2ts(date,dformat="%Y-%m-%d %H:%M:%S.%f"):
    dtime = dt.datetime.strptime(date,dformat)
    return dtime.replace(tzinfo=timezone.utc).timestamp()

def ts2date(ts):
    return dt.datetime.utcfromtimestamp(ts)

def tryconvert(df_geo, x):
    try:
        return(df_geo[df_geo['station']==x]['lon'].values[0])
    except:
        return np.nan

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
        df_out=pd.DataFrame({"parameter":var_names,"accum_hours":var_accum,"units":var_units})
        con=sqlite3.connect(dbase)
        df_out.to_sql('SYNOP_PARAMS', con, if_exists='replace', index=False)
        con.close()
    else:
        print(f"SYNOP_PARAMS already exists in {dbase}") #: {df_check}")
        con.close()

def restructure_fcst_db(dbase:str, model:str, cfg:dict) -> pd.DataFrame:
    
    coord_height_dbase = cfg["coord_height_dbase"]
    print(f'Reading station and heights {coord_height_dbase}')
    con = sqlite3.connect(coord_height_dbase)
    df_geo = pd.read_sql('SELECT * FROM roadstations;', con)
    con.close()
    df_geo.rename(columns={'height':'model_elevation'}, inplace=True)

    print(f"Reading data from {dbase}")
    con = sqlite3.connect(dbase)
    df=pd.read_sql('SELECT * FROM fild7;', con)
    con.close()    
    basename = os.path.basename(dbase)
    yearmonth = basename.split("_")[1]
    cycle = basename.split("_")[2].replace(".db","")
    
    df.drop(axis=1, labels='DATETIME', inplace=True)
    columns= list(df.columns);
    columns.remove('ID');
    columns.remove('TIME');
    columns.remove('FSTEP');

    # I replace the name for the TIME and ID columns to the harp names
    df.rename(columns={'ID':'SID', 'TIME':'validdate',"FSTEP":"leadtime"}, inplace=True)
    
    for column_name in columns:
        
        df_out = df[['SID', 'validdate','leadtime', column_name]].copy()
        
        df_out['p']=np.nan
        #before doing the merge, drop any stations from df_geo NOT in df_out
        unique_to_geo = df_geo.drop_duplicates(["SID"])
        unique_to_df = df_out.drop_duplicates(["SID"])["SID"].to_list()
        diff_in_stations = list(set(unique_to_geo)^set(unique_to_df))
        #print("Differences in stations before correcting for merge")
        #print(diff_in_stations)
        df_geo=df_geo[df_geo["SID"].isin(unique_to_df)]
        df_out=pd.merge(df_out, df_geo, on='SID')

        #TODO:correct the forecast steps (leadtime)
        #check the dates before calculating the leadtime
        #check_the_dates(df_out)
        #sys.exit(0)
        #df_out['leadtime']=df_out['validdate'].map(lambda x:ts2date(x).time().hour + ts2date(x).time().minute/60 )
        #correct strings to add leading zeroes
        #df_out["leadtime"]=[ts.zfill(4) for ts in df_out["leadtime"]]
        #df_out["leadtime"] = [float(ts[0:2]) + float(ts[2:4])/60. for ts in df_out["leadtime"]]

        #drop all the fractional times, still to figure out how to use them
        df_out["leadtime"] = df_out["leadtime"].astype("float")
        df_out = df_out[df_out["leadtime"]%1 != 0.5]
        df_out["leadtime"] = df_out["leadtime"].astype("int64")
        df_out['fcdate']=df_out['validdate']-df_out['leadtime']*3600
        df_out['fcdate']=df_out['fcdate'].astype('int64')
        df_out['parameter']=variables[column_name]
        df_out['units']=units[column_name]
        df_out.rename(columns={column_name:f'{model}_det'}, inplace=True)
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        year = yearmonth[0:4]
        month = yearmonth[4:6]
        dbase_path = os.path.join(cfg['sql_dbs_path'],"FCTABLE",model,year,month)
        if not os.path.isdir(dbase_path):
            os.makedirs(dbase_path)
        dbase_out=os.path.join(dbase_path,'FCTABLE_'+variables[column_name]+'_'+yearmonth+"_"+cycle+'.sqlite')

        if not os.path.isfile(dbase_out):
            schema = f"""CREATE TABLE FC(fcdate INT, leadtime INT, parameter TEXT, SID INT, lat DOUBLE, lon DOUBLE, model_elevation DOUBLE, p DOUBLE, units TEXT, validdate INT, {model}_det DOUBLE);"""
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
    base_name = os.path.split(dbase)[-1]
    name = base_name.split("_")[1]    
    if name in BUFR.keys():
        param = BUFR[name]
        print(f"Doing parameter {param}")
    else:
        print("parameter not in list of parameters to process")
        print(name)
        print(BUFR.keys())
        return
        
    coord_height_dbase = cfg["coord_height_dbase"]
    print(f'Reading station and heights {coord_height_dbase}')
    con = sqlite3.connect(coord_height_dbase)
    df_geo = pd.read_sql('SELECT * FROM roadstations;', con)
    con.close()
    #rename height as elev
    df_geo.rename(columns={"height":"elev"},inplace=True)
    con = sqlite3.connect(dbase)
    print(f"Reading the raw data for observations from {dbase}")
    df_raw = pd.read_sql('SELECT ID, SENSOR, TIME, MEAS FROM glatdump;', con)
    con.close()

    #create new column with 6 digits station number
    df_raw["SID"] = [str(sid)+str(df_raw["SENSOR"].values[k]).zfill(2) for k,sid in enumerate(df_raw["ID"])] 
    df_raw["SID"] = df_raw["SID"].astype(int)

    df_raw.rename(columns={'TIME':'validdate','MEAS': param}, inplace=True)
    df_raw.drop(columns=["ID","SENSOR"],inplace=True)
    df_raw.drop_duplicates(['SID', 'validdate'], inplace=True) 

    # Drop all instances which are not hourly
    print(f"Dropping all values not on the hour")
    df_raw=df_raw[df_raw["validdate"]%3600 == 0]
    dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+str(year)+'.sqlite')

    #output for one parameter only
    dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+param+'_'+str(year)+'.sqlite')
    print(f"Writing obs data to {dbase_out}")
    param_type={"validdate":int, "SID": int, "lat": float, "lon":float, "elev":float,
                 "CCtot":float, "D10m":float,"S10m": float, "T2m":float, "Td2m":float, "RH2m":float, "Q2m":float, 
                 "Ps":float, "Pmsl":float, "vis":float, "Tmax":float, "Tmin":float, "AccPcp12h":float, "Cbase":float, "TROAD":float, "Ice_road":float}
    if not os.path.isfile(dbase_out):
         print(f"Creating new obs database {dbase_out}")
         con=sqlite3.connect(dbase_out)
         #general schema (not using anymore)
         schema_all = """
CREATE TABLE IF NOT EXISTS "SYNOP" (
"validdate" INT, "SID" INT, "lat" REAL, "lon" REAL, "elev" REAL,
  "CCtot" REAL, "D10m" REAL, "S10m" REAL, "T2m" REAL, "Td2m" REAL, "RH2m" REAL, "Q2m" REAL, "Ps" REAL, "Pmsl" REAL, "vis" REAL, "Tmax" REAL, "Tmin" REAL, "AccPcp12h" REAL, "Cbase" REAL, "TROAD" REAL, "Ice_road" REAL);"""
         #schema for one parameter only
         schema = f"""
CREATE TABLE IF NOT EXISTS "SYNOP" (
"validdate" INT, "SID" INT, "lat" REAL, "lon" REAL, "elev" REAL,
  "{param}" REAL);"""
         cursor = con.cursor()
         cursor.execute(schema)
         #add the geo info to the raw data:
         df_raw_ext=pd.merge(df_raw, df_geo, on='SID', how='inner', validate='m:1')
         df_raw_ext.drop_duplicates(['SID', 'validdate'], inplace=True)
         # rearrange the columns
         base_cols=["validdate","SID", "lat","lon","elev"]
         var_cols=[v for v in df_raw_ext.columns if v not in base_cols]
         write_cols = base_cols + var_cols
         df_raw_ext[write_cols].to_sql('SYNOP', con, if_exists='replace', index = False)
         schema_index = """CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"""
         cursor.execute(schema_index)
         con.close()
    else:    
         print(f"Updating obs database {dbase_out}")
         conn=sqlite3.connect(dbase_out)
         #read the data alredy in database
         df_out = pd.read_sql('SELECT * FROM SYNOP;', conn)
         #this line avoids conflicts with data types when merging
         df_out[param] = df_out[param].astype(param_type[param])
         #print(df_out.dtypes)
         #print(df_input.dtypes)
         #add the geo info to the raw data:
         df_raw_ext = pd.merge(df_raw, df_geo, on='SID', how='inner', validate='m:1')
         print("Merging data before dumping it")
         df_write=pd.concat([df_out,df_raw_ext])
         df_write.drop_duplicates(['SID', 'validdate'], inplace=True)
         # rearrange the columns
         base_cols=["validdate","SID", "lat","lon","elev"]
         var_cols=[v for v in df_write.columns if v not in base_cols]
         write_cols = base_cols + var_cols
         df_write[write_cols].to_sql('SYNOP', conn, if_exists='replace', index = False)
         schema_index = """CREATE UNIQUE INDEX index_validdate_SID ON SYNOP (validdate,SID);"""
         cursor = conn.cursor()
         cursor.execute(schema_index)
         conn.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script so useful.')
    parser.add_argument('--param', type=str)
    parser.add_argument('--file', type=str)
    parser.add_argument('--year', type=int)
    parser.add_argument('--config', type=str)
    parser.add_argument('process_obs', type=int)
    parser.add_argument('process_fcst', type=int)
    parser.add_argument('--model', type=str) #change the output of the forecast model
    args = parser.parse_args()
    
    cfg_file = args.config
    if not os.path.isfile(cfg_file):
        print(f"Config file {cfg_file} not found!")
        sys.exit(1)
    else:
        with open(cfg_file, "r") as ymlfile:
            cfg = yaml.full_load(ymlfile)

    if args.process_obs:
        print(f"Doing observations for {args.file}")
        restructure_obs_db(args.file, args.year,cfg)
        #dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+str(args.year)+'.sqlite')
        print(args.param)
        dbase_out = os.path.join(cfg['sql_dbs_path'],'OBSTABLE/OBSTABLE_'+BUFR[args.param]+'_'+str(args.year)+'.sqlite')
        create_synop_params(dbase_out, variables, units, accum)
    if args.process_fcst:
        print(f"Doing forecasts for {args.file}")
        restructure_fcst_db(args.file,args.model,cfg)
