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


parser = argparse.ArgumentParser(description='Script so useful.')
parser.add_argument('--param', type=str)
parser.add_argument('--file', type=str)
parser.add_argument('--year', type=int)
parser.add_argument('process_obs', type=int)
parser.add_argument('process_fcst', type=int)
args = parser.parse_args()


with open("config.yml", "r") as ymlfile:
 
    cfg = yaml.full_load(ymlfile)
    
    
variables={'WINDSPEED':'S10m', 'ROAD_TEMPERATURE':'TROAD', 'AIR_TEMPERATURE':'T2m',
           'PRECIP_INTENSITY':'Pcp', 'CLOUDCOVER': 'CCtot', 'CLOUDBASE':'Cbase',
           'DEWPOINT':'Td2m', 'WATER_ON_ROAD':'AccPcp12h', 
           'ICE_ON_ROAD':'?ice_road?', 'WIND_DIRECTION':'D10m',
           'PRECIPITATION_TYPE':'?pcp_type?'}
units={'WINDSPEED':'m/s', 'ROAD_TEMPERATURE': 'degC', 'AIR_TEMPERATURE':'degC', 
       'PRECIP_INTENSITY':'mm', 'CLOUDCOVER':'Okta', 'CLOUDBASE':'m',
       'DEWPOINT':'degC', 'WATER_ON_ROAD':'mm', 'ICE_ON_ROAD':'mm',
       'WIND_DIRECTION':'degrees',  'PRECIPITATION_TYPE':'????'}
BUFR={'12200':'T2m', '12201': 'TROAD', '12202':'Td2m', '13213':'AccPcp12h'}



def restructure_fcst_db(file):
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
    
    con = sqlite3.connect(file)
    df=pd.read_sql('SELECT * FROM fild7;', con)
    con.close()    
    
    basename = os.path.basename(file)
    basename = basename.replace('.db', '')
    basename = basename.replace('dump_', '')
    basename = basename.split('_')
    yearmonth = basename[0]
    cc= basename[1]
    
    df.drop(axis=1, labels='DATETIME', inplace=True)
    columns= list(df.columns);
    columns.remove('ID');
    columns.remove('TIME');
    
    df_coord.rename(columns={'station_id':'SID'}, inplace=True)
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
        df_out['fcdate']=df_out['validdate']-df_out['leadtime']*3600
        df_out['fcdate']=df_out['fcdate'].astype('int64')
        

            
        df_out['parameter']=variables[column_name]
        df_out['units']=units[column_name]

        df_out.rename(columns={column_name:'glatmodel_det'}, inplace=True)
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        
        con=sqlite3.connect(cfg['sql_dbs_path']+'FCTABLE/glatmodel/FCTABLE_'+variables[column_name]+'_'+yearmonth+'_'+cc+'.sqlite')
                            
        df_out.to_sql('FC', con, if_exists='replace', index=False)
        con.close()

    return df_out

def restructure_obs_db(file, year=2000):
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
    i=0
    for name in list(BUFR.keys()):
        if name in file:
            param = name
            i+=1
    if i==0:
        return
    
    
    con = sqlite3.connect(cfg['coordinates_path'])
    df_coord= pd.read_sql('SELECT station_id, lat, lon FROM STATIONS;', con)
    con.close()

    con = sqlite3.connect(file)
    
    df_input=pd.read_sql('SELECT ID, TIME, MEAS FROM glatdump;', con)
    
    
    
    con.close()


    
    df_coord.rename(columns={'station_id':'SID'}, inplace=True)
    df_heights= pd.read_csv(cfg['heights_path'])
    df_heights['station']//=10000
    
    df_heights.rename(columns={'station':'SID','height':'elev'}, inplace=True)
    df_heights.drop_duplicates('SID', inplace=True)
    df_geo=pd.merge(df_coord, df_heights, on='SID', validate='1:1')

    
    df_input.rename(columns={'ID':'SID', 'TIME':'validdate','MEAS': BUFR[param]}, inplace=True); print(df_input)
    df_input.drop_duplicates(['SID', 'validdate'], inplace=True); print(df_input)

    con=sqlite3.connect(cfg['sql_dbs_path']+'OBSTABLE/OBSTABLE_'+str(year)+'_.sqlite')

    try:
        df_out= pd.read_sql('SELECT * FROM SYNOP;', con)
        df_out.drop(labels=['lat','lon','elev'], inplace=True, axis=1)
        
        df_out= pd.merge(df_out, df_input, how='outer', on=['SID', 'validdate'])
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        df_out=pd.merge(df_out, df_geo, on='SID', how='inner', validate='m:1')
        
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        #df_out.dropna(inplace=True)
        #df_out=pd.merge(df_input, df_geo, how='outer',on='SID')
        try:
        	df_out.to_sql('SYNOP', con, if_exists='replace', index=False)
        except:
        	print("problem saving db")
        	return
    except:
        print("output DataFrame does not exist, creating file")
        df_out=pd.merge(df_input, df_geo, on='SID', how='inner', validate='m:1')
        df_out.drop_duplicates(['SID', 'validdate'], inplace=True)
        df_out.dropna(inplace=True)
        df_out.to_sql('SYNOP', con, if_exists='fail', index=False) #?
        
    del(df_out)
    con.close()
    
    return 

#df_out= restructure_obs_db('/home/tobou/Desktop/sql_dbs/obs/2021/dump_12201_20210101000000_20210131230000.db')



if __name__ == "__main__":
    if args.process_obs:
        restructure_obs_db(args.file, args.year)
    if args.process_fcst:
        restructure_fcst_db(args.file)



