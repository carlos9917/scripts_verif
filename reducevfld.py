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

def main(args):
    version_out=4
    #SYNOP
    inEXP=args.variables_exp #file with variables in vfld or vobs file
    model=args.exp_name
    ofile=args.output_file
    stndata=pd.read_csv(args.station_list,sep=r"\s+",engine='python',header=None,index_col=None)
    stndata.columns=['lat','lon','stationId','incl']
    slat, slon, istnid,station_heights = stndata['lat'].values,stndata['lon'].values,stndata['stationId'].values, np.full(stndata['lat'].shape[0],-99.0)
    #The info from the date comes from the file name
    path, fname = os.path.split(inEXP)
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
    #if model in ['nea40h11','EC9']:
    #    newvfld='vfld'+model
    #elif model == 'vobs':
    #    newvfld='vobs'
    #else:
    #    print('Model %s not known'%model)
    #    sys.exit()
    odir,fname=os.path.split(inEXP)
    dataNEW.to_csv(ofile,sep=' ',header=None,index=False,float_format='%2.4f')
    print("Writing to file %s"%ofile)
    #write the header part:
    soffset=15
    column_variables=[]
    for i,var in enumerate(varlist[0:-1]):
        column_variables.append(var+' '*soffset+str(varacct[i])+'\n')
    column_variables.append(varlist[-1]+' '*soffset+str(varacct[-1]))    
    header_variables=''.join(column_variables)
    for line in fileinput.input(files=ofile,inplace=True):
        if fileinput.isfirstline():
            print(header_variables)
        print(line.strip())    
    n_s_inside = dataNEW.shape[0]
    extra_header=" "+str(n_s_inside)+"     0     "+str(version_out)+"\n"+" "*10+str(len(varlist))
    for line in fileinput.input(files=ofile,inplace=True):
        if fileinput.isfirstline():
            print(extra_header)
        print(line.strip())    
    #TODO: add temp files at the end of the file (no filtering)
    #TEMP


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

    parser.add_argument('-ofile',"--output_file",
                        metavar='output vfld file',
                        type=str,
                        help='The file where I will write the reduced data',
                        default=None,
                        required=True)

    parser.add_argument('-stn',"--station_list",
                        metavar='File with the list of stations I want to keep in new vfld file',
                        type=str,
                        help='This file contains the list of stations I want to keep',
                        default='/home/cap/verify/scripts_verif/stncoord.dat', 
                        required=False)

    parser.add_argument('-vexp',"--variables_exp",
                        metavar='File with variables in VFLD or VOBS file',
                        type=str,
                        help='This file contains the variable list from VFLD or VOBS data',
                        default=None,
                        required=True)

    parser.add_argument('-model',"--exp_name",
                        metavar='Name of the experiment',
                        type=str,
                        help='Experiment name. If experiment name is vobs, then convert vobs files',
                        default=None,
                        required=True)
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)


