#check the timestamps of the vfld files under
# /scratch/ms/dk/nhx/oprint/carra
# Save in an sql file for fast access
#
import os
import time
from collections import OrderedDict
import pandas as pd
import datetime
import re
import sys
import subprocess
import sqlite3
#This is the where I am gonna write the processed data
vfldout='/scratch/ms/dk/nhx/oprint/carra'
#vfldout='/perm/ms/dk/nhd/carra_merge_vfld'
DBASE="/scratch/ms/dk/nhd/CARRA/daily_logs.sqlite"

def progress_stream(ifile):
    '''
    read the sql file with the stream information
    and determine minimum matching dtg
    '''
    import sqlite3
    from dateutil import relativedelta
    conn=sqlite3.connect(ifile)
    sql_command = "SELECT * FROM daily_logs"
    data=pd.read_sql(sql_command, conn)
    streams=['carra_NE_1','carra_NE_2','carra_NE_3','carra_IGB_1','carra_IGB_1B',
         'carra_IGB_2','carra_IGB_2B','carra_IGB_3']
    progress_stream={}
    project_months=24*24
    beg_dates={'carra_NE_1': '1996070100','carra_NE_2':'2005090100','carra_NE_3':'2013090100',
            'carra_IGB_1':'1996070100','carra_IGB_1B':'2001090100','carra_IGB_2':'2005090100',
            'carra_IGB_2B':'2009090100','carra_IGB_3':'2013090100'}
    dtg_stream = {'stream_1':[], 'stream_2':[],'stream_3':[]}
    max_dtg_stream = {}
    for st in streams:
        logs=data[data['stream']==st].logfiles.tolist() # check log files for this stream
        logs=[os.path.splitext    (log)[0] for log in logs]
        logs=[os.path.split(log)[1] for log in logs]
        logs=[log.replace('.html','') for log in logs] #get rid of any .gz in strings
        log_dates=[int(log.split('_')[2]) for log in logs]
        DTG_min=str(min(log_dates))
        DTG_max=str(max(log_dates))
        #Two lines below: check stream number, save max date for this stream
        check_digit=''.join(c for c in st if c.isdigit())
        dtg_stream['stream_'+check_digit].append(max(log_dates))
    #Go through list of max dates for all streams. Keep minimum so it matches both NE and IGB
    #The dates between last merged vfld and current can then be processed
    for i in range(1,4):    
        max_dtg_stream['stream_'+str(i)]=str(min(dtg_stream['stream_'+str(i)]))
    #print("total months completed: %d (%g)"%(months_total,total))
    return max_dtg_stream


#Class to store all time stamps for a given stream
class vfldmerge_timestamps(object):
    def __init__(self,   read_archive=False, date=None, ifile=None, use_pkl=True, use_sql=None):
        self.read_archive = read_archive
        self.date = None #to be used only with read_archive
        self.ifile = ifile
        if read_archive:
            self.timestamps = self._read_sql(self.ifile)
        else:    
            self.timestamps = self._get_timestamps()
        self.now=datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H%M%S')
        self.today=datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d')
        #self.count=self.timestamps.groupby(['Year/Month/Day','simtimes']).size().reset_index(name='count')

    def _get_timestamps(self):
        times=[] 
        files=[]
        sim_times=[]
        os.chdir(vfldout)
        sortedfiles=sorted(os.listdir(vfldout), key=os.path.getmtime)
        for vfile in sortedfiles:
            #the file should only have 3 parts after 1st split, last part is YYYYMMDD.html
            if 'vfldcarra' in vfile:
                stuff,simdate=vfile.split('vfldcarra')
                fpath=os.path.join(vfldout,vfile)
                files.append(fpath)
                mtime=time.ctime(os.path.getmtime(fpath))
                times.append(mtime)
                sim_times.append(simdate)
        timestamps = pd.DataFrame({'vfld':files,'simtimes':sim_times,'timestamp':times})
        timestamps['timestamp'] = pd.to_datetime(timestamps['timestamp'])
        #I keep this format for easier reading only...
        timestamps['Year/Month/Day']=timestamps['timestamp'].apply(lambda x: "%s/%s/%s" % (str(x.year),str(x.month).zfill(2), str(x.day).zfill(2)))
        return timestamps

    def save_data(self,outdir,prefix='carra_tstamps'):
        fout=os.path.join(outdir,'_'.join([prefix,self.now])+'.pkl')
        self.timestamps.to_pickle(fout)

    def _read_pkl(self,ifile):
        ts = pd.read_pickle(ifile)
        return ts

    def _read_sql(self,ifile):
        conn=sqlite3.connect(ifile)
        sql_command = "SELECT * FROM daily_logs"
        ts = pd.read_sql(sql_command, conn)
        return ts


if __name__ == "__main__":
    print("Reading timestamps")
    ts_vfld=vfldmerge_timestamps()        
    vfld_merged = ts_vfld.timestamps.simtimes.tolist() #which dates already processed
    #which max dates per stream I can process now
    max_dtg_stream = progress_stream(DBASE)
    import pdb
    pdb.set_trace()
    #print("Counting data")
    #today=datetime.datetime.strftime(datetime.datetime.now(),'%Y/%m/%d')
    #count_them=ts_streams.count_timestamps(simnames,today)
    #print(count_them)
