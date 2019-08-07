# Merge all the non-overlapping data from the 750 models:
#
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
#
# The aim is to combine all the data produced by the 750 models
# in one file named vfldgl750_*
# Two options here:
# non-overlapping (default): domains don't overlap, hence they all contain different stations
# overlapping: domains share some stations. In this case the priority of
# one model over another must be set
#
# The data is assumed to be split into SYNOPVar/Data and TEMPVar/Data
# as in the merge_models750_IGB.py script
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

def get_synop_vars(ifile):
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

def locate_files(models,period,finit,flen):
    #locate the files to process from each model.
    #period = YYYYMMDD_beg-YYYYMMDD_end
    #Shift the file name by -3 h if the model is tasii
    #tdate=datetime.datetime.strptime('2019081200','%Y%m%d%H')-datetime.timedelta(seconds=10800)
    #datadir='/netapp/dmiusr/aldtst/vfld'
    #datadir='/data/cap/code_development_hpc/scripts_verif/merge_scripts/merge_vfld/example_data'
    date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
    date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
    dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
    model_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
    #hours=[hour for hour in range(0,flen)]
    ifiles_model=OrderedDict()
    for model in models:
        ifiles_model[model] = []

    for date in model_dates:
        for init_hour in finit:
            for hour in range(0,flen):
                for model in models:
                    if model != 'tasii':
                        fname=''.join(['vfld',model,date,init_hour,str(hour).zfill(2)])
                        fdir='/'.join([datadir,model])
                        ifile=os.path.join(fdir,fname)
                        if os.path.exists(ifile):
                            ifiles_model[model].append(ifile)
                        else:
                            ifiles_model[model].append('None')
                    elif model == 'tasii':
                        dtgtas=datetime.datetime.strptime(date+init_hour,'%Y%m%d%H') - datetime.timedelta(seconds=10800)
                        dtgtas = datetime.datetime.strftime(dtgtas,'%Y%m%d%H')
                        hour3=str(hour+3).zfill(2)
                        fname=''.join(['vfld',model,dtgtas,hour3])
                        fdir='/'.join([datadir,model])
                        ifile=os.path.join(fdir,fname)
                        if os.path.exists(ifile):
                            ifiles_model[model].append(ifile)
                        else:
                            ifiles_model[model].append('None')
                    else:
                        print("model %s not in in the data directory!"%model) 
                        
    return ifiles_model    

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
        colnames, nsynop_stations, ignore_rows, ntemp_stations, accum_synop = get_synop_vars(ifile)
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


def combine_nonoverlapping(input_files):
    #combine non-overlapping data. In this case
    #simply combine all the data in one file
    models_data=OrderedDict()
    nsynop_total=0
    ntemp_total=0
    #for k,model in enumerate(input_files.keys()):
        #pile_synop[model] = []
    #all input files ordered by date.
    #loop below assumes all files contain the same number of synop variables
    #this should be the case for all models, since we are dealing with vfld
    #and not vobs data
    pile_synop=OrderedDict()
    models=list(input_files.keys())
    for k,ifile in enumerate(input_files[models[0]]): 
        if ifile != 'None':
            print("first model data exists: %s"%ifile)
            data_synop,data_temp,accum_synop=split_data(models[0], ifile)
            
            save_cols=list(data_synop[models[0]].keys())
            #pile_synop[model].append(data_synop)
            pile_synop[models[0]]=data_synop
            save_synop=OrderedDict() #{}
            save_temp=OrderedDict() #{}
            nkeys=len(data_synop[models[0]].keys())
            print("contains %d synop variables (includes lat,lon,stationid)"%nkeys)
            print(data_synop[models[0]].keys())
            for key in data_synop[models[0]].keys():
                save_synop[key]=list(data_synop[models[0]][key])

            for key in data_temp[models[0]].keys():
                save_temp[key]=list(data_temp[models[0]][key])

            df_synop=pd.DataFrame.from_dict(save_synop)
            df_temp=pd.DataFrame.from_dict(save_temp)
        else:
            print("Data for model %s  not available"%models[0])
            df_synop=pd.DataFrame()
            df_temp=pd.DataFrame()
            accum_synop=None

        for model in models[1:]:
            print(model)
            this_file=input_files[model][k]
            #print(this_file)
            if this_file != 'None':
                save_file=this_file
                save_model=model
                print("Adding data from model %s"%(this_file))
                #ignore accum times for this set now, since I stored them above
                data_synop,data_temp,stuff=split_data(model, this_file)
                nkeys=len(data_synop[model].keys())
                print("contains %d synop variables (includes lat,lon,stationid)"%nkeys)
                print(data_synop[model].keys())
                pile_synop[model]=data_synop
                save_synop=OrderedDict() #{}
                save_temp=OrderedDict() #{}
                for key in data_synop[model].keys():
                    save_synop[key]=list(data_synop[model][key])

                for key in data_temp[model].keys():
                    save_temp[key]=list(data_temp[model][key])

                df_add=pd.DataFrame.from_dict(save_synop)
                df_synop = df_synop.append(df_add)
                df_add=pd.DataFrame.from_dict(save_temp)
                df_temp = df_temp.append(df_add)

        if (not df_temp.empty) and (not df_synop.empty):
            print("Writing data for this date")
            df_synop = df_synop.reset_index(drop=True) 
            df_temp = df_temp.reset_index(drop=True)    
            outdir='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld'
            ofile=os.path.split(save_file)[-1].replace(save_model,'gl750')
            ofile=os.path.join(outdir,ofile)
            df_synop.fillna('-9999999999',inplace=True)
            #df_temp.fillna('-9999999999',inplace=True)
            df_temp=df_temp.replace('None','') #,regex=True)
            df_synop.to_csv(ofile,sep=' ',header=False,index=False,columns=save_cols)

            #now add the header for the synop data:
            vars_synop=df_synop.columns

            df_temp.to_csv(ofile,sep=' ',mode='a',header=False,index=False,na_rep='-9999999999')
            import pdb
            pdb.set_trace()

            #data =  pd.read_csv(ifileData,sep=r"\s+",engine='python',header=None,index_col=None,dtype=str)

        #ifileVars = ifileData.replace('Data','Vars')
        #colnames, col_start= get_vars(ifileVars)
        #data.columns=colnames
        #models_data[model] =  data #save data in dict
        ##read the first line to determine the variables inside
        #with open(ifileVars) as f:
        #    first_line = f.readline()
        #first_line=first_line.rstrip('\n')    
        #header_line=first_line.split()
        #nsynop=int(header_line[0]) #number of synop stations
        #ntemp=int(header_line[1]) #number of temp stations
        #print("Number of nsynop and ntemp stations in %s file: %d, %d"%(ifile,nsynop,ntemp))

def writesynop_nonoverlapping(data):
    pass

def writesynop_overlapping():
    print("In construction")
    sys.exit()

def writetemp_nonoverlapping(data,ofile):
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
    with open(ofile,'a') as f:
        with open(fileIGB_temp) as tfile:
            lines_read=tfile.read()
            f.write(lines_read)

def main(args):
    #datadir='/netapp/dmiusr/aldtst/vfld'
    #files750 = args.files750_synop
    models750= args.models750
    input_models = models750.split(',')
    print("models to merge")    
    print(input_models)
    period = args.merge_period.split('-')
    print("period:")
    print(period)
    finit=args.init_hours.split(',')
    flen=args.forecast_length
    #calculate all dates in format YYYYMMDDHH I need to read
    #and return list of files I will have to process
    input_files = locate_files(input_models,period,finit,flen)
    if args.overlapping == False:
        print("Combining models that do not overlap")
        print("Warning: no check on duplicate stations will be carried out!")
        #data=split_data(input_models,input_files)
        data,header = combine_nonoverlapping(input_files)
        #writesynop_nonverlapping(data,header)
        #writetemp_nonoverlapping(ofile)
    elif args.overlapping == True:
        data,header = replace_overlapping(input_files)
    else:
        print("-ov option must be True or False (default)")
        sys.exit()

                      
if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
             Example usage: ./merge_750models_IGB.py -f750 tasiifile,sgl40h11file -fo fileout''', formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('-ihours','--init_hours',
                        metavar='init hours of the forecast each day (separate by commas), format HH',
                        type=str,
                        default='00,06,12,18',
                        required=False)

    parser.add_argument('-flen','--forecast_length',
                        metavar='forecast length in hours HH',
                        type=int,
                        default=52,
                        required=False)

    parser.add_argument('-period','--merge_period',
                        metavar='Period to convert in format: date1-date2, with date=YYYYMMDD',
                        type=str,
                        default=None,
                        required=True)

    parser.add_argument('-mod','--models750',
                        metavar='models to merge. Separate them with a comma',
                        type=str,
                        default='tasii,sgl40h11,nuuk750,qaan40h11',
                        required=False)

    parser.add_argument('-ov','--overlapping',
                        metavar='model domains overlap.',
                        type=str,
                        default=False,
                        required=False)

                          
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    main(args)

