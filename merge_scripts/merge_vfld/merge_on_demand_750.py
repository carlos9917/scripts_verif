# Merge all the non-overlapping data from the 750 models:
#
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
# and the on_demand models
# sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand
#
# NOTE: Script assumes models are NOT overlapping each other!
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

#this to avoid issues with plotting via qsub
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)

def check_plot(df,fout):
    import seaborn as sns
    dfp=df.astype(float)
    #ax=dfp.plot(x='lon',y='lat',style='o')
    sns_plot=sns.scatterplot(x="lon", y="lat", data=dfp)
    #fig = ax.get_figure()
    #fig.savefig(fout)
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

    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Combine all Greenland 750 m vfld data
                        Example usage: python merge_750models.py -pe 20190101-20190101 -fl 52 -fi 00,06,12,18 -dvfl /netapp/dmiusr/aldtst/vfld -dout /home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl ''',formatter_class=RawTextHelpFormatter)

    parser.add_argument('-pe','--period',metavar='Period to process (YYYYMMDD-YYYYMMDD)',
                                type=str, default='20190101-20190101', required=False)
    parser.add_argument('-fl','--flen',metavar='Forecast length (HH)',
                                type=int, default=52, required=False)
    #parser.add_argument('-fi','--finit',metavar='Forecast init times. One value or list separated by commans (00,06,12,18)',type=str, default='00,06,12,18', required=False)

    parser.add_argument('-dvfl','--vfld_dir',metavar='Path of the vfld directory',
                                type=str, default='/netapp/dmiusr/aldtst/vfld', required=False)
    parser.add_argument('-dout','--out_dir',metavar='Path of the output directory',
                                type=str, default='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl', required=False)
    parser.add_argument('-mm','--merge_models',metavar='List of models I want to merge. String separated by commas',
                                type=str, default='tasii,sgl40h11', required=False)
    parser.add_argument('-mode','--merging_mode',metavar='Merging mode: overlap or nonoverlap',
                                type=str, default='nonoverlap', required=False)

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
    if ',' in args.merge_models:
        mmodels = arg.merge_models.split(',')
    else:
        print("Please provide more than one model: %s"%arg.merge_models)
        print("Format: 'model1,model2...'")
        sys.exit()
    print("arguments to use: %s"%args)
    logFile=os.path.join(outdir,'merge.log')
    print("All screen output will be written to %s"%logFile)
    setup_logger(logFile,outScreen=False)
    #read data for each model
    models = mmodels
    #models=["tasii", "sgl40h11", "nuuk750", "qaan40h11",
    #        "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" ]
    models_data=OrderedDict()
    for model in models:
        models_data[model] = vf(model=model, period=period, flen=flen, datadir=datadir)
        logger.info("model "+model+" done")
    logger.info("merge synop data from all stations (non-overlapping assumed)")

    #now merge the whole data. Choose a model that will contain all dates!
    print("Looping through dates from model %s"%models[0])
    for date in models_data[models[0]].dates:
        logger.debug("Merging date %s"%date)
        #Only collect those dates which contain any data:
        frames_synop = [models_data[m] for m in models_data.keys() if isinstance(models_data[m].data_synop[date],pd.DataFrame)]
        models_avail = [f.model for f in frames_synop]
        logger.debug("Number of models with synop data for %s: %d \n"%(date,len(frames_synop)))
        logger.debug("Available models: %s"%' '.join(models_avail))
        frames_temp = [models_data[m] for m in models_data.keys() if isinstance(models_data[m].data_temp[date],pd.DataFrame)]
        dfs=[f.data_synop[date] for f in frames_synop]
        dft=[f.data_temp[date] for f in frames_temp]
        if len(dfs) >= 2:
            df_synop = pd.concat(dfs,sort=False)
            #fout=os.path.join(outdir,'synop_stations_'+date+'.png')
        else:
            logger.debug("No data for df_synop: %d"%len(dfs))
        if len(dft) >= 2:
            df_temp = pd.concat(dft)
        else:    
            logger.debug("No data for df_temp: %d"%len(dft))
        if len(dfs) >= 2 and len(dft) >= 2:    
            mon_save= monitor(model='gl_ondemand',date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
            mon_save.write_vfld()
            del mon_save
            del df_synop
            del df_temp
