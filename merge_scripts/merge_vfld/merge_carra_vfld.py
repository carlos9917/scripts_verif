# Merge NE and IGB vfld data
#
# The aim is to combine all data produced by the NE and IGB domains.
# Whenever a station appears in both data sets, the NE data set takes precedence
# /scratch/ms/dk/nhz/oprint/carra_IGB
# /scratch/ms/dk/nhz/oprint/carra_NE
#
import logging
import pandas as pd
import os
import sys
import glob
import fileinput
import datetime
import numpy as np
from collections import OrderedDict
import csv
import subprocess
import re
from vfld import vfld as vf
from vfld import vfld_monitor as monitor
import collections
#this to avoid issues with plotting via qsub
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)
from vfldmerge_timestamps import vfldmerge_timestamps as vt
def drop_duplicates(df_temp):
    '''
    Drop duplicate stations in the df_temp frame.
    '''
    #identify the station names
    temp_stations=[st for st in df_temp['PP'].values if '.' not in st]
    #idenfity the index of each station
    temp_st_loc=[df_temp.loc[df_temp['PP']==st].index for st in df_temp['PP'] if '.' not in st]
    #repeated stations:
    repeated =[item for item, count in collections.Counter(temp_stations).items() if count > 1]
    #print("before dropping ")
    #print(df_temp.shape)
    to_del=[]
    for st in repeated:
        check_ind=df_temp.loc[df_temp['PP']==st].index.tolist()
        for ch in check_ind[1:]: # keep only first 
            to_del = to_del + list(range(ch,ch+11))
            #df_temp.drop(df_temp.index[ch:ch+11],inplace=True)
    df_temp.drop(to_del,inplace=True)
    

def test_duplicates(df,date,outdir):
    '''
    check duplicated rows in SYNOP data based on stationId.
    Sanity check to check if 
    '''
    #check all duplicates but keep them all (default: keep first)
    check_dups=df_synop[df_synop.duplicated(['stationId'],keep=False)]
    fout=os.path.join(outdir,'checkdups_synop_'+date+'.csv')
    check_dups.to_csv(fout,sep=' ')

def check_plot(df,fout):
    import seaborn as sns
    dfp=df.astype(float)
    sns_plot=sns.scatterplot(x="lon", y="lat", data=dfp)
    sns_plot.figure.savefig(fout)


def setup_logger(logFile,outScreen=False):
    '''
    Set up the logger output
    '''
    global logger
    global fmt
    global fname

    logger = logging.getLogger(__name__)
    fmt_debug = logging.Formatter('%(levelname)s:%(name)s %(message)s - %(asctime)s -  %(module)s.%(funcName)s:%(lineno)s')
    fmt_default = logging.Formatter('%(levelname)-8s:  %(asctime)s -- %(name)s: %(message)s')
    fmt = fmt_default
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fname = logFile
    fh = logging.FileHandler(fname, mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    if outScreen:
        logger.addHandler(ch) # Turn on to also log to screen


if __name__ == '__main__':
    #NOTE: limit period to 1 month at a time.
    # Otherwise the class will become huge!
    # and the the processing time will increase exponentially.
    #period='20190101-20190101'
    #finit='00,06,12,18'
    #flen=52
    #datadir='/netapp/dmiusr/aldtst/vfld'
    #outdir='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl'

    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Combine all Greenland 750 m vfld data
                        Example usage: python merge_carra_vfld.py -pe 19980101-19980101 -fl 21 -fi 00,06,12,18 -dout /perm/ms/dk/nhd/carra_merge_vfld -dvfl /scratch/ms/dk/nhz/oprint/ ''',formatter_class=RawTextHelpFormatter)

    parser.add_argument('-pe','--period',metavar='Period to process (YYYYMMDD-YYYYMMDD)',
                                type=str, default='19980101-19980101', required=False)
    parser.add_argument('-fl','--flen',metavar='Forecast length (HH)',
                                type=int, default=30, required=False)
    parser.add_argument('-fi','--finit',metavar='Forecast init times. One value or list separated by commans (00,06,12,18)',
                                type=str, default='00,06,12,18', required=False)
    parser.add_argument('-dvfl','--vfld_dir',metavar='Path of the vfld directory',
                                type=str, default='/scratch/ms/dk/nhz/oprint/', required=False)
    parser.add_argument('-dout','--out_dir',metavar='Path of the output directory',
                                type=str, default='/perm/ms/dk/nhd/carra_merge_vfld', required=False)

    parser.add_argument('-log','--log_file',metavar='log file name',
                                type=str, default='merge.log', required=False)

    parser.add_argument('-branch','--carra_branch',metavar='branch of carra being used',
                                type=str, default='carra', required=False)

    args = parser.parse_args()


    try:
        print("Arguments: %s"%args)
    except:
        print("Error. Exiting")
        parser.print_help()
        sys.exit(0)
 
    try:
        os.makedirs(args.out_dir)
    except OSError:
        print("%s directory already exists!"%args.out_dir)

    period = args.period    
    outdir  = args.out_dir
    datadir = args.vfld_dir
    flen    = args.flen
    finit   = args.finit
    log_file = args.log_file
    carra_branch = args.carra_branch
    force_write = False # Force writing. Only for debugging purposes

    logFile=os.path.join(outdir,log_file)
    print("All screen output will be written to %s"%logFile)
    setup_logger(logFile,outScreen=False)
    if (force_write): logger.info("NOTE: forcing overwriting of the vfld files")
    ts_vfld=vt()        
    forbidden_dates = ts_vfld.timestamps.simtimes.tolist() #which dates already processed

    igb = vf(model='carra_IGB', period=period, finit=finit, flen=21, datadir=datadir)
    logger.info("carra_IGB data loaded")
    ne = vf(model='carra_NE', period=period, finit=finit, flen=21, datadir=datadir)
    logger.info("carra_NE data loaded")
    models=[igb, ne] #NOTE: order is important here, since I will decide to keep 
                     #last occurrence of duplicated stations after concatenate
    logger.info("merge synop data from all stations")
    for date in igb.dates:
        if (date not in forbidden_dates) or (force_write) :
            logger.debug("Merging date %s"%date)
            #Only collect those dates which contain any data:
            frames_synop = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
            models_avail = [f.model for f in frames_synop]
            logger.debug("Number of models with synop data for %s: %d \n"%(date,len(frames_synop)))
            logger.debug("Available models (in order of concatenation): %s"%' '.join(models_avail))
            #print(models_avail)
            frames_temp = [f for f in models if isinstance(f.data_temp[date],pd.DataFrame)]
            if len(frames_synop) != 0:
                dfs=[f.data_synop[date] for f in frames_synop]
                dft=[f.data_temp[date] for f in frames_temp]
                df_synop = pd.concat(dfs,sort=False)
                #test_duplicates(df_synop,date,outdir) #for debugging
                df_synop = df_synop.drop_duplicates(['stationId'],keep='last') #keeping NE 
                #fout=os.path.join(outdir,'synop_stations_'+date+'.png') #for debugging
                #check_plot(df_synop,fout) #for debugging
                df_temp = pd.concat(dft,ignore_index=True)
                drop_duplicates(df_temp)
                mon_save= monitor(model=carra_branch,date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
                mon_save.write_vfld()
                del df_synop
                del df_temp
                del mon_save
            else:
                logger.debug("No data available on %s"%date)
        else:
            logger.info("Date %s already merged. Jumping to next date."%date)
