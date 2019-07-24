# merge two of the upscaled files
# The data from the stations of the first file replace the contents of the second file
import logging
import pandas as pd
import os
import sys
import glob
import fileinput
import datetime
import numpy as np
from collections import OrderedDict
import multiprocessing as mp
import csv


def main(args):

    file1 = args.file1
    file2 = args.file2
    ofile = args.ofile
    if ',' in file2:
        print("several files provided as input for second file")
        input_files = file2.split(',')
    else:
        input_files =  [file2]
    print ("check file2")
    print(input_files)
    #data from IGB:
    data1 = pd.read_csv(file1,sep=r"\s+",engine='python',header=None,index_col=None,skiprows=1,dtype=str)
    #read the first line of the file to add it later
    with open(file1) as f:
        first_line = f.readline()
    first_line=first_line.rstrip('\n')    

    varnames=['var'+str(i) for i in range(1,10)] # give the variables generic names.
    colnames= ['stationId','lat','lon','HH'] + varnames
    #data from SGL (and eventually tassilaq):
    for file2 in input_files:
        print("Replacing data from %s"%file2)
        #data2 = pd.read_csv(file2,sep=' ',engine='python',header=None,index_col=None,skiprows=1,dtype=str)
        data2 = pd.read_csv(file2,sep=r"\s+",engine='python',header=None,index_col=None,skiprows=1,dtype=str)
        data1.columns=colnames
        data2.columns=colnames
        #replace the stations in data1 with the stations in data2:
        for sindex,station in enumerate(data2.stationId):
            replace_index = data1.index[data1['stationId']==station]
            #print("Before change")
            #print(data1[data1['stationId'][:]==station])
            for var in colnames[3:]: #replaces all variables starting from HH
                print("Replacing variable %s"%var)
                data1[var][replace_index] = data2[var][sindex]

    data1.to_csv(ofile,sep=' ',header=False,index=False)
    # this one adds the header of the file:
    for line in fileinput.input(files=[ofile],inplace=True):
        if fileinput.isfirstline():
            print(first_line)
        line.rstrip('\n')    
        print(line.strip())

                      
if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Usually called from bash master script. Otherwise only one file is processed.
             Example usage: ./merge_ups.py file1 file2 fileout''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-f1','--file1',
                        metavar='file1',
                        type=str,
                        default=None,
                        required=True)

    parser.add_argument('-f2','--file2',
                        metavar='file2',
                        type=str,
                        default=None,
                        required=True)

    parser.add_argument('-fo','--ofile',
                        metavar='ofile',
                        type=str,
                        default=None,
                        required=True)


                          
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)

