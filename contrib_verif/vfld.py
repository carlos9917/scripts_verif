# Class that defines the vfld data from Harmonie
#
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
import csv
import logging
logger = logging.getLogger(__name__)

class vfld(object):
    def __init__(self,  model=None, period=None, finit=None,
                 flen=None, datadir=None):
        self.model = model
        self.period = period.split('-')
        self.finit = finit
        if ',' in self.finit:
            self.finit=finit.split(',')
        else:
            self.finit=[finit]
        self.flen= flen
        self.fhours = list(range(0,flen))
        self.datadir=datadir
        ifiles_model,dates_model = self._locate_files(self.datadir,self.model,self.period,self.finit,self.flen)
        self.ifiles_model=ifiles_model
        self.dates = dates_model
        #self.dates=self._get_dates_from_files(self.ifiles_model)
        data_synop, data_temp, accum_synop = self._get_data(self.ifiles_model)
        self.data_synop = data_synop
        self.data_temp = data_temp
        self.temp_stations = self._get_temp_station_list(self.data_temp)
        self.accum_synop = accum_synop

    def _get_temp_station_list(self,data_temp):
        ''' Extract the temp stations from the first row of data
            of the temp data section of the vfld file,
            which contains: stationId lat lon height
        '''
        # check if temp data is actually there
        #
        tempStations=OrderedDict()
        for date in data_temp.keys():
            if isinstance(data_temp[date], pd.DataFrame):
                tempStations[date] = [data_temp[date].iloc[0][0],data_temp[date].iloc[0][1],
                                      data_temp[date].iloc[0][2], data_temp[date].iloc[0][3]]
            else:
                tempStations[date] = [np.nan,np.nan,np.nan,np.nan]
        return tempStations

    def _get_data(self,ifiles):
        '''
        Extract the data from all ifiles in a df for SYNOP and TEMP data
        '''
        data_synop=OrderedDict()
        data_temp=OrderedDict()
        accum_synop =OrderedDict()
        for i,ifile in enumerate(ifiles):
            date=self.dates[i]
            data_synop[date], data_temp[date], accum_synop[date] = self._split_data(ifile)
            # print a warning if synop data is not there:
            # TODO: if no synop, don't include model!
            if len(data_synop[date]) == 0:
                logger.info("WARNING: synop data for %s[%s] is empty!"%(self.model,date))
                data_synop[date] = 'None'
            if len(data_temp[date]) == 0:
                logger.info("WARNING: temp data for %s[%s] is empty!"%(self.model,date))
                data_temp[date] = 'None'
        return data_synop, data_temp, accum_synop

    def _locate_files(self,datadir,model,period,finit,flen):
        '''
        Locate the files to process from each model.
        period = YYYYMMDD_beg-YYYYMMDD_end
        Shift the file name by -3 h if the model is tasii
        '''
        date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
        date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
        dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
        model_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
        ifiles_model = []
        dtgs=[]

        for date in model_dates:
            for init_hour in self.finit:
                for hour in range(0,flen):
                    dtgs.append(''.join([date,init_hour,str(hour).zfill(2)]))
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
        if (len(ifiles_model) == 0) or (len(set(ifiles_model)) == 1): # if all elements equal all None!
            logger.info("WARNING: no %s data found for dates %s"%(model,model_dates))
            logger.info(ifiles_model)
        logger.debug("first file for model %s: %s"%(self.model,ifiles_model[0]))
        logger.debug("last file for model %s: %s"%(self.model,ifiles_model[-1]))
        return ifiles_model, dtgs

    def _get_synop_vars(self,ifile):
        '''
        Extract information about the SYNOP variables in vfld file
        '''
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

    def _split_data(self,ifile):
        '''
        Split the data from ifile into SYNOP and TEMP
        in two data frames
        '''
        cols_temp = ['PP','FI','TT','RH','DD','FF','QQ','TD'] #this set of temp variables is constant
        header_temp=OrderedDict()
        if ifile != 'None':
            colnames, nsynop_stations, ignore_rows, ntemp_stations, accum_synop = self._get_synop_vars(ifile)
            data_synop = pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,
                    dtype=str,skiprows=ignore_rows,nrows=nsynop_stations)
            #NOTE: will name the columns as VariableName+AccumulationTime. To be split afterwards 
            #when writing the data in vfld format for monitor in vfld_monitor
            #data_synop.columns=colnames
            if 'FI' in colnames:
                data_synop.columns=colnames[0:3]+[' '.join(str(i) for i in col) for col in zip(colnames[3:],accum_synop)]
            else:
                data_synop.columns=colnames[0:4]+[' '.join(str(i) for i in col) for col in zip(colnames[4:],accum_synop)]
            ignore_temp=ignore_rows+data_synop.shape[0]+10
            data_temp =  pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,names=cols_temp,
                                      dtype=str,skiprows=ignore_temp)
        else:
            data_synop = 'None'
            data_temp = 'None'
            accum_synop = 'None'
    
        return data_synop, data_temp, accum_synop

if __name__ == '__main__':
    model='EC9'
    period='20190601-20190601'
    #finit='00,06,12,18'
    finit='00'
    flen=67
    datadir='/home/cap/data/from_ecmwf/codes/scripts_verif/contrib_verif/data'
    ec9 = vfld(model=model, period=period, finit=finit, flen=flen, datadir=datadir)
    print(ec9.data_synop)

