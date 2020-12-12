# Merge CARRA and CERRA vobs
#
# The aim is to combine all data produced by two different vobs sources
# Whenever a station appears in both data sets, the first data set takes precedence
# over the second
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
import collections

from vobs_merge import vobs as vo
from vobs_merge import vobs_format as vof

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
    to_del=[]
    for st in repeated:
        check_ind=df_temp.loc[df_temp['PP']==st].index.tolist()
        for ch in check_ind[1:]: # keep only first 
            to_del = to_del + list(range(ch,ch+11))
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

    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Combine CARRA and CERRA data 
                        Example usage: python merge_carra_cerra.py -pe 19980101-19980101 -dout /perm/ms/dk/nhd/carra_merge_vobs -dvobs /scratch/ms/dk/nhz/oprint/ ''',formatter_class=RawTextHelpFormatter)

    parser.add_argument('-pe','--period',metavar='Period to process (YYYYMMDD-YYYYMMDD)',
                                type=str, default=None, required=True)

    parser.add_argument('-dvobs','--vobs_dir',metavar='Base path of the vfld directory',
                                type=str, default='../test_data', required=False)

    parser.add_argument('-dout','--out_dir',metavar='Path of the output directory',
                                type=str, default='../test_out', required=False)

    parser.add_argument('-log','--log_file',metavar='log file name',
                                type=str, default='merge_vobs.log', required=False)

    parser.add_argument('-fw','--force_write',action='store_false') # set to true by default
                        #overwrite the existing data if the file already exists

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
    datadir = args.vobs_dir
    log_file = args.log_file
    force_write = args.force_write #True # Force writing. Only for debugging purposes

    logFile=os.path.join(outdir,log_file)
    print("All screen output will be written to %s"%logFile)

    setup_logger(logFile,outScreen=False)
    if (force_write): logger.info("NOTE: forcing overwriting of the vfld files")
    #TODO: calculate dates already processed. Used to do this for vfld...
    #ts_vobs=vobs()        
    #forbidden_dates = ts_vobs.timestamps.simtimes.tolist() #which dates already processed

    cerra = vo(period=period, datadir=os.path.join(datadir,"CERRA"),model="CERRA")
    logger.info("CERRA data loaded")
    carra = vo(period=period, datadir=os.path.join(datadir,"CARRA"),model="CARRA")
    logger.info("CARRA data loaded")
    models=[carra, cerra] #NOTE: Data from first source will replace any repeated values on the second
    logger.info("Merging synop data from all stations")
    for date in carra.dates:
        #if (date not in forbidden_dates) or (force_write) :
        if force_write:
            logger.debug("Merging date %s"%date)
            #Only collect those dates which contain any data:
            frames_synop = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
            models_avail = [f.model for f in frames_synop]
            logger.debug(f"Number of models with synop data for {date}: {len(frames_synop)}")
            logger.debug("Available models (in order of concatenation): %s"%' '.join(models_avail))
            #print(models_avail)
            frames_temp = [f for f in models if isinstance(f.data_temp[date],pd.DataFrame)]
            if len(frames_synop) != 0 and len(frames_synop) == 2: #only merge if two models available!
                dfs=[f.data_synop[date] for f in frames_synop]
                dft=[f.data_temp[date] for f in frames_temp]
                df_synop = pd.concat(dfs,sort=False)
                df_synop = df_synop.drop_duplicates(['stationId'],keep='last') #keep
                df_temp = pd.concat(dft,ignore_index=True)
                drop_duplicates(df_temp)
                vobs_save = vof(date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
                vobs_save.write_vobs()
                del df_synop
                del df_temp
                del vobs_save
            else:
                logger.debug("No data available on %s or data available only for one model"%date)
                logger.debug("Number of models: %d"%len(frames_synop))
                #Delete this file if it exists:
                ofile=os.path.join(outdir,''.join(['vfld',carra_branch,date]))
                logger.debug("Skipping this date and deleting %s if it exists"%ofile)
                if os.path.exists(ofile):
                    os.remove(ofile)
                

        else:
            logger.info("Date %s already merged. Jumping to next date."%date)
    logger.info(" >>>>> merge script finished <<<<< ")
