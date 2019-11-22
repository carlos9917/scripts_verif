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
    #NOTE: the beginning dates exclude the first year. start years: 1996,2005,2013
    beg_dates={'stream_1':1997070100, 'stream_2':2006090100, 'stream_3':2014090100}
    #check last DTGs produced by the streams
    max_dtg_stream = progress_stream('/home/ms/dk/nhd/scripts/carra/daily_logs.sqlite')
    #print(max_dtg_stream.keys())
    #streams_last_dates = [max_dtg_stream[key] for key in max_dtg_stream.keys()]
    #print(type(streams_last_dates[0]))
    #check last dates already processed:
    #ts_vfld=vt()
    #max_dtg_processed = max(ts_vfld.timestamps.simtimes.tolist()) #which dates already processed
    #print("max dtg already processed: %d"%max_dtg_processed)
    for key in max_dtg_stream.keys():
        print("%d-%d"%(beg_dates[key],max_dtg_stream[key]))

