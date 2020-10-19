'''
Script to check which streams are available
or missing data
'''
import sys
import os
import glob
import fnmatch
import subprocess
from datetime import datetime
from datetime import timedelta
import numpy as np
from collections import OrderedDict
from finaldate import lastday

def check_streams_availability(dom,period,datadir):
     ''' 
     check if all files that should be available for the merge of
     IGB and NE domains are indeed available
     '''
     flen=31
     #init times: 00 and 12. Forecast hours expected from 0-30. Every 1h until 6, then every 3 h
     #init times: 03,06,09,15,18,21. Forecast hours expected from 0-3. Every 1h.
     fhours_long=[str(i).zfill(2) for i in range(0,7)] + [str(i).zfill(2) for i in range(9,flen,3)]
     fhours_short=[str(i).zfill(2) for i in range(0,4)]
     init_expected = [str(i).zfill(2) for i in range(0,22,3)]
     period = period.split('-')
     date_ini=datetime.strptime(period[0],'%Y%m%d')
     date_end=datetime.strptime(period[1],'%Y%m%d')
     dates = [date_ini + timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
     model_dates=[datetime.strftime(date,'%Y%m%d') for date in dates]
     domain='_'.join(['carra',dom])
     vflddir=os.path.join(datadir,domain)
     print(f"Searching {vflddir}")
     dates_found=[]
     yyyymm=period[0][0:6]
     print(f'Gonna search in {vflddir} for {yyyymm}')
     for ifile in sorted(os.listdir(vflddir)): #TODO: need to refine search below. 
                                       # Only matching the YYYYMM of first date!
                                       #OK for same month, since usually running
                                       #one month at a time
         if fnmatch.fnmatch(ifile, 'vfld*'+yyyymm+'*'):
             this_date=''.join([n for n in ifile if n.isdigit()])
             #print(f"found file {ifile}")
             dates_found.append(this_date)
     #print(f'Preliminary number of files found: {len(dates_found)}')
     dtg_expected=[]
     for date in model_dates:
         for init in init_expected:
             if init in ['00', '12']:
                 for hour in fhours_long:
                     dtg_expected.append(''.join([date,init,str(hour).zfill(2)]))
             else:
                 for hour in fhours_short:
                     dtg_expected.append(''.join([date,init,str(hour).zfill(2)]))
     dates_pass=[]
     dates_miss=[]
     for dtg in dtg_expected:
         if dtg in dates_found:
             dates_pass.append(dtg)
         else:
             dates_miss.append(dtg)
     #print(f'After:  {len(dates_pass)}')
     return dtg_expected, dates_pass, dates_miss

def read_current_state(hfile,period,stream_number):
    '''
    Attempts to read current state through html file printed daily.
    Output dtgs that must be available for this period and stream_number
    It uses only the NE streams for checking for end dates
    '''
    import bs4 as bs
    from bs4 import BeautifulSoup
    cols=['expId','Current assimilated date','End date of stream',
          'Completion date', 'Avg. throughput (7d)',
          'Avg. throughput (30d)']
    f = open(hfile,'r') #'/home/cap/current_state_sims.html', 'r')
    s=f.read()
    soup = BeautifulSoup(s,"lxml")
    table=soup.find('table')
    trows=table.find_all('tr')
    min_dtg={}
    dom_edate=OrderedDict()
    for i in range(1,4):
        dom_edate[str(i)]=np.array([])
    for tr in trows[1:]:
        td = tr.find_all('td')
        row = [i.text for i in td]
        dom=row[0].split('_')[1]
        num=row[0].split('_')[2]
        date1=datetime.strptime(row[1],"%Y%m%d%H")
        #print(row[0])
        if 'B' not in num and dom != 'IGB': #ignore the additional streams for IGB
            if '*' in num: #an asterisk will appear in table sometimes
                num = num.replace('*','')
            if '**' in num: #an asterisk will appear in table sometimes
                num = num.replace('**','')
            if '***' in num: #an asterisk will appear in table sometimes
                num = num.replace('***','')
            dom_edate[num] = np.append(dom_edate[num],date1)
        #print(f"num is {num} and dom {dom}")
        #cur_dtg[row[0]]=row[1]
        #end_dtg[row[0]]=row[2]
    period = period.split('-')
    date_ini= datetime.strptime(period[0],'%Y%m%d')
    date_end= datetime.strptime(period[1],'%Y%m%d')
    period_avail=False
    #using beg/end dates from stream NE 1, since I only consider 3 streams here
    beg_dates=['19960701','20050901','20130901']
    end_dates=['20060831','20140831','20210630']
    dtg_end={}
    dtg_beg={}
    for i in range(1,4):
        dtg_beg[str(i)]=datetime.strptime(beg_dates[i-1],'%Y%m%d')
        dtg_end[str(i)]=datetime.strptime(end_dates[i-1],'%Y%m%d')
    #determine to which stream the current period belongs to     
    for key in dom_edate.keys():
        print(f'Checking key extracted from html file {key}')
        min_dtg[key] = datetime.strftime(min(dom_edate[key]),'%Y%m%d')
        if min(dom_edate[key]) >= date_end and key==stream_number:
        #if min(dom_edate[key]) >= dtg_beg[key] and min(dom_edate[key]) <= dtg_end[key]:
        #if dtg_beg[key] <= min(dom_edate[key]) and dtg_end[key] >= min(dom_edate[key]):
            print(f'Found this {dom_edate[key]} with end date {date_end}')
            period_avail=True
            print(f"The last available date for stream {stream_number} is {min_dtg[key]}")
    return min_dtg, period_avail

def sbatch_ecfs(sname,sfile,cmd,submit):
    text='''#!/bin/bash 
# >>>>>>> To be submitted from ecgate <<<<<<<<
#SBATCH --error=/scratch/ms/dk/nhd/tmp/carra_temp/out/sbatch-%J.err
#SBATCH --output=/scratch/ms/dk/nhd/tmp/carra_temp/out/sbatch-%J.out
#SBATCH --job-name='''+sname.replace('carra_','')+'''
'''+cmd
    with open(sfile,'w') as f:
        f.write(text)
    if submit:    
        print(f'Submitting {sfile}')    
        ret=subprocess.check_output("sbatch "+sfile,shell=True)

def select_stream_number(yyyymm,dom):
    '''
    Select correct stream number for IGB 
    '''
    beg_stream={'NE_1': '19960701','NE_2':'20050901','NE_3':'20130901',
               'IGB_1':'19960701','IGB_1B':'20010901','IGB_2':'20050901',
               'IGB_2B':'20090901','IGB_3':'20130901'}
    end_stream={'NE_1':'20060831','NE_2':'20140831','NE_3':'20210630',
               'IGB_1':'20020831','IGB_1B':'20060831',
               'IGB_2':'20100831','IGB_2B':'20140831',
               'IGB_3':'20210630'}
    current_date = datetime.strptime(yyyymm+'01','%Y%m%d')
    stream_number=None
    for key in beg_stream.keys():
        beg_date = datetime.strptime(beg_stream[key],'%Y%m%d')
        end_date = datetime.strptime(end_stream[key],'%Y%m%d')
        if beg_date <= current_date <= end_date and dom in key:
            stream_number = key.split('_')[-1]
            print(f"Should be using stream {stream_number} for this date {yyyymm} and domain {dom}")
    if stream_number != None:
        return stream_number
    else:
        print(f"Could not find stream name for {yyyymm}")
        sys.exit()

def extract_ecfs(dom,stream_number,yyyymm,tmpdir,submit,run=False):
    '''
    extract files from ecfs if files are missing
    tar balls are of the form
    vfldcarra_IGB201604.tar
    Creates a sbatch script for each file
    '''
    failed_commands=[]
    if dom == 'IGB':
        stream_number = select_stream_number(yyyymm,dom)
        print(f"Modified stream number for IGB: {stream_number}")
    edir='/nhx/harmonie/' #carra_IGB_3/vfld'
    sname='_'.join(['carra',dom,stream_number])
    fname='vfldcarra_'+dom+yyyymm+'*'
    dpath=[edir,sname,'vfld',fname]
    cmd_ls='els ec:'+os.path.join(*dpath)
    cmd_copy='ecp ec:'+os.path.join(*dpath)+' '+tmpdir
    try:
        #print(f"Getting list of tar files in {dpath}")
        ret_ls=subprocess.check_output(cmd_ls,shell=True)
        #print(f"Res: {ret_ls}")
    except subprocess.CalledProcessError as err:
        print(f"Error in calling {cmd_ls}")
        print("Hint: maybe not the correct stream number???")
        print("Skipping this period")
        failed_commands.append(cmd_ls+' failed on '+datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S'))
        return failed_commands

    tarfile=ret_ls.decode('utf-8').rstrip()
    print(f"tarfile to extract: {tarfile}")
    write_ec_list('ec:'+tarfile,tmpdir,yyyymm[0:4])
    if run:
        try:
            ret_copy=subprocess.check_output(cmd_copy,shell=True)
        except subprocess.CalledProcessError as err:
            print(f"Error in calling {cmd_copy}")
            print("Hint: maybe not the correct stream number???")
            print("Exiting")
            sys.exit()
    else:
        dpath=[edir,sname,'vfld',tarfile]
        cmd_copy='ecp ec:'+os.path.join(*dpath)+' '+tmpdir
        add_command = cmd_copy+'\n'

    cmd='tar xvf '+tarfile
    if run:
        os.chdir(tmpdir)
        #cmd='cd '+tmpdir+';tar xvf '+tarfile
    else:    
        sfile='copy_'+'_'.join([dom,stream_number,yyyymm])+'.sh'
        sfile = os.path.join(tmpdir,sfile)
        add_command += "cd " + tmpdir + '\n'
        add_command += cmd + '\n'
        add_command += "rm -f " + tarfile + '\n'
        
    #Copy big tar file
    if run:
        try:
            ret=subprocess.check_output(cmd,shell=True)
            dfile=tarfile.rstrip()
            os.remove(dfile)
        except subprocess.CalledProcessError as err:
            print("Error uncompressing data")
        #cmd=re.sub('els ec:','',cmd)

    if run:
        for vfile in os.listdir(tmpdir):
                if vfile.endswith("tar.gz"):
                    print(f"file to uncompress: {vfile}")
                    cmd='tar zxvf '+vfile
                elif vfile.endswith("tar"):
                    print(f"file to uncompress: {vfile}")
                    cmd='tar xvf '+vfile
                try:
                    ret=subprocess.check_output(cmd,shell=True)
                    os.remove(vfile)    
                except subprocess.CalledProcessError as err:
                    print("Error uncompressing %s"%vfile)
    #TODO: delete this option. I will submitting the whole list in one file
    #else:
    #    print("Running all commands from sbatch file")
    #    cmd = 'for file in `ls -1 *.tar.gz`; do tar zxvf ${file}; rm -f ${file};done'
    #    add_command += cmd + '\n'
    #    sbatch_ecfs(sname+'_'+yyyymm[2:],sfile,add_command,submit)        
    return failed_commands

def write_ec_list(fpath,tmpdir,year):
    ofile=os.path.join(tmpdir,'list_ecp_commands_'+year+'.txt')
    if os.path.isfile(ofile):
        with open(ofile,"a") as f:
            f.write(fpath+"\n")
    else:
        with open(ofile,"w") as f:
            f.write(fpath+"\n")

def create_links(files,ddir):
    for f in files:
        tfile=f.split('/')[-1]
        link_name = os.path.join(ddir,tfile)
        cmd="ln -sf "+f+" "+link_name
        try:
             ret=subprocess.check_output(cmd,shell=True)
        except subprocess.CalledProcessError as err:
            print(f"Error in creating link {cmd}")

def write_summary(ofile,dates):
    with open(ofile,"w") as f:
        for date in dates:
            f.write(date+"\n")

def write_failed(ofile,dates):
    if os.path.isfile(ofile):
        with open(ofile,"a") as f:
            for date in dates:
                f.write(date+"\n")
    else:
        with open(ofile,"w") as f:
            for date in dates:
                f.write(date+"\n")

def search_stream(stream_number,period,tmpdir,submit,link,datadir='/scratch/ms/dk/nhz/oprint/'):
    #Check IGB domain
    IGB_path = os.path.join(datadir,'carra_IGB')
    NE_path = os.path.join(datadir,'carra_NE')
    NE_ok = False
    IGB_ok = False

    dtg_valid, dates_found,dates_notfound = check_streams_availability('IGB',period,datadir)
    files_found = [os.path.join(IGB_path,'vfldcarra_IGB'+d) for d in dates_found]
    if len(dtg_valid) == len(dates_found):
        print("IGB complete")
        IGB_ok=True
    else:
        print("IGB missing %d forecast times out of %d"%(len(dates_notfound),len(dtg_valid)))
        if "nhz" in datadir:
            ofile=os.path.join(tmpdir,"missing_oprint_IGB_"+stream_number+'_'+period+".dat")
        else:
            ofile=os.path.join(tmpdir,"missing_IGB_"+stream_number+'_'+period+".dat")
        print(f'Writing forecast times missing for IGB in {ofile}')
        files_notfound = ['vfldcarra_IGB'+d for d in dates_notfound]
        write_summary(ofile,files_notfound)
    if link and len(files_found) != 0:
        print(f"Creating soft links for IGB files present in {IGB_path}")
        dest=os.path.join(tmpdir,'carra_IGB') #,"links_IGB_"+stream_number+'_'+period+".sh"])
        create_links(files_found,dest)

    #check NE domain
    dtg_valid, dates_found,dates_notfound = check_streams_availability('NE',period,datadir)
    files_found = [os.path.join(NE_path,'vfldcarra_NE'+d) for d in dates_found]
    if len(dtg_valid) == len(dates_found):
        print("NE complete")
        NE_ok=True
    else:
        print("NE missing %d forecast times out of %d"%(len(dates_notfound),len(dtg_valid)))
        if "nhz" in datadir:
            ofile=os.path.join(tmpdir,"missing_oprint_NE_"+stream_number+'_'+period+".dat")
        else:
            ofile=os.path.join(tmpdir,"missing_NE_"+stream_number+'_'+period+".dat")
        print(f'Writing forecast times missing for NE in {ofile}')
        files_notfound = ['vfldcarra_NE'+d for d in dates_notfound]
        write_summary(ofile,files_notfound)
    if link and len(files_found) != 0:
        print(f"Creating soft links for NE files present in {NE_path}")
        dest=os.path.join(tmpdir,'carra_NE')
        create_links(files_found,dest)

    #If this period is available, copy data over to from ecfs
    #to temporary location
    #print("Last dtg available for stream %s"%stream_number)
    #print(min_dtg)
    if NE_ok and IGB_ok:
        print(f"Data for NE and IGB in {period} already available")
    else:
        print("copying files to temporary location before proceeding with period: %s"%period)
        for dom in ['IGB','NE']:
            try:
                cdir=os.path.join(tmpdir,'carra_'+dom)
                os.makedirs(cdir)
            except OSError:
                print("%s directory already exists or not enough rights to create it"%cdir)
            yyyymm=period.split('-')[0][0:6]
            failed=extract_ecfs(dom,stream_number,yyyymm,cdir,submit)
            if len(failed) != 0:
                ofile=os.path.join(tmpdir,"failed_commands.dat")
                write_summary(ofile,failed)
                print(f"Not doing period {yyyymm}")

def first_last_year(yymm):
    '''
    if year is 1996 or 1997 limit to start in 19960701 and 19970701
    '''
    proceed = True
    print(yymm)
    yy = yymm[0:4]
    mm = int(yymm[4:6])
    if (yy == '1996' or yy == '1997') and mm < 7:
        print(f"Reject this period: {yymm}")
        proceed = False
    if yy == '2021' and mm < 7:
        print("Not done yet")
        sys.exit()
    return proceed

def sbatch_ecfs_long(script,dom,stream,year):
    text='''#!/bin/bash 
# >>>>>>> To be submitted from ecgate <<<<<<<<
#SBATCH --error=/scratch/ms/dk/nhd/tmp/carra_temp/out/sbatch-%J.err
#SBATCH --output=/scratch/ms/dk/nhd/tmp/carra_temp/out/sbatch-%J.out
#SBATCH --job-name=fetch_'''+dom+'_'+str(year)+'''
module load ecfs
ecd ec:/nhx/harmonie/carra_'''+dom+'_'+stream+'''/vfld/
ecp -F ./list_ecp_commands_'''+str(year)+'''.txt .
'''
    #script=os.path.join(tmpdir,"copy_all_"+dom+"_"+stream+'_'+str(yy)+".sh")
    with open(script,'w') as f:
        f.write(text+'\n')
    cmd_t1 = 'for file in `ls -1 *.tar`; do tar xvf ${file}; rm -f ${file};done'
    cmd_t2 = 'for file in `ls -1 *.tar.gz`; do tar zxvf ${file}; rm -f ${file};done'
    with open(script,'a') as f:
        f.write(cmd_t1+'\n')
        f.write(cmd_t2+'\n')
    #ret=subprocess.check_output("sbatch "+sfile,shell=True)

if __name__ == "__main__":
    #stream_number='3' #CHANGE Decide according to stream period (1,2,3)
    submit=False
    checkExtract=True
    incomplete_years = [1996, 1997, 1998, 1999, 
                       2000, 2001, 2002, 2003, 2004,
                       2016, 2017, 2018]
    incomplete_years=[2018]
    incomplete_months=[i for i in range(1,13)]
    print(incomplete_months)
    bools = {"F":False,"T":True}
    if len(sys.argv) != 5:
        example = '''./check_merge_availability.py year(s) submitOrNot checkExtract cleanOrNot
                    ./check_merge_availability.py 2018,2019 True False True'''
        print(f"Please provide input as in {example}")
        sys.exit()
    else:
        #stream_number = sys.argv[1]
        year = sys.argv[1]
        if "," in year:
            incomplete_years = year.split(',')
        else:
            incomplete_years = [year]
        submit = bools[sys.argv[2]]
        checkExtract = bools[sys.argv[3]]
        clean = bools[sys.argv[4]]
        print(f"Parameters: {incomplete_years}, {submit}, {checkExtract} {clean}")
    #period='19970801-19970831'
    user=subprocess.check_output("echo $USER",shell=True)
    user=user.decode('utf-8').rstrip()
    if user == "nhd":
        tmpdir='/scratch/ms/dk/nhd/tmp/carra_temp'
    elif user == "nhx":
        tmpdir='/scratch/ms/dk/nhx/carra_temp'
    else:
        print(f'User {user} unknown')
        sys.exit()
    print(f'Unpacking data in {tmpdir}')

    #use this to search first
    datadir='/scratch/ms/dk/nhz/oprint/'
    #then switch to this to check if any files still missing after extraction from ecfs
    if  checkExtract:
        datadir=tmpdir
        link=False
    else:
        link=True

    if clean:
        import glob
        for dom in ['NE','IGB']:
            cdir=os.path.join(tmpdir,"carra_"+dom)
            scriptList = glob.glob(os.path.join(cdir,'*sh'))
            ecpList = glob.glob(os.path.join(cdir,'*txt'))
            clean_files=ecpList+scriptList
            for f in clean_files:
                print(f"removing {f}")
                os.remove(os.path.join(cdir,f))

    for yy in incomplete_years:
        for m in incomplete_months: #range(1,13):
            yyyymm = str(yy)+str(m).zfill(2)
            yymmddi = yyyymm +'01'
            yymmddf = lastday(yymmddi)
            period='-'.join([yymmddi,yymmddf])
            #print(period)
            check_period = first_last_year(period)
            if not check_period:
                continue
            print(f'Period to check: {period}')
            # stream number based on NE. Check if correct
            stream_number = select_stream_number(yyyymm,"NE")
            search_stream(stream_number,period,tmpdir,submit,link,datadir=datadir)
        #do whole year at once for each domain
        #if "nhz" not in datadir:
        print("Writing the whole script")
        for dom in ['NE','IGB']:
            stream=select_stream_number(yymmddf[0:6],dom)
            ddir=os.path.join(tmpdir,'carra_'+dom)
            script=os.path.join(ddir,"copy_all_"+dom+"_"+stream+'_'+str(yy)+".sh")
            sbatch_ecfs_long(script,dom,stream,yy)

