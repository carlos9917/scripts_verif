# Calculate the range date between the last available DTG of each
# stream and days_beg_merge days before, to give it as argument for
# carra_merged_vfld.p. 
# days_bef_merge is based on current streams speed/day and
# should not be large than 6-7. Making it 10 here to be on the safe side

#Database with time stamps
DBASE='/scratch/ms/dk/nhd/CARRA/daily_logs.sqlite'

from vfldmerge_timestamps import progress_stream
from vfldmerge_timestamps import vfldmerge_timestamps as vt
days_bef_dtg = 10
if __name__ == '__main__':
    from datetime import datetime
    from datetime import timedelta
    beg_dates={}
    #check last DTGs produced by the streams
    max_dtg_stream = progress_stream(DBASE)
    for key in max_dtg_stream.keys():
        date1=datetime.strptime(max_dtg_stream[key][0:8],'%Y%m%d')-timedelta(days=10)
        beg_dates[key] = datetime.strftime(date1,'%Y%m%d')
        print("%s-%s"%(beg_dates[key],max_dtg_stream[key][0:8]))

