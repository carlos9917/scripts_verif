#calculate date difference
from datetime import date
from datetime import datetime
import sys
from calendar import monthrange
#determine the number of days in this month (properly accounts for leap years!)
#curDTG=sys.argv[1]
def lastday(curDTG):
    days_in_month=monthrange(int(curDTG[0:4]),int(curDTG[4:6]))[1]
    datel=curDTG[0:6]+str(days_in_month).zfill(2)
    l_date = date(int(datel[0:4]), int(datel[4:6]),int(datel[6:8])) #last day of month
    f_date=date(int(curDTG[0:4]),int(curDTG[4:6]),int(curDTG[6:8])) #current day
    return datetime.strftime(l_date,'%Y%m%d')
    
#delta = l_date - f_date 
#print(delta.days)
if __name__=='__main__':
    #calculate last day of month
    if len(sys.argv) == 1:
        print("Please provide first day of the month (YYYYMMDD)")
        sys.exit()
    else:
        curDTG=sys.argv[1]
        lastDate = lastday(curDTG)
        print(lastDate)

