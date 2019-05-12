# script to convert vobs/vfld data to verif format
# from MeteoMate to the format that verif expects to find.
# The obs data is taken from the CDC files generated by
# cdcDWDToMETFormat.py

import datetime
import os
import numpy as np
import pandas as pd

def read_synop(time,date):
def read_temp(time,date):
    "Read the "



sDate='2017103100'
eDate='2017110700'
TempFile='./Temperature_clean_20171031_20171106.txt'#'WP_AHAUS_2017110100_Temperature.csv'
WindFile='./Wind_clean_20171031_20171106.txt'#'WP_AHAUS_2017110100_Wind.csv'
GustFile='./Gust_clean_20171031_20171106.txt'

startDate = datetime.datetime.strptime(sDate, "%Y%m%d%H")
endDate = datetime.datetime.strptime(eDate, "%Y%m%d%H")

station_Data = '/gpfs/home/ENERCON1/00061460/DATA/AHAUS/DWD_CDC_DATA/Station_07374/MET/'
date_list = [startDate + datetime.timedelta(days=x) for x in range(0, (endDate-startDate).days + 1)] 

# open output file for writing the fcst/obs data for T
ofT=open('obs_fcst_T2_mmate_'+str(sDate)+'.txt','w')
ofT.write("%s\n" %("# variable: T"))
ofT.write("%s\n" %("# units: $K$"))
ofT.write("%s %s %s %s %s %s %s %s %s %s %s\n" %("date" , "leadtime", "location","lat", "lon", "altitude" ,"obs", "fcst", "p0", "p11", "pit"))

# open output file for writing the fcst/obs data for U
ofU=open('obs_fcst_WS_mmate_'+str(sDate)+'.txt','w')
ofU.write("%s\r\n" %("# variable: U"))
ofU.write("%s\n" %("# units: $m s^{-1}$"))
ofU.write("%s %s %s %s %s %s %s %s %s %s %s\n" %("date" , "leadtime", "location","lat", "lon", "altitude" ,"obs", "fcst", "p0", "p11", "pit"))

# open output file for writing the fcst/obs data for Wind Gust
ofG=open('obs_fcst_Gust_mmate_'+str(sDate)+'.txt','w')
ofG.write("%s\r\n" %("# variable: Gust"))
ofG.write("%s\n" %("# units: $m s^{-1}$"))
ofG.write("%s %s %s %s %s %s %s %s %s %s %s\n" %("date" , "leadtime", "location","lat", "lon", "altitude" ,"obs", "fcst", "p0", "p11", "pit"))

# open file with digitalized data from meteo mate
# x,Date,Leadtime,Wind
with open(TempFile) as f:
    mmT = pd.read_csv(f,delimiter=" ")
    mmT_Fcst = mmT.Temp.tolist()
    mmT_Lt = mmT.Leadtime.tolist()
    mmT_Hour = mmT.Hour.tolist()
    mmT_Date = mmT.Date.tolist()


with open(WindFile) as f:
    mmU = pd.read_csv(f,delimiter=" ")
    mmU_Fcst = mmU.Wind.tolist()
    mmU_Lt = mmU.Leadtime.tolist()
    mmU_Hour = mmU.Hour.tolist()
    mmU_Date = mmU.Date.tolist()


# read the data generated by the cdc script:
for date in date_list:
    thisdate =  date.strftime("%Y%m%d")
    ifile = os.path.join(station_Data,'ascii_obs_cdc_'+str(thisdate)+'.txt')
    with open(ifile) as f:
        print "opening cdc/obs data file ",ifile
        rawData=pd.read_csv(f,delimiter=" ")
        rawData.columns=['mtype','sid','time','lat','lon','elev','gcode','lev','height','qc','obs'] #define headers
        obsDates=rawData.time.tolist()
        obsId = rawData.sid.tolist()
        obsLAT = rawData.lat.tolist()
        obsLON = rawData.lon.tolist()
        obsELV = rawData.elev.tolist()
        obs = rawData.obs.tolist()
        obsGrib=rawData.gcode.tolist()
        fcstHours = range(0,168)
        missingHoursT=[];missingHoursU=[]
        for fh in fcstHours:
            if fh not in mmT_Lt:
                missingHoursT.append(fh)
            if fh not in mmU_Lt:
                missingHoursU.append(fh)
        print "missing hours in U ",missingHoursU

        for j,obsTime in enumerate(obsDates):
            for k,fcst in enumerate(mmT_Fcst):
                timeMM = str(mmT_Date[k]) +'_'+ str(mmT_Hour[k]*10000).zfill(6)
                if (timeMM == obsTime and obsGrib[j]==11):  #temperature
                    fcst=mmT_Fcst[k] + 273.15 # convert to K
                    leadTime = mmT_Lt[k] # want to have this as function of meteo mate lead time  instead
                    takeDate, takeTime = obsTime.split('_')
                    #leadTime=takeTime[0:2]
                    #leadTime = mmT_Lt[k] # want to have this as function of meteo mate lead time  instead
                    ofT.write("%s %s %d %.3f %.3f %.3f %.3f %.3f %s %s %s\n" %(takeDate,leadTime,obsId[j],obsLAT[j], obsLON[j], obsELV[j] ,obs[j], fcst, "-999.0", "-999.0","-999.0" ))

        for j,obsTime in enumerate(obsDates):
            for k,fcst in enumerate(mmU_Fcst):
                timeMM = str(mmU_Date[k]) +'_'+ str(mmU_Hour[k]*10000).zfill(6)
                if (timeMM == obsTime and obsGrib[j]==32): #wind
                    print "time in MM and onbs file ",timeMM,obsTime
                    fcst=mmU_Fcst[k]
                    takeDate, takeTime = obsTime.split('_')
                    #leadTime=takeTime[0:2]
                    leadTime = int(mmU_Lt[k]) # want to have this as function of meteo mate lead time  instead
                    ofU.write("%s %d %d %.3f %.3f %.3f %.3f %.3f %s %s %s\n" %(takeDate,leadTime,obsId[j],obsLAT[j], obsLON[j], obsELV[j] ,obs[j], fcst, "-999.0", "-999.0","-999.0" ))
            #For Gust there is no data, so no writing anything here (at least for CDC)


#import verif
#input = verif.input.Text('obs_fcst_U10_mmate_00.txt')
#data = verif.data.Data(inputs=[input])
#[obs, fcst] = data.get_fields() # data.get_scores(fields, 0, axis, 0)
#print fcst


