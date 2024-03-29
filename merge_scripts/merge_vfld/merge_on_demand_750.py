# Merge all the non-overlapping data from the 750 models:
#
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
# and the on_demand models
# sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand
#
# If the data is overlapping, then last model in the list
# will take precedence. See below for CLI arguments.
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
from vfld import vfld as vf
from vfld import vfld_monitor as monitor
import collections

#this to avoid issues with plotting via qsub
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)

def fill_hole(args,model,date,output_name,no_model=False):
    '''
    Fill any holes present when there is not enough models
    available to do a merge for a given date. Rules:
    For on_demand models, replace hole with available model (copy over the corresponding file and rename it as needed)
    For gl_hires, copy over the igb40h11 file for the date
    For gl_opr, copy over the igb40h11 file for the date
    '''
    logger = logging.getLogger(__name__)

    base_model='igb40h11'

    if output_name == 'gl_opr':
        logger.info("Filling hole in %s with IGB %s"%(date,base_model))
        ifile=os.path.join(args.vfld_dir+'/'+base_model,''.join(['vfld',base_model,date]))
        ofile=os.path.join(args.out_dir,''.join(['vfld',output_name,date]))
        if os.path.isfile(ifile):
            cmd='cp '+ifile+' '+ofile
            try:
                ret=subprocess.check_output(cmd,shell=True)
            except subprocess.CalledProcessError as err:
                logger.error('Error copying %s to %s')
        else:
            logger.info('%s does not exist!'%ifile)

    if output_name == 'gl_ondemand':
        logger.info("Filling hole in %s with file from %s"%(str(date),model))
        ifile=os.path.join(args.vfld_dir+'/'+model,''.join(['vfld',model,str(date)]))
        ofile=os.path.join(args.out_dir,''.join(['vfld',output_name,str(date)]))
        if os.path.isfile(ifile):
            cmd='cp '+ifile+' '+ofile
            try:
                ret=subprocess.check_output(cmd,shell=True)
            except subprocess.CalledProcessError as err:
                logger.error('Error copying %s to %s')
        else:
            logger.info('%s does not exist!'%ifile)

    if output_name == 'gl_hires':
        #gl_hires comes from the merge of gl_opr and gl_ondemand
        #if list of models is zero, this function is called with
        # the base_model name
        if model == 'igb40h11':
            logger.info("Special case for gl_hires. No models available. Using IGB")
        logger.info("Filling hi_res hole in %s with %s"%(date,model))
        ifile=os.path.join(args.vfld_dir+'/'+model,''.join(['vfld',model,str(date)]))
        ofile=os.path.join(args.out_dir,''.join(['vfld',output_name,str(date)]))
        if os.path.isfile(ifile):
            cmd='cp '+ifile+' '+ofile
            try:
                ret=subprocess.check_output(cmd,shell=True)
            except subprocess.CalledProcessError as err:
                logger.error('Error copying %s to %s')
        else:
            logger.info('%s does not exist!'%ifile)


    if output_name not in ['gl_opr','gl_hires','gl_ondemand']:
        logger.info("Model is %s. Doing nothing"%model)



def save_unavail(models,date,outdir,period,output_name):
    '''
    Write out dates with not enough models.
    This is just for debugging purposes
    '''
    fout=os.path.join(outdir,'_'.join(['only_one_present',period,output_name])+'.log')
    for model in models:
        if os.path.isfile(fout):
            with open(fout,'a') as f:
                f.write("%s %s \n"%(model,date))
        else:
            with open(fout,'w') as f:
                f.write("#model date\n")
                f.write("%s %s \n"%(model,date))

def check_frames_synop(models_data,date):
    '''
    check if there's synop data for this date for all models
    '''
    frames_synop = []
    for m in models_data.keys():
        if date in models_data[m].dates:
            if isinstance(models_data[m].data_synop[date],pd.DataFrame):
                frames_synop.append(models_data[m])
    return frames_synop        

def check_frames_temp(models_data,date):
    '''
    check if there's temp data for this date for all models
    '''
    frames_temp=[]
    for m in models_data.keys():
        if date in models_data[m].dates:
            if isinstance(models_data[m].data_temp[date],pd.DataFrame):
                frames_temp.append(models_data[m])
    return frames_temp

def drop_duplicates(df_temp):
    '''
    Drop duplicate stations in the df_temp frame.
    '''
    #identify the station names
    temp_stations=[st for st in df_temp['PP'].values if '.' not in st]
    #idenfity the index of each station
    temp_st_loc=[df_temp.loc[df_temp['PP']==st].index for st in df_temp['PP'] if '.' not in st]
    #repeated stations:
    repeated =[item for item, count in collections.Counter(temp_stations).items() if count > 1]
    to_del=[]
    for st in repeated:
        check_ind=df_temp.loc[df_temp['PP']==st].index.tolist()
        for ch in check_ind[1:]: # keep only first 
            to_del = to_del + list(range(ch,ch+11))
    if len(to_del) != 0:        
        df_temp.drop(to_del,inplace=True)


def check_plot(df,fout):
    import seaborn as sns
    dfp=df.astype(float)
    #ax=dfp.plot(x='lon',y='lat',style='o')
    sns_plot=sns.scatterplot(x="lon", y="lat", data=dfp)
    #fig = ax.get_figure()
    #fig.savefig(fout)
    sns_plot.figure.savefig(fout)


def setup_logger(logFile,outScreen=False):
    '''
    Set up the logger output
    '''
    global logger
    global fmt
    global fname

    logger = logging.getLogger(__name__)
    fmt_debug = logging.Formatter('%(levelname)s:%(name)s %(message)s - %(asctime)s -  %(module)s.%(funcName)s:%(lineno)s')
    fmt_default = logging.Formatter('%(levelname)-8s:  %(asctime)s -- %(name)s: %(message)s')
    fmt = fmt_default
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fname = logFile
    fh = logging.FileHandler(fname, mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    if outScreen:
        logger.addHandler(ch) # Turn on to also log to screen

def main(args):

    try:
        os.makedirs(args.out_dir)
    except OSError:
        print("%s directory already exists!"%args.out_dir)

    period = args.period    
    outdir  = args.out_dir
    datadir = args.vfld_dir
    flen    = args.flen
    merge_type = args.merge_type
    output_name = args.output_name
    if ',' in args.merge_models:
        mmodels = args.merge_models.split(',')
    else:
        print("Please provide more than one model: %s"%arg.merge_models)
        print("Format: 'model1,model2...'")
        sys.exit()

    logFile=os.path.join(outdir,args.log_file)
    print("All remaining screen output will be written to %s"%logFile)
    setup_logger(logFile,outScreen=False)
    

    #read data for each model
    models = mmodels
    #This dictionary if for checking available data
    merged_models=OrderedDict()
    merged_models['available date']=np.array([])

    #models=["tasii", "sgl40h11", "nuuk750", "qaan40h11",
    #        "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" ]
    #
    models_data=OrderedDict()

    for model in models:
        models_data[model] = vf(model=model, period=period, flen=flen, datadir=datadir, stream='DMI')
        logger.info("Data for "+model+" loaded")
        #print("will store model %s"%model)
        merged_models[model] = np.array([]) #this for bookkeepimg later on
        #print("passed model")

    #now merge the whole data. Choose a model that will contain all dates!
    #Using the last model, since this will be the one setting the order in overlapping models
    logger.info("Looping through dates from model %s"%models[-1])
    for date in models_data[models[-1]].dates:
        logger.info("Attempting to merge date %s"%date)
        #Only collect those dates which contain any data:
        #frames_synop = [models_data[m] for m in models_data.keys() if isinstance(models_data[m].data_synop[date],pd.DataFrame)]
        frames_synop = check_frames_synop(models_data,date)
        models_avail = [f.model for f in frames_synop]
        logger.info("Number of models with synop data for %s: %d"%(date,len(frames_synop)))
        if len(frames_synop) < 2:
            logger.info("Merge failure: not enough models available (%d)"%len(frames_synop))
            if len(models_avail) == 1:
                save_unavail(models_avail,date,outdir,period,output_name)
                fill_hole(args,models_avail[0],date,output_name)
            elif len(models_avail) == 0 and output_name == 'gl_hires':
                fill_hole(args,'igb40h11',date,output_name)
            else:
                logger.info("Jumping to next date")
            continue
        else:
            logger.info("Available models: %s"%' '.join(models_avail))
            # The following will be written to disk as a list of
            # available models
            for this_model in models_avail:
                merged_models[this_model] = np.append(merged_models[this_model],'Present')
            for this_model in merged_models.keys():
                if this_model not in models_avail and this_model != 'available date':
                    merged_models[this_model] = np.append(merged_models[this_model],'Missing')
            merged_models['available date'] = np.append(merged_models['available date'],date)
                
        #frames_temp = [models_data[m] for m in models_data.keys() if isinstance(models_data[m].data_temp[date],pd.DataFrame)]
        frames_temp=check_frames_temp(models_data,date)
        #collect all frames with data for this date to concatenate afterwards
        dfs=[f.data_synop[date] for f in frames_synop]
        dft=[f.data_temp[date] for f in frames_temp]

        if len(dfs) >= 2:
            if merge_type == 'overlap':
                logger.info("Overlapping models. Keeping SYNOP data from %s if stations repeated"%models[-1])
                df_synop = pd.concat(dfs,sort=False)
                df_synop = df_synop.drop_duplicates(['stationId'],keep='last') #keeping last model
                logger.info("Passed SYNOP")
            elif merge_type == 'nonoverlap':
                logger.info("Non-overlapping models. Keeping all SYNOP data")
                df_synop = pd.concat(dfs,sort=False)
            else:
                logger.error("Wrong option for merge_type: %s"%merge_type)
                logger.error("Exit program")
                sys.exit()
        else:
            logger.info("Not enough data for df_synop: %d"%len(dfs))
            df_synop = pd.DataFrame(columns = ['a','b','c']) #empty dataframe


        if len(dft) >= 2:
            if merge_type == 'overlap':
                logger.info("Overlapping models. Keeping TEMP data from %s if stations repeated"%models[-1])
                df_temp = pd.concat(dft,ignore_index=True)
                drop_duplicates(df_temp) #NOTE: this is an internal function! Not pandas
                logger.info("Passed TEMP")
            elif merge_type=='nonoverlap':
                logger.info("Non-overlapping models. Keeping all TEMP data")
                df_temp = pd.concat(dft)
            else:
                logger.error("Wrong option for %s"%merge_type)
                logger.error("Exit program")
                sys.exit()
        elif len(dft) == 1:
            logger.info("Only one model has data for df_temp: %d"%len(dft))
            df_temp = pd.concat(dft) #,ignore_index=True)
        else:    
            logger.info("Not enough data for df_temp: %d"%len(dft))
            df_temp = pd.DataFrame(columns = ['a','b','c']) #empty dataframe

        if not df_synop.empty and not df_temp.empty:
            logger.info("Writing the data (df_synop.size:%d, df_temp.size:%d)"%(df_synop.size,df_temp.size))
            mon_save= monitor(model=output_name,date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
            mon_save.write_vfld()
            del mon_save
            del df_synop
            del df_temp
        else:
            logger.info("SYNOP data available for only %d model. No merging done"%len(dfs))
            logger.info("TEMP data available for only %d model. No merging done"%len(dft))
    #write list of models for debugging
    #print("before the evaluation")
    if len(merged_models) > len(models_avail)+1:
        fout=os.path.join(outdir,'_'.join(['models_available',period,output_name])+'.log')
        logger.info("Writing model availability to %s"%fout)
        write_models_merged=pd.DataFrame(merged_models,columns=merged_models.keys())
        write_models_merged.to_csv(fout,sep=' ',index=False)
    else:
        logger.info("No matching data available for this period")


    logger.info("Merging done")
if __name__ == '__main__':
    #NOTE: limit period to 1 month at a time.
    # Otherwise the class will become huge!

    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''Combine all Greenland 750 m vfld data
                        Example usage: python merge_on_demand_750.py -pe 20190101-20190101 -fl 52 -dvfl /netapp/dmiusr/aldtst/vfld -dout /home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl ''',formatter_class=RawTextHelpFormatter)

    parser.add_argument('-pe','--period',metavar='Period to process (YYYYMMDD-YYYYMMDD)',
                                type=str, default='20190101-20190101', required=False)
    parser.add_argument('-fl','--flen',metavar='Forecast length (HH)',
                                type=int, default=52, required=False)
    #parser.add_argument('-fi','--finit',metavar='Forecast init times. One value or list separated by commans (00,06,12,18)',type=str, default='00,06,12,18', required=False)

    parser.add_argument('-dvfl','--vfld_dir',metavar='Path of the vfld directory',
                                type=str, default='/netapp/dmiusr/aldtst/vfld', required=False)
    parser.add_argument('-dout','--out_dir',metavar='Path of the output directory',
                                type=str, default='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl', required=False)
    parser.add_argument('-mm','--merge_models',metavar='List of models I want to merge. String separated by commas',
                                type=str, default='tasii,sgl40h11', required=False)
    parser.add_argument('-mt','--merge_type',metavar='Merge type: overlap or nonoverlap. If overlap, last model on the list takes precedence',
                                type=str, default='nonoverlap', required=False)
    parser.add_argument('-on','--output_name',metavar='Output name. The string to be used after vfld in the name files',
                                type=str, default=None, required=True)

    parser.add_argument('-lg','--log_file',metavar='Log file name',
                                type=str, default='merge.log', required=False)
    args = parser.parse_args()


    try:
        print("Arguments: %s"%args)
        main(args)
    except:
        print("Error. Exiting")
        parser.print_help()
        sys.exit(0)
 
