# script to reduce the size of a vfld or vobs file.
# Need the input produced by splitvobs.sh:
# synop data/header in separate files
# Currently only doing the SURF part

import datetime
import os, sys
import numpy as np
import pandas as pd
import re
import csv
import fileinput

def read_synop(infile,varlist):
    rawData=pd.read_csv(infile,delimiter=" ")
    if 'FI' in varlist:
        columns = ['stationId','lat','lon'] + varlist
        rawData.columns=columns
        rawData=rawData.rename(columns={'FI': 'HH'})
    else:    
        columns=['stationId','lat','lon','HH']+varlist
        rawData.columns=columns
    #if 'PE' in varlist:
    #    rawData=rawData.rename(columns={'PE':'PE1'})
    return rawData

def filter_synop(data,stnlist):
    '''
    data: pd df read from read_synop.
    stnlist:  the list of stations I want to keep
    '''
    data_subset = data[data['stationId'].isin(stnlist)]
    return data_subset    

def read_temp(time,date):
    "Read the temp stations"

# open output file for writing the fcst/obs data for any variable
def write_var(infile,var,units,data,datum):
    leadtime = datum[8:10]
    date = datum[0:8]
    odir,fname=os.path.split(infile)
    odir,stuff = os.path.split(odir)
    ofile=os.path.join(odir,'synop_'+'_'.join([var,str(date)])+'.txt')
    exists = os.path.isfile(ofile)
    data['date'] = date
    data['leadtime'] = leadtime
    data['p0']=-999. #np.nan
    data['p11']=-999. #np.nan
    data['pit']=-999. #np.nan
    data=data.rename(columns={var+'_x': 'obs', var+'_y':'fcst',
        'lat_x':'lat','lon_x':'lon','HH_x':'altitude','stationId':'location'})
    data_write=data[['date','leadtime','location','lat','lon','altitude','obs','fcst','p0','p11','pit']]
    #import pdb
    #pdb.set_trace()
    if exists==True:
        #with open(ifile,'a') as f:
        #data_.to_csv(ofile)
        with open(ofile, 'a') as f:
            data_write.to_csv(f, header=False,index=False,sep=' ')
    else:
        with open(ofile,'w') as f:
            f.write('#variable %s\n' %(var))
            f.write('#units: $%s$\n' %(units))
            data_write.to_csv(f,sep=' ',index=False) 
        
def main(args):
    version_out=4
    #SYNOP
    inEXP=args.variables_exp #file with variables in vfld file
    stndata=pd.read_csv(args.station_list,sep=r"\s+",engine='python',header=None,index_col=None)
    stndata.columns=['lat','lon','stationId','incl']
    slat, slon, istnid,station_heights = stndata['lat'].values,stndata['lon'].values,stndata['stationId'].values, np.full(stndata['lat'].shape[0],-99.0)
    #The info from the date comes from the file name
    path, fname = os.path.split(inEXP)
    datum=fname.split('_')[1]
    #NOTE: this one reads only the variables information
    vardata=np.loadtxt(inEXP,delimiter=' ',dtype=str)
    varlist=vardata[:,0].tolist()
    varacct=vardata[:,1].tolist()
    #then switch to reading the Data
    inEXP=re.sub('Vars','Data',inEXP)
    dataEXP=read_synop(inEXP,varlist)
    dataNEW=filter_synop(dataEXP,istnid)
    #dataNEW.to_csv('test_check.dat',sep=' ',header=None,index=False,float_format='%2.3f',quoting=csv.QUOTE_NONE,escapechar=' ')

    #NOTE: used 4 decimal places to mimic the output saved in the vfld files.
    #Leading zero in station name should not be an issue, since output will be used by monitor
    newvfld='vfldnea40h11'
    odir,fname=os.path.split(inEXP)
    out_vfld=os.path.join(odir,newvfld+str(datum)+'_NEW.dat')
    dataNEW.to_csv(out_vfld,sep=' ',header=None,index=False,float_format='%2.4f')
    #write the header part:
    soffset=15
    column_variables=[]
    for i,var in enumerate(varlist[0:-1]):
        column_variables.append(var+' '*soffset+str(varacct[i])+'\n')
    column_variables.append(varlist[-1]+' '*soffset+str(varacct[-1]))    
    header_variables=''.join(column_variables)
    for line in fileinput.input(files=out_vfld,inplace=True):
        if fileinput.isfirstline():
            print(header_variables)
        print(line.strip())    
    n_s_inside = dataNEW.shape[0]
    extra_header=" "+str(n_s_inside)+"     0     "+str(version_out)+"\n"+" "*10+str(len(varlist))
    for line in fileinput.input(files=out_vfld,inplace=True):
        if fileinput.isfirstline():
            print(extra_header)
        print(line.strip())    

    #write_var(inOBS,var,units[var],data,datum)


if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''If no argument provided, it will stop! 
             Example usage: script.py -vvobs T -vexp T''',
                                                    formatter_class=RawTextHelpFormatter)
    #Not using this yet
    #parser.add_argument('-vvobs',"--variables_vobs",
    #                    metavar='File with variables in VOBS file',
    #                    type=str,
    #                    help='This file contains the variables list from VOBS data',
    #                    default=None,
    #                    required=True)

    parser.add_argument('-stn',"--station_list",
                        metavar='File with the list of stations I want to keep in new vfld file',
                        type=str,
                        help='This file contains the list of stations I want to keep',
                        default='./stncoord.dat', 
                        required=False)

    parser.add_argument('-vexp',"--variables_exp",
                        metavar='File with variables in VFLD file',
                        type=str,
                        help='This file contains the variable list from VFLD data',
                        default=None,
                        required=True)
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)


