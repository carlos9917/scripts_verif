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


class vfld_lite(object):
    def __init__(self,  model=None, period=None, finit=None,
                 flen=None, datadir=None):
        self.model = model
        self.period = period.split('-')
        self.finit=finit.split(',')
        self.flen= flen
        self.fhours = list(range(0,flen))
        self.datadir=datadir
        ifiles_model,dates_model = self._locate_files(self.model,self.period,self.finit,self.flen)
        self.ifiles_model=ifiles_model
        self.dates = dates_model
        #self.dates=self._get_dates_from_files(self.ifiles_model)
        data_synop, data_temp, accum_synop = self._get_data(self.ifiles_model)
        self.data_synop = data_synop
        self.data_temp = data_temp
        self.temp_stations = self._get_temp_station_list(self.data_temp)
        self.accum_synop = accum_synop

    def _get_temp_station_list(self,data_temp):
        ''' Extract the temp stations from the first row of data,
            which contains stationId lat lon height
        '''
        tempStations=OrderedDict()
        for date in data_temp.keys():
            if isinstance(data_temp[date], pd.DataFrame):
                tempStations[date] = [data_temp[date].iloc[0][0],data_temp[date].iloc[0][1],
                                      data_temp[date].iloc[0][2], data_temp[date].iloc[0][3]]
            else:
                tempStations[date] = [np.nan,np.nan,np.nan,np.nan]
        return tempStations

    def _get_data(self,ifiles):
        data_synop=OrderedDict()
        data_temp=OrderedDict()
        accum_synop =OrderedDict()
        for i,ifile in enumerate(ifiles):
            date=self.dates[i]
            data_synop[date], data_temp[date], accum_synop[date] = self._split_data(ifile,date)
            
        return data_synop, data_temp, accum_synop

    def _get_dates_from_files(self,ifiles):
        dates=[]
        for ifile in ifiles:
            if 'None' not in ifile:
                stuff,date=ifile.split('vfld'+self.model)
                dates.append(date)
            else:
                dates.append('None')
        return dates

    def _locate_files(self,model,period,finit,flen):
        #locate the files to process from each model.
        #period = YYYYMMDD_beg-YYYYMMDD_end
        #Shift the file name by -3 h if the model is tasii
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
                    else:
                        print("model %s not in in the data directory!"%model) 
                        
        return ifiles_model, dtgs

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

    def _split_data(self,ifile,date):
        '''
        Split the data files into SYNOP and TEMP data
        '''
        #data_synop= OrderedDict()
        cols_temp = ['PP','FI','TT','RH','DD','FF','QQ','TD']
        #data_temp= OrderedDict()
        header_temp=OrderedDict()
        if ifile != 'None':
            colnames, nsynop_stations, ignore_rows, ntemp_stations, accum_synop = self._get_synop_vars(ifile)
            data_synop = pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,
                    dtype=str,skiprows=ignore_rows,nrows=nsynop_stations)
            data_synop.columns=colnames
    
            ignore_temp=ignore_rows+data_synop.shape[0]+10
            data_temp =  pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,names=cols_temp,
                                      dtype=str,skiprows=ignore_temp)
        else:
            data_synop = 'None'
            data_temp = 'None'
            accum_synop = 'None'
    
        return data_synop, data_temp, accum_synop

class  monitor(object):
    '''
        Take dataframe with vfld data and format the
        rows and columns to write the whole thing to 
        a standard vfld ascii file that monitor can read
    '''

    def __init__(self, model=None, date=None,df_synop=None, df_temp=None, outdir=None):
        self.model = model #model to name the vfld file
        self.date=date
        self.df_synop = df_synop # pandas dataframe with synop data
        self.df_temp = df_temp # pandas dataframe with temp data
        self.outdir = outdir
        #self.date = date #date in format YYYYMMDDFINITHH
        self.df_out = self._format_data(df_synop,df_temp)
        
    def _format_data(self,df_synop,df_temp):
        '''
        Format the data to write in monitor vfld format.
        First create a dummy set of column names with the 
        same length as the length of the synop data.
        Then put below the info about
        ns_synop ns_temp version_4
        number_of_vars_synop
        list of vars from synop
        synopdata
        header temp
        temp data
        '''
        colst = df_temp.columns
        colss = df_synop.columns
        ns_synop = df_synop.shape[0]
        ns_temp = df_temp.shape[1]
        header_synop=[int(ns_synop), int(ns_temp), 4]
        df_out=pd.DataFrame(columns=colss) #dummy_cols) #
        if 'FI' in colss:
            nvars_synop = df_synop.shape[1]-3 # subtract stationId,lat,lon
            varlist_synop=colss[3:]  
            nvars=len(colss[3:])
        else:
            nvars_synop = df_synop.shape[1]-4 #subtract stationId,lat,lon,hh
            varlist_synop=colss[4:]  
            nvars=len(colss[4:])
        df_out=df_out.append({'stationId':header_synop[0],'lat':header_synop[1],'lon':header_synop[2]},ignore_index=True)
        df_out=df_out.append({'lat':nvars},ignore_index=True)
        for var in varlist_synop:
            df_out = df_out.append({'stationId':var},ignore_index=True)
        df_out = df_out.append(df_synop,ignore_index=True)    
        df_out = df_out.append({'stationId':11},ignore_index=True) #11 pressure levels (constant)
        df_out = df_out.append({'stationId':8},ignore_index=True) #8 variables for temp profiles (constant)
        for var in colst:
            df_out = df_out.append({'stationId':var},ignore_index=True)
        fill_these = ['stationId', 'lat', 'lon', 'FI', 'NN', 'DD', 'FF', 'TT']
        for i in enumerate(df_temp['PP'].values):
            print(i[0])
            collect_dict=OrderedDict()
            for k,col in enumerate(colst):
                collect_dict[fill_these[k]] = df_temp[col].values[i[0]]
            df_out = df_out.append(collect_dict,ignore_index=True)
     
        #import pdb
        #pdb.set_trace()
        return df_out
        #df_out = df_out.append(df_temp,ignore_index=True)    


    def write_vfld(self):
        ofile=os.path.join(self.outdir,''.join([self.model,self.date]))
        self.df_out.to_csv(ofile,sep=' ',header=False,index=False,na_rep='') #'-9999999999')


if __name__ == '__main__':
    models=[]
    #for model in ['tasii','sgl40h11']:
    #    models.append(
    model='tasii'
    period='20190601-20190630'
    finit='00,06,12,18'
    flen=52
    datadir='/data/cap/code_development_hpc/scripts_verif/merge_scripts/merge_vfld/example_data'
    #datadir='/netapp/dmiusr/aldtst/vfld'
    tasii = vfld_lite(model=model, period=period, finit=finit, flen=52, datadir=datadir)
    sgl40h11 = vfld_lite(model='sgl40h11', period=period, finit=finit, flen=52, datadir=datadir)
    #nuuk750 = vfld_lite(model='nuuk750', period=period, finit=finit, flen=52, datadir=datadir)
    qaan40h11 = vfld_lite(model='qaan40h11', period=period, finit=finit, flen=52, datadir=datadir)
    #models=[tasii, sgl40h11, nuuk750, qaan40h11]
    models=[tasii, sgl40h11, qaan40h11]
    date=tasii.dates[0]
    #print("data contents for %s"%date)
    #print("tasii")
    #print(tasii.data_synop[date])
    #print("sgl")
    #print(sgl40h11.data_synop[date])
    #print("nuuk")
    #print(nuuk750.data_synop[date])
    #print("qaan")
    #print(qaan40h11.data_synop[date])
    #print("merge synop data from all stations")
    frames_synop = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
    frames_temp = [f for f in models if isinstance(f.data_temp[date],pd.DataFrame)]
    #print("frames active ")
    #print([f.model for f in frames])
    #if tasii.dates[0] == sgl40h11.dates[0] == nuuk750.dates[0] == qaan40h11.dates[0]:
    dfs=[f.data_synop[date] for f in frames_synop]
    dft=[f.data_temp[date] for f in frames_temp]
    #print("frames to concatenate")
    #print(dfs[0])
    #print(dfs[1])
    #print(dfs[2])
    df_synop = pd.concat(dfs,sort=False)
    df_temp = pd.concat(dft)
    mon_save= monitor(model='gl',date=date,df_synop=df_synop,df_temp=df_temp,outdir=datadir)
    mon_save.write_vfld()
    #check=mon_save.write_vfld(df_synop,df_temp)

    #print("result")
    #print(df_row)

