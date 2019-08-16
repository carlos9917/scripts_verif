# Merge all the non-overlapping data from the 750 models:
#
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
#
# The aim is to combine all the data produced by the 750 models
# in one file named vfldgl750_*
# Two options here:
# non-overlapping (default): domains don't overlap, hence they all contain different stations
# overlapping: domains share some stations. In this case the priority of
# one model over another must be set
#
# The data is assumed to be split into SYNOPVar/Data and TEMPVar/Data
# as in the merge_models750_IGB.py script
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
    period='20190301-20190331'
    finit='00,06,12,18'
    flen=52
    datadir='/netapp/dmiusr/aldtst/vfld'
    outdir='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test'
    logFile=os.path.join(outdir,'merge.log')
    setup_logger(logFile,outScreen=False)

    tasii = vf(model='tasii', period=period, finit=finit, flen=52, datadir=datadir)
    print("tasii done")
    sgl40h11 = vf(model='sgl40h11', period=period, finit=finit, flen=52, datadir=datadir)
    print("sgl done")
    nuuk750 = vf(model='nuuk750', period=period, finit=finit, flen=52, datadir=datadir)
    print("nuuk done")
    qaan40h11 = vf(model='qaan40h11', period=period, finit=finit, flen=52, datadir=datadir)
    print("qaan done")
    models=[tasii, sgl40h11, nuuk750, qaan40h11]
    print("merge synop data from all stations (non-overlapping assumed)")
    for date in tasii.dates:
        print("Merging date %s"%date)
        #Only collect those dates which contain any data:
        frames_synop = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
        models_avail = [f.model for f in frames_synop]
        print("Number of models with synop data for %s: %d \n"%(date,len(frames_synop)))
        print("Available models")
        print(models_avail)
        frames_temp = [f for f in models if isinstance(f.data_temp[date],pd.DataFrame)]
        dfs=[f.data_synop[date] for f in frames_synop]
        dft=[f.data_temp[date] for f in frames_temp]
        df_synop = pd.concat(dfs,sort=False)
        df_temp = pd.concat(dft)
        mon_save= monitor(model='gl',date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
        mon_save.write_vfld()
        del df_synop
        del df_temp
        del mon_save
