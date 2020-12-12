# class that defines the vobs data set

import logging
import datetime
import os, sys
import numpy as np
import pandas as pd
import re
import csv
from collections import OrderedDict
logger = logging.getLogger(__name__)

class vobs(object):
    def __init__(self,period=None, datadir=None, model=None):
        self.model = model
        self.flen = 24 #always 24h for vobs
        self.ftimes=list(range(0,self.flen))
        self.period = period.split('-')
        self.datadir = datadir
        self.ifiles,self.dates = self._locate_files(self.datadir,self.period,self.flen)
        data_synop, data_temp, accum_synop = self._get_data(self.ifiles)
        self.data_synop = data_synop
        self.data_temp = data_temp
        self.accum_synop = accum_synop

    def _locate_files(self,datadir,period,flen):
        '''
        Locate the files to process
        period = YYYYMMDD_beg-YYYYMMDD_end
        '''
        date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
        date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
        dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
        str_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
        ifiles = []
        dtgs=[]

        for date in str_dates:
            for hour in range(0,flen):
                date_file = datetime.datetime.strptime(date,'%Y%m%d') + datetime.timedelta(seconds=3600*hour)
                date_file = datetime.datetime.strftime(date_file,'%Y%m%d%H')
                dtgs.append(date_file)
                fname=''.join(['vobs',date_file])
                ifile=os.path.join(datadir,fname)
                if os.path.exists(ifile):
                    ifiles.append(ifile)
                else:
                    ifiles.append('None')
        if (len(ifiles) == 0) or (len(set(ifiles)) == 1): # if all elements equal all None!
            logger.info(f"WARNING: no data found on {str_dates} for {self.model}")
            logger.info(ifiles)
        logger.debug("first file: %s"%(ifiles[0]))
        logger.debug("last file: %s"%(ifiles[-1]))
        return ifiles, dtgs

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
                logger.info("WARNING: no synop data for %s!"%(date))
                data_synop[date] = 'None'
            if len(data_temp[date]) == 0:
                logger.info("WARNING: no temp data for %s!"%(date))
                data_temp[date] = 'None'
        return data_synop, data_temp, accum_synop

    def read_synop(infile,varlist):
        rawData=pd.read_csv(infile,delimiter=" ")
        if 'FI' in varlist:
            columns = ['stationId','lat','lon'] + varlist
            rawData.columns=columns
            rawData=rawData.rename(columns={'FI': 'HH'})
        else:    
            columns=['stationId','lat','lon','HH']+varlist
            rawData.columns=columns
        if 'PE' in varlist:
            rawData=rawData.rename(columns={'PE':'PE1'})
        return rawData

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
            #NOTE 2: taking this back, since for the merging makes more sense
            #when writing the data in vfld format for monitor in vfld_monitor
            data_synop.columns=colnames
            #convert the station names to integer so as not to mix them with the 
            #short/long name convention used by CARRA and CERRA. Damn meteorologists follow their own conventions...          
            data_synop = data_synop.astype({'stationId': int})
            ignore_temp=ignore_rows+data_synop.shape[0]+10
            data_temp =  pd.read_csv(ifile,sep=r"\s+",engine='python',header=None,index_col=None,names=cols_temp,
                                      dtype=str,skiprows=ignore_temp)
        else:
            data_synop = 'None'
            data_temp = 'None'
            accum_synop = 'None'
    
        return data_synop, data_temp, accum_synop

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

    def _dates_2ftimes(self,period,flen):
        '''
        convert real dates to forecast times
        '''
        date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
        date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
        dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
        dtgs=[]
        str_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
        for date in str_dates:
            for init_hour in self.finit:
                for hour in range(0,flen):
                    dtgs.append(''.join([date[0:8],init_hour,str(hour).zfill(2)]))
        return dtgs            

    def merge_synop(dobs,dexp,var):
        '''
        merge the obs and vfld data
        '''
        #OBS data usually longer. Merge according
        # to this list.
        stnlist=dobs['stationId'].tolist()
        cols_sel=['stationId','lat','lon','HH',var]
        selOBS=dobs[['stationId','lat','lon','HH',var]]
        selEXP=dexp[['stationId','lat','lon','HH',var]]
        mergeOE = selOBS.merge(selEXP, on='stationId')
        #the result will contain vars with _x for OBS and _y for EXP
        return mergeOE

#--------------------------------------------------------

class vobs_format(object):
    '''
        Take dataframe with vobs data and format the
        rows and columns to write the whole thing to 
        a standard vobs format
    '''

    def __init__(self,  date=None,df_synop=None, df_temp=None, outdir=None):
        self.date=date
        self.df_synop = df_synop # pandas dataframe with synop data
        self.df_temp = df_temp # pandas dataframe with temp data
        self.outdir = outdir
        self.synop_cols = self.df_synop.columns
        self.df_out = self._format_data(df_synop,df_temp)
        
    def _format_data(self,df_synop,df_temp):
        '''
        Format the data to write in vobs format.
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

        #Since I read all in string format, only the 
        #strings not containing a . will be station names in the PP column
        temp_stations_PP=[st for st in df_temp['PP'].values if '.' not in st]
        ns_temp = len(temp_stations_PP)

        #declaring these values for header as strings is the only way I can ensure these numbers are written as non-float
        header_synop=[str(ns_synop), str(ns_temp), str(4)]
        df_out=pd.DataFrame(columns=colss) 
        if 'FI 0' in colss:
            nvars_synop = df_synop.shape[1]-3 # subtract: stationId,lat,lon
            varlist_synop=colss[3:]  
            nvars=len(colss[3:])
        else:
            nvars_synop = df_synop.shape[1]-4 #subtract stationId,lat,lon,hh
            varlist_synop=colss[4:]  
            nvars=len(colss[4:])
        #write first line of file:    
        df_out=df_out.append({'stationId':header_synop[0],'lat':header_synop[1],'lon':header_synop[2]},ignore_index=True)
        df_out=df_out.append({'lat':str(nvars)},ignore_index=True)
        for var in varlist_synop:
            df_out = df_out.append({'stationId':var},ignore_index=True)
        df_out = df_out.append(df_synop,ignore_index=True)    

        df_out = df_out.append({'stationId':str(10)},ignore_index=True) #10 pressure levels in vobs
        df_out = df_out.append({'stationId':str(8)},ignore_index=True) #8 variables for temp profiles (constant)
        for var in colst:
            df_out = df_out.append({'stationId':var+' 0'},ignore_index=True) #include accumulation time for temp vars
        fill_these = self.synop_cols[0:8]
        for i in enumerate(df_temp['PP'].values):
            collect_dict=OrderedDict()
            for k,col in enumerate(colst):
                collect_dict[fill_these[k]] = df_temp[col].values[i[0]]
            df_out = df_out.append(collect_dict,ignore_index=True)
        for col in df_out.columns:
            df_out[col].replace('None', '', inplace=True)
        return df_out


    def write_vobs(self):
        ofile=os.path.join(self.outdir,''.join(['vobs',self.date]))
        #the extra QUOTE_NONE is to avoid using extra "" in output for var names, and the escapechar 
        #so it won't complain about no escapechar unset
        self.df_out.to_csv(ofile,sep=' ',header=False,index=False,na_rep='',quoting=csv.QUOTE_NONE,quotechar='',escapechar=' ')


if __name__ == '__main__':
    period='20190601-20190601'
    datadir='/home/cap/data/from_ecmwf/codes/scripts_verif/contrib_verif/data/OBS'
    #vobs_data = vobs(period=period, datadir=datadir)
    #print(vobs_data.data_synop)
    #SYNOP: access data for a particular YYYYMMDDHH using vobs_data.data_synop[stringdate]
