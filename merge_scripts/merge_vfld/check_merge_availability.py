#

import datetime
import os
import glob
import fnmatch

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
     date_ini=datetime.datetime.strptime(period[0],'%Y%m%d')
     date_end=datetime.datetime.strptime(period[1],'%Y%m%d')
     dates = [date_ini + datetime.timedelta(days=x) for x in range(0, (date_end-date_ini).days + 1)]
     model_dates=[datetime.datetime.strftime(date,'%Y%m%d') for date in dates]
     stream='_'.join(['carra',stream])
     vflddir=os.path.join(datadir,stream)
     dates_found=[]
     for ifile in os.listdir(vflddir): #TODO: need to refine search below. 
                                       # Only matching the YYYYMM of first date!
                                       #OK for same month, since usually running
                                       #one month at a time
         if fnmatch.fnmatch(ifile, 'vfld*'+period[0][0:6]+'*'):
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

if __name__ == "__main__":
    period='20160601-20160630'
    datadir='/scratch/ms/dk/nhz/oprint/'
    dtg_valid, dates_found,dates_notfound = check_streams_availability('IGB',period,datadir)
    print(dates_found)
    print('-------------')
    print(dates_notfound)
    #check_streams_availability('NE',period,datadir)

