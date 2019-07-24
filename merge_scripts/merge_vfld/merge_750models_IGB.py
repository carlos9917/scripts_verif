# Merge all the non-overlapping data from the 750 models:
# tasii and sgl40h11
# (eventually need to add: qaan40h11)
# with the data from IGB
#
# The aim is to replace all the data produced by the 750 models
# at the stations considered by IGB
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

def get_vars(fileVars):
    #Read this file to determine number of variables in file:
    first_two=[]
    with open(fileVars) as f:
        first_two.extend(str(f.readline()).rstrip() for i in range(2))
    nsynop=int(first_two[-1])
    lines_header =[]
    with open(fileVars) as f:
            lines_header.extend(f.readline().rstrip() for i in range(nsynop+2))
    vars_synop=[i.split(' ')[0] for i in lines_header[2:]]
    if 'FI' in vars_synop:
        colnames= ['stationId','lat','lon'] + vars_synop
        start_col_replace = 3
    else:
        colnames=['stationId','lat','lon','HH'] + vars_synop
        start_col_replace = 4
    return colnames, start_col_replace

def main(args):

    fileIGB = args.fileIGB_synop
    files750 = args.files750_synop
    ofile = args.ofile
    fileIGBVars = fileIGB.replace('Data','Vars')
    fileIGB_temp = fileIGB.replace('synop','temp')
    localdir=os.getcwd()
    if ',' in files750:
        print("several files provided as input for second file")
        input_files = files750.split(',')
    else:
        input_files =  [files750]
    print("750 m input files to include ")    
    print(input_files)
    data1 = pd.read_csv(fileIGB,sep=r"\s+",engine='python',header=None,index_col=None,dtype=str)# kiprows=nsynop+2,dtype=str)
    colnamesIGB, col_start_IGB= get_vars(fileIGBVars)
    data1.columns=colnamesIGB
    #read the first line of the file to add it later
    with open(fileIGBVars) as f:
        first_line = f.readline()
    first_line=first_line.rstrip('\n')    
    igb_line=first_line.split()
    igb_ntemp=int(igb_line[1])
    print("Number of ntemp stations in IGB file %d"%igb_ntemp)

    #data from SGL (and eventually tassilaq):
    for file2 in input_files:
        file2Vars=file2.replace('Data','Vars')
        #I don't want to change the start of column counting here
        colnames, col_start_file2 = get_vars(file2Vars)
        print("Replacing data from %s in %s"%(file2,fileIGB))
        data2 = pd.read_csv(file2,sep=r"\s+",engine='python',header=None,index_col=None,dtype=str) #,skiprows=nsynop+2,dtype=str)
        data2.columns=colnames
        with open(file2Vars) as f:
           read_line = f.readline()
        check_line=read_line.split()
        #igb_ntemp = igb_ntemp + int(check_line[1]) # increase the count of temp stations for each new file
        #replace the stations in data1 with the stations in data2:
        #NOTE: Replaces only the variables already in IGB file!
        #No new variables are added
        for sindex,station in enumerate(data2.stationId):
            replace_index = data1.index[data1['stationId']==station]
            for var in colnamesIGB[col_start_IGB:]: #replaces all variables starting this column
                #print("Replacing variable %s"%var)
                data1[var][replace_index] = data2[var][sindex]
    #DONOT UPDATE!!! ONly include the original IGB stations
    #igb_line[1]=str(igb_ntemp) # update the igb first line with the new number of temp stations
    first_line = ' '.join(igb_line) #create the first line
    data1.to_csv(ofile,sep=' ',header=False,index=False)

    print("Number of ntemp stations after loop %d"%igb_ntemp)

    #read the header again to include at the beginning
    with open(fileIGBVars) as f:
        all_lines = f.readlines()[1:] #ignore first line. It will be added later
    all_lines[-1] = all_lines[-1].rstrip()    
    first_header=''.join(all_lines)
    #do the following to add a blank space before the var name.
    #monitor might be picky about these blank spaces!
    reformat=[]
    for comp in re.split("(\n)", first_header):
        if comp != '\n':
            comp='   '+comp
            reformat.append(comp)
        else:
            reformat.append(comp)
    first_header=' '.join(reformat)
    #add this part:
    for line in fileinput.input(files=[ofile],inplace=True):
        if fileinput.isfirstline():
            print(first_header)
        #line.rstrip('\n')    
        print(line.strip())
    # this one adds the first line of the file:
    first_line = ' '+first_line # Add an extra space to comply with read_vobs_temp expected format
    for line in fileinput.input(files=[ofile],inplace=True):
        if fileinput.isfirstline():
            print(first_line)
        line.rstrip('\n')    
        print(line.strip())

    #Assumming this one doesn't change!!!  
    temp_header= '''          11
           8
 PP           0
 FI           0
 TT           0
 RH           0
 DD           0
 FF           0
 QQ           0
 TD           0
'''
    with open(ofile, 'a') as f:
        f.write(temp_header)
    # this one adds the footer of the file with the data from the temp files
    # NOTE: only the original data from IGB is written here!!
    temp_files = [i.replace('synop','temp') for i in input_files]
    #all_files=[fileIGB_temp] + temp_files
    #for ifile in all_files:
    #print("temp file to process %s"%ifile)
    with open(ofile,'a') as f:
        #with open(ifile) as tfile:
        with open(fileIGB_temp) as tfile:
            lines_read=tfile.read()
            #print("lines to write %s"%lines_read)
            #f.write(tfile.read())
            f.write(lines_read)

                      
if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
             Example usage: ./merge_750models_IGB.py -fIGB IGBfile -f750 tasiifile,sgl40h11file -fo fileout''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-fIGB_synop','--fileIGB_synop',
                        metavar='file with IGB data',
                        type=str,
                        default=None,
                        required=True)

    #parser.add_argument('-fIGB_temp','--fileIGB_temp',
    #                    metavar='file with IGB data',
    #                    type=str,
    #                    default=None,
    #                    required=True)

    parser.add_argument('-f750_synop','--files750_synop',
                        metavar='file(s) with 750 m data. Separate several files with a comma',
                        type=str,
                        default=None,
                        required=True)

    #parser.add_argument('-f750_temp','--files750_temp',
    #                    metavar='file(s) with 750 m data. Separate several files with a comma',
    #                    type=str,
    #                    default=None,
    #                    required=True)

    parser.add_argument('-fo','--ofile',
                        metavar='Output file',
                        type=str,
                        default=None,
                        required=True)

                          
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)

