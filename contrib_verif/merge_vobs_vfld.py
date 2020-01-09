# merge data from vobs and vfld in a verif-compatible ascii file
#
import pandas as pd
import os
import sys
import glob
import fileinput
from datetime import datetime
from datetime import timedelta
import numpy as np
from collections import OrderedDict
import csv
import subprocess
import re
import csv
import logging
logger = logging.getLogger(__name__)
from vobs import vobs as vobs
from vfld import vfld as vfld

def merge_synop(dobs,dexp,var):
    '''
    merge the obs and vfld data for a given datum
    YYYYMMDDIIHH (II=2 digits init time)
    '''
    stnlist=dobs['stationId'].tolist()
    cols_sel=['stationId','lat','lon','HH',var]
    selOBS=dobs[['stationId','lat','lon','HH',var]]

    #quick hack: rename FI as HH in dexp. Only the HH
    #from dobs (renamed HH_x) will be used afterwards. This is just
    #to match the names of the variables in the merge
    #There is no guarantee that HH will be present in the dexp data
    if 'FI' in dexp.columns:
        dexp=dexp.rename(columns={'FI':'HH'})

    selEXP=dexp[['stationId','lat','lon','HH',var]] 
    mergeOE = selOBS.merge(selEXP, on='stationId')
    #the result will contain vars with _x for OBS and _y for EXP
    return mergeOE

def write_var(odir,var,data,datum,ini):
    ''' objective is to create one file per day.
        The data will be appended to the end of the file
        if more data is added
    '''
    units={'TT':'K','FF':'m/s','TD':'K','RH':'%','PS':'hPa'}
    real_names={'TT':'Temperature','FF':'WindSpeed','TD':'DewPointTemperature','RH':'RelativeHumidity',
                'PS':'Pressure'}
    leadtime = datum[10:12]
    #date = str(datum[0:8])+str(ini)
    date = str(datum[0:8]) #date for the data below
    #date_file = str(datum[0:6])+str(ini)+datum[10:12] #date for the file. All data will go in one file per month
    date_file = datum[0:8] #+datum[10:12] #date for the file. All data will go in one file per month
    #odir,fname=os.path.split(infile)
    #odir,stuff = os.path.split(odir)
    ofile=os.path.join(odir,'synop_'+'_'.join([var,date_file])+'.txt')


    exists = os.path.isfile(ofile)
    data['date'] = date
    data['leadtime'] = leadtime
    data['p0']=-999. #np.nan
    data['p11']=-999. #np.nan
    data['pit']=-999. #np.nan
    data=data.rename(columns={var+'_x': 'obs', var+'_y':'fcst',
        'lat_x':'lat','lon_x':'lon','HH_x':'altitude','stationId':'location'})
    data_write=data[['date','leadtime','location','lat','lon','altitude','obs','fcst','p0','p11','pit']]
    if exists==True:
        with open(ofile, 'a') as f:
            data_write.to_csv(f, header=False,index=False,sep=' ')
    else:
        with open(ofile,'w') as f:
            f.write('# variable: %s\n' %real_names[var])
            f.write('# units: $%s$\n' %units[var])
            data_write.to_csv(f,sep=' ',index=False) 

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Combine vobs and vfld data
                        Example usage: python merge_vobs_vfld.py -pe 19980101-19980101 -model EC9 -fi 00 -fl 61 -var TT -dout /perm/ms/dk/nhd/carra_merge_vfld -din /scratch/ms/dk/nhz/oprint/ ''',formatter_class=RawTextHelpFormatter)
    parser.add_argument('-m','--model',metavar='model to process',
                                type=str, default='EC9', required=False)
    parser.add_argument('-pe','--period',metavar='Period to process (YYYYMMDD-YYYYMMDD)',
                                type=str, default='19980101-19980101', required=False)
    parser.add_argument('-fl','--flen',metavar='Forecast length (HH)',
                                type=int, default=62, required=False)
    parser.add_argument('-fi','--finit',metavar='Forecast init times. One value or list separated by commans (00,06,12,18)',
                                type=str, default='00,06,12,18', required=False)
    parser.add_argument('-dout','--out_dir',metavar='Path of the output directory',
                                type=str, default='/perm/ms/dk/nhd/carra_merge_vfld', required=False)
    parser.add_argument('-din','--in_dir',metavar='Path of the input directory',
                                type=str, default='/perm/ms/dk/nhd/carra_merge_vfld', required=False)
    parser.add_argument('-var','--variable',metavar='variable to process',
                                type=str, default='TT', required=False)

    #NOTE: use a short range. 30 days seems to be too long and I run into memory issues! Using 10
    args = parser.parse_args()
    try:
        print("Arguments: %s"%args)
    except:
        print("Error. Exiting")
        parser.print_help()
        sys.exit(0)
    period=args.period #'20190611-20190620'
    model=args.model# 'EC9'
    finit=args.finit #'00'
    flen=args.flen #61
    var=args.variable #'TT'
    datadir=args.in_dir
    odir=args.out_dir
    #datadir='/home/cap/data/from_ecmwf/codes/scripts_verif/contrib_verif/data'
    #datadir='/scratch/ms/dk/nhz/oprint'
    #odir='/home/cap/tmp'
    #odir='/perm/ms/dk/nhd/carra_merge_vfld'
    #get vfld and vobs data
    ec9 = vfld(model=model, period=period, finit=finit, flen=flen, datadir=datadir)
    obs = vobs(period=period, flen=flen, finit=finit, datadir=os.path.join(datadir,'OBS')) #note: vobs only every 24 h

    date_vobs=ec9.dates[0][0:8]+ec9.dates[0][10:12]
    vobs_count=datetime.strptime(date_vobs, "%Y%m%d%H")

    for date in ec9.dates:
        if isinstance(ec9.data_synop[date],pd.DataFrame) and isinstance(obs.data_synop[date],pd.DataFrame):
            print("Merging for date %s"%date)
            merged_df = merge_synop(obs.data_synop[date],ec9.data_synop[date],var)
            write_var(odir,var,merged_df,date,finit)

