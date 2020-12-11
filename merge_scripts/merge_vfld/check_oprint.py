'''
Check what data is available in 
datadir
ie,
datadir='/scratch/ms/dk/nhz/oprint/'
or 
/scratch/ms/dk/nhd/tmp/carra_temp/
'''
import sys
import os
import glob
import fnmatch
import subprocess
from datetime import datetime
from datetime import timedelta
import numpy as np
from collections import OrderedDict
from finaldate import lastday
from check_merge_availability import select_stream_number
from check_merge_availability import check_streams_availability
from finaldate import lastday

datadir='/scratch/ms/dk/nhz/oprint/'
outdir="/scratch/ms/dk/nhd/tmp/carra_temp/missing_data_nhz"

#datadir='/scratch/ms/dk/nhd/tmp/carra_temp/'
#outdir="/scratch/ms/dk/nhd/tmp/carra_temp/still_missing"
incomplete_years = [2006]

def write_summary(ofile,dates):
    with open(ofile,"w") as f:
        for date in dates:
            f.write(date+"\n")


def search_streams(period,outdir):
    '''Check both streams to see what is missing'''
    #Check IGB domain
    dom_complete = {'IGB': False,'NE':False}
    for dom in ['IGB','NE']:
        dtg_valid, dates_found,dates_notfound = check_streams_availability(dom,period,datadir)
        if len(dtg_valid) == len(dates_found):
            print(f"{dom} complete")
            dom_complete[dom] = True
            files_found = [os.path.join(*[datadir,'carra_'+dom,'vfldcarra_'+dom+d]) for d in dates_found]
        else:
            print(f"{dom} missing %d forecast times"%len(dates_notfound))
            ofile=os.path.join(outdir,"missing_"+dom+'_'+period+".dat")
            print(f'Writing forecast times missing for {dom} in {ofile}')
            files_notfound = [os.path.join(*[datadir,'carra_'+dom,'vfldcarra_'+dom+d]) for d in dates_notfound]
            write_summary(ofile,files_notfound)

    if dom_complete['IGB'] and dom_complete['NE']:
        print(f"Data for NE and IGB in {period} already available")
    else:
        print("Missing files in period: %s"%period)

def main(outdir):

    #incomplete_years = [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2016, 2017, 2018]
    #incomplete_years = [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]

    # to search the whole period:
    #incomplete_years = [i for i in range(1997,2018)]

    incomplete_months = [i for i in range(1,13)]

    for yy in incomplete_years:
        for m in incomplete_months: #range(1,13):
            yyyymm = str(yy)+str(m).zfill(2)
            yyyymmddi = yyyymm+'01'
            yyyymmddf = lastday(yyyymmddi)
            period='-'.join([yyyymmddi,yyyymmddf])
            print(f'Period to check: {period}')
            odir=os.path.join(outdir,str(yy))
            if not os.path.exists(odir):
                os.makedirs(odir)
            search_streams(period,odir)

if __name__ == "__main__":
    main(outdir)
