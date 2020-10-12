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

def check_streams_availability(stream,period,datadir):
     ''' 
     check if all files that should be available for the merge of
     IGB and NE streams are indeed available
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
     stream='_'.join(['carra',stream])
     vflddir=os.path.join(datadir,stream)
     dates_found=[]
     yyyymm=period[0][0:6]
     for ifile in os.listdir(vflddir): #TODO: need to refine search below. 
                                       # Only matching the YYYYMM of first date!
                                       #OK for same month, since usually running
                                       #one month at a time
         if fnmatch.fnmatch(ifile, 'vfld*'+yyyymm+'*'):
             this_date=''.join([n for n in ifile if n.isdigit()])
             dates_found.append(this_date)
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
     return dtg_expected, dates_pass, dates_miss

def read_current_state(hfile,period,stream):
    '''
    read current state through html file printed daily.
    Output dtgs that must be available for this period and stream
    '''
    import bs4 as bs
    from bs4 import BeautifulSoup
    cols=['expId','Current assimilated date','End date of stream',
          'Completion date', 'Avg. throughput (7d)',
          'Avg. throughput (30d)']
    #url='https://hirlam.org/portal/CARRA/Progress/current_state_sims.html'
    #url='/home/cap/current_state_sims.html'
    #import urllib.request
    f = open(hfile,'r') #'/home/cap/current_state_sims.html', 'r')
    s=f.read()
    soup = BeautifulSoup(s,"lxml")
    table=soup.find('table')
    trows=table.find_all('tr')
    #cols=trows[0].text
    #print(cols)
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
        if 'B' not in num:
            if '*' in num: #an asterisk will appear in table sometimes
                num = num.replace('*','')
            dom_edate[num] = np.append(dom_edate[num],date1)
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
        min_dtg[key] = datetime.strftime(min(dom_edate[key]),'%Y%m%d')
        if min(dom_edate[key]) >= date_end and key==stream:
        #if min(dom_edate[key]) >= dtg_beg[key] and min(dom_edate[key]) <= dtg_end[key]:
        #if dtg_beg[key] <= min(dom_edate[key]) and dtg_end[key] >= min(dom_edate[key]):
            period_avail=True
            print("date %s for stream %s must be available"%(min_dtg[key],stream))

    return min_dtg, period_avail

def extract_ecfs(dom,stream,yyyymm,tmpdir):
    '''
    extract files from ecfs if files are missing
    tar balls are of the form
    vfldcarra_IGB201604.tar
    '''
    edir='/nhx/harmonie/' #carra_IGB_3/vfld'
    sname='_'.join(['carra',dom,stream])
    fname='vfldcarra_'+dom+yyyymm+'*'
    dpath=[edir,sname,'vfld',fname]
    cmd_ls='els ec:'+os.path.join(*dpath)
    cmd_copy='ecp ec:'+os.path.join(*dpath)+' '+tmpdir
    try:
        ret_ls=subprocess.check_output(cmd_ls,shell=True)
        ret_copy=subprocess.check_output(cmd_copy,shell=True)
    except subprocess.CalledProcessError as err:
        print("Error in calling command %s"%cmd_ls)
        print("Error in calling command %s"%cmd_copy)
        print("Hint: maybe not the correct stream number???")
        print("Exiting")
        sys.exit()
    tarfile=ret_ls.decode('utf-8')
    print(tarfile)
    os.chdir(tmpdir)
    #cmd='cd '+tmpdir+';tar xvf '+tarfile
    cmd='tar xvf '+tarfile
    print(cmd)
    try:
        ret=subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as err:
        print("Error uncompressing data")
    #cmd=re.sub('els ec:','',cmd)
    dfile=tarfile.rstrip()
    os.remove(dfile)
    for vfile in os.listdir(tmpdir):
        if vfile.endswith("tar.gz"):
            print("file %s"%vfile)
            cmd='tar zxvf '+vfile
            try:
                ret=subprocess.check_output(cmd,shell=True)
            except subprocess.CalledProcessError as err:
                print("Error uncompressing %s"%vfile)
            os.remove(vfile)    

def copy_local(stream,yyyymm):
    '''
    copy files to a local tmp directory if month is missing
    '''
    pass

def search_stream(stream,period,datadir='/scratch/ms/dk/nhz/oprint/'):
    #Read current state of simulations from daily html file:
    min_dtg,period_avail=read_current_state('/home/ms/dk/nhx/scr/check_progress/log/current_state_sims.html',period,stream)
    #Check IGB domain
    dtg_valid, dates_found,dates_notfound = check_streams_availability('IGB',period,datadir)
    NE_ok = False
    IGB_ok = False
    if len(dtg_valid) == len(dates_found):
        print("IGB complete")
        IGB_ok=True
    else:
        print("IGB missing %d dates"%len(dates_notfound))
    #print(dates_found)
    #print('-------------')
    #print(dates_notfound)

    #check NE domain
    dtg_valid, dates_found,dates_notfound = check_streams_availability('NE',period,datadir)
    if len(dtg_valid) == len(dates_found):
        print("NE complete")
        NE_ok=True
    else:
        print("NE missing %d dates out of %d"%(len(dates_notfound),len(dtg_valid)))
    #print(dates_found)
    #print('-------------')
    #print(dates_notfound)

    #If this period is available, copy data over to from ecfs
    #to temporary location
    if period_avail:
        print("Last dtg available for stream %s"%stream)
        print(min_dtg)
        if NE_ok and IGB_ok:
            print("proceed with standard setup")
        else:
            print("copying files to temporary location before proceeding with period: %s"%period)
            #copy_local(tmpdir)
            #now=datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')
            #tmpdir='_'.join([tmpdir,now])
            for dom in ['IGB','NE']:
                try:
                    cdir=os.path.join(tmpdir,'carra_'+dom)
                    os.makedirs(cdir)
                except OSError:
                    print("%s directory already exists or not enough rights to create it"%cdir)
                yyyymm=period.split('-')[0][0:6]
                extract_ecfs(dom,stream,yyyymm,cdir)
    else:
        print("Period %s not available yet"%period)

if __name__ == "__main__":
    incomplete_years = [1996, 1997, 1998, 1999, 
                       2000, 2001, 2002, 2003, 2004,
                       2016, 2017, 2018]
    incomplete_years=[1996]
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
    print(tmpdir)
    stream='1' #CHANGE
    for yy in incomplete_years:
        for m in range(1,13):
            yymmddi = str(yy)+str(m).zfill(2)+'01'
            yymmddf = lastday(yymmddi)
            period='-'.join([yymmddi,yymmddf])
            search_stream(stream,period)
    #need to indicate which stream if I want to copy!!

