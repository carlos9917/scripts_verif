#!/usr/bin/env python3

'''
Check what data has been already merged
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

datadir='/scratch/ms/dk/nhz/oprint/'
outdir="/scratch/ms/dk/nhd/tmp/carra_temp/incomplete_merge"


def check_merge(period,datadir):
     ''' 
     check if all files that should be merged are there
     '''
     flen=31
     #init times: 00 and 12. Forecast hours expected from 0-30. Every 1h until 6, then every 3 h
     #init times: 03,06,09,15,18,21. Forecast hours expected from 0-3. Every 1h.
     fhours_long=[str(i).zfill(2) for i in range(0,7)] + [str(i).zfill(2) for i in range(9,flen,3)]
     fhours_short=[str(i).zfill(2) for i in range(0,4)]
     init_expected = [str(i).zfill(2) for i in range(0,22,3)]
     period = period.split('-')
     date_ini=datetime.strptime(period[0],'%Y%m%d')
     date_end=datetime.strptime(period[1],'%Y%m%d')
     dates = [date_ini + timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
     model_dates=[datetime.strftime(date,'%Y%m%d') for date in dates]
     vflddir=os.path.join(datadir,'carra')
     print(f"Searching {vflddir}")
     dates_found=[]
     yyyymm=period[0][0:6]
     print(f'Gonna search in {vflddir} for {yyyymm}')
     for ifile in sorted(os.listdir(vflddir)): #TODO: need to refine search below. 
                                       # Only matching the YYYYMM of first date!
                                       #OK for same month, since usually running
                                       #one month at a time
         if fnmatch.fnmatch(ifile, 'vfld*'+yyyymm+'*'):
             this_date=''.join([n for n in ifile if n.isdigit()])
             #print(f"found file {ifile}")
             dates_found.append(this_date)
     #print(f'Preliminary number of files found: {len(dates_found)}')
     dtg_expected=[]
     for date in model_dates:
         for init in init_expected:
             if init in ['00', '12']:
                 for hour in fhours_long:
                     dtg_expected.append(''.join([date,init,str(hour).zfill(2)]))
             else:
                 for hour in fhours_short:
                     dtg_expected.append(''.join([date,init,str(hour).zfill(2)]))
     dates_pass=[]
     dates_miss=[]
     for dtg in dtg_expected:
         if dtg in dates_found:
             dates_pass.append(dtg)
         else:
             dates_miss.append(dtg)
     #print(f'After:  {len(dates_pass)}')
     return dtg_expected, dates_pass, dates_miss

def write_summary(ofile,dates):
    with open(ofile,"w") as f:
        for date in dates:
            f.write(date+"\n")


def search_period(period,datadir,outdir):
    '''Check both streams to see what is missing'''
    #Check IGB domain
    merge_complete = False
    dtg_valid, dates_found,dates_notfound = check_merge(period,datadir)
    if len(dtg_valid) == len(dates_found):
        print(f"Merge for {period} complete")
        merge_complete = True
        files_found = [os.path.join(*[outdir,'carra','vfldcarra'+d]) for d in dates_found]
    else:
        print(f"{period} missing %d forecast times"%len(dates_notfound))
        ofile=os.path.join(outdir,"missing"+'_'+period+".dat")
        print(f'Writing forecast times missing for {period} in {ofile}')
        files_notfound = [os.path.join(*[outdir,'carra'+'vfldcarra'+d]) for d in dates_notfound]
        write_summary(ofile,files_notfound)

    if merge_complete:
        print(f"Data merge complete for {period}")
    else:
        print(f"Missing files in period: {period}")

def main(outdir,incomplete_years,incomplete_months):
    #incomplete_years = [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2016, 2017, 2018]
    #incomplete_years = [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015]
    # to search the whole period:
    #incomplete_years = [i for i in range(1997,2018)]


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
            search_period(period,datadir,odir)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please provide a year or a list of years (separated by commas)")
        sys.exit()
    else:
        if ',' in sys.argv[1]:
            incomplete_years = sys.argv[1].split(",")
        else:
            incomplete_years = [sys.argv[1]]
    incomplete_months = [i for i in range(1,13)]
    main(outdir,incomplete_years,incomplete_months)
