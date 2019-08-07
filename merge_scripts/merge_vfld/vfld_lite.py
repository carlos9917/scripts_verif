# Class that defines the vfld file of an Harmonie-lite model like:
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
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

datadir='/netapp/dmiusr/aldtst/vfld'

class vfld_lite(object):
    def __init__(self,  model=None, period=None, finit=None,
                 flen=None, searchdir=None):
        self.model = model
        self.period = period.split('-')
        self.finit=finit.split(',')
        self.flen= flen
        self.fhours = list(range(0,flen))
    def locate_files(self,model,period,finit,flen):
        #locate the files to process from each model.
        #period = YYYYMMDD_beg-YYYYMMDD_end
        #Shift the file name by -3 h if the model is tasii
        date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
        date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
        dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
        model_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
        ifiles_model = []

        for date in model_dates:
            for init_hour in finit:
                for hour in range(0,flen):
                    if model != 'tasii':
                        fname=''.join(['vfld',model,date,init_hour,str(hour).zfill(2)])
                        fdir='/'.join([datadir,model])
                        ifile=os.path.join(fdir,fname)
                        if os.path.exists(ifile):
                            ifiles_model.append(ifile)
                        else:
                            ifiles_model.append('None')
                    elif model == 'tasii':
                        dtgtas=datetime.datetime.strptime(date+init_hour,'%Y%m%d%H') - datetime.timedelta(seconds=10800)
                        dtgtas = datetime.datetime.strftime(dtgtas,'%Y%m%d%H')
                        hour3=str(hour+3).zfill(2)
                        fname=''.join(['vfld',model,dtgtas,hour3])
                        fdir='/'.join([datadir,model])
                        ifile=os.path.join(fdir,fname)
                        if os.path.exists(ifile):
                            ifiles_model.append(ifile)
                        else:
                            ifiles_model.append('None')
                    else:
                        print("model %s not in in the data directory!"%model) 
                        
        return ifiles_model    

    def _get_synop_vars(self,ifile):
        #Read this file to determine number of variables in file:
        first_two=[]
        with open(ifile) as f:
            first_two.extend(str(f.readline()).rstrip() for i in range(2))
        nsynop_vars=int(first_two[-1]) # number of variables in synop data
        ntemp_stations=int(first_two[-1]) # number of temp stations in file
        nsynop_stations,ntemp_stations,ver_file =  first_two[0].split() # number of synop stations in file
        nsynop_stations=int(nsynop_stations)
        ntemp_stations = int(ntemp_stations)
    
        lines_header =[]
        with open(ifile) as f:
                lines_header.extend(f.readline().rstrip() for i in range(nsynop_vars+2))
        lines_clean =  [re.sub('\s+',' ',i).strip() for i in lines_header]        
        vars_synop=[i.split(' ')[0] for i in lines_clean[2:]]
        accum_synop=[i.split(' ')[1] for i in lines_clean[2:]] #accumulation times. Needed to write the data at the end
        if 'FI' in vars_synop:
            colnames= ['stationId','lat','lon'] + vars_synop
            start_col_replace = 3
        else:
            colnames=['stationId','lat','lon','HH'] + vars_synop
            start_col_replace = 4
        ignore_rows = 2 + nsynop_vars # number of rows to ignore before reading the actual synop data
        return colnames, nsynop_stations, ignore_rows, ntemp_stations, accum_synop

    def split_data(model,ifile):
        '''
        Split the data files into SYNOP and TEMP data
        '''
        data_synop= OrderedDict()
        cols_temp = ['PP','FI','TT','RH','DD','FF','QQ','TD']
        #header_synop=OrderedDict()
        data_temp= OrderedDict()
        header_temp=OrderedDict()
        #for model in models:
        #for ifile in input_files[model]:
        if ifile != 'None':
            colnames, nsynop_stations, ignore_rows, ntemp_stations, accum_synop = _get_synop_vars(ifile)
            data_synop[model] = pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,
                    dtype=str,skiprows=ignore_rows,nrows=nsynop_stations)
            data_synop[model].columns=colnames
    
            ignore_temp=ignore_rows+data_synop[model].shape[0]+10
            data_temp[model] =  pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,names=cols_temp,
                                      dtype=str,skiprows=ignore_temp)
        else:
            data_synop[model] = 'None'
            data_temp[model] = 'None'
    
        return data_synop, data_temp, accum_synop

if __name__ == '__main__':
    models=[]
    for model in ['tasii','sgl40h11']:
        models.append(

