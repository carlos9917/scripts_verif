# Merge NE and IGB vfld data
#
# The aim is to combine all data produced by the NE and IGB domains.
# Whenever a station appears in both data sets, the NE data set takes precedence
# /scratch/ms/dk/nhz/oprint/carra_IGB
# /scratch/ms/dk/nhz/oprint/carra_NE
#

from vfldmerge_timestamps import progress_stream
from vfldmerge_timestamps import vfldmerge_timestamps as vt

if __name__ == '__main__':
    from datetime import datetime
    from datetime import timedelta
    #NOTE: the beginning dates exclude the first year. start years: 1996,2005,2013
    #beg_dates={'stream_1':'19970701','stream_2':'20060901','stream_3':'20140901'}
    #beg_dates={'stream_1':'19990427','stream_2':'20080527','stream_3':'20160510'}
    beg_dates={}
    #check last DTGs produced by the streams
    max_dtg_stream = progress_stream('/home/ms/dk/nhd/scripts/carra/daily_logs.sqlite')
    #calculate 20 days before current date:
    #print(max_dtg_stream.keys())
    #streams_last_dates = [max_dtg_stream[key] for key in max_dtg_stream.keys()]
    #print(type(streams_last_dates[0]))
    #check last dates already processed:
    #ts_vfld=vt()
    #max_dtg_processed = max(ts_vfld.timestamps.simtimes.tolist()) #which dates already processed
    #print("max dtg already processed: %d"%max_dtg_processed)
    for key in max_dtg_stream.keys():
        date1=datetime.strptime(max_dtg_stream[key][0:8],'%Y%m%d')-timedelta(days=20)
        beg_dates[key] = datetime.strftime(date1,'%Y%m%d')
        print("%s-%s"%(beg_dates[key],max_dtg_stream[key][0:8]))

