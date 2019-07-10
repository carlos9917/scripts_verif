# script to convert vobs/vfld data to verif format

import datetime
import os, sys
import numpy as np
import pandas as pd
import re

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

def merge_synop(dobs,dexp,var):
    '''
    merge the obs and vfld data
    '''
    #OBS data usually longer. Merge according
    # to this list.
    stnlist=dobs['stationId'].tolist()
    #subEXP=dexp[dexp['stationId'].isin(stnlist)]
    #mergeEO=dexp.merge(dobs,how='right')#  on=['stationId'])
    #cols=dobs.columns.tolist()
    #cols=subEXP.columns.tolist()
    #mergeEO = dobs.merge(dexp.reset_index(), on=cols)
    #mergeEO = doexp.merge(dobs.reset_index(), on=cols_sel)
    #joinEO = dobs.join(other=subEXP,on=cols)#on=['stationId'])
    cols_sel=['stationId','lat','lon','HH',var]
    selOBS=dobs[['stationId','lat','lon','HH',var]]
    selEXP=dexp[['stationId','lat','lon','HH',var]]
    mergeOE = selOBS.merge(selEXP, on='stationId')
    #the result will contain vars with _x for OBS and _y for EXP
    return mergeOE


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
    units={'TT':'K','FF':'m/s'}
    #SYNOP
    var=args.variable
    inOBS=args.variables_vobs
    #NOTE: this one reads only the variables information
    vardata=np.loadtxt(inOBS,delimiter=' ',dtype=str)
    varlist=vardata[:,0].tolist()
    #then switch to Data
    inOBS=re.sub('Vars','Data',inOBS)
    dataOBS=read_synop(inOBS,varlist)

    #The info from the date comes from the file name
    path, fname = os.path.split(inOBS)
    datum=fname.split('_')[1]

    inEXP=args.variables_exp
    vardata=np.loadtxt(inEXP,delimiter=' ',dtype=str)
    varlist=vardata[:,0].tolist()
    #then switch to Data
    inEXP=re.sub('Vars','Data',inEXP)
    dataEXP=read_synop(inEXP,varlist)
    data=merge_synop(dataOBS,dataEXP,var)
    write_var(inOBS,var,units[var],data,datum)
    #TEMP
    #write_var(infile,var,'K',datum,data)



if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''If no argument provided, it will stop! 
             Example usage: script.py -v "T" -vvobs file_with_list_of_vobs -vexp file_with_list_of_vexp''',
                                                    formatter_class=RawTextHelpFormatter)

    parser.add_argument('-v',"--variable",
                        metavar='Variable to process',
                        type=str,
                        help='Variable to read and write',
                        default="TT",
                        required=False)

    parser.add_argument('-vvobs',"--variables_vobs",
                        metavar='File with the list of variables in the VOBS file',
                        type=str,
                        help='This file contains the variables list extracted from the original vobs file',
                        default=None,
                        required=True)

    parser.add_argument('-vexp',"--variables_exp",
                        metavar='File with the list of variables in the VFLD file',
                        type=str,
                        help='This file contains the variable list extracted from the original vfld file',
                        default=None,
                        required=True)
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)


