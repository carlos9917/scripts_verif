#!/usr/bin/env python
import glob
import os
import time
from datetime import datetime
import sys
from calendar import monthrange
models={"enea43h22opr":{"flen":52,"fstep":3,"step_cyc":6,"mems":[i for i in range(0,19)]}}
def count_vfld(date:str,
               model:str,
               eps:bool,
               flen:int,
               fstep:int,
               step_cyc:int,
               vfld_path:str):
    yy=int(date[0:4])
    mm=int(date[4:6])
    yyyymmdd = date
    days_in_month=monthrange(yy,mm)[1]
    if eps:
        str_watch='vfld'+model+"mbr*"+yyyymmdd+'*'
    else:
        str_watch='vfld'+model+yyyymmdd+'*'
    print("Checking if all these files are there: %s"%str_watch)
    files_expected=[]
    for cc in range(0,22,step_cyc): #all cycles
        cycle = str(cc).zfill(2)
        for hh in range(0,flen,fstep):
            step = str(hh).zfill(2)
            if eps:
                mems=models[model]["mems"]
                for m in mems:
                    fstring='vfld'+model+"mbr"+str(m).zfill(3)+yyyymmdd+cycle+step
                    files_expected.append(os.path.join(vfld_path,model,fstring))
            else:    
                fstring='vfld'+model+yyyymmdd+cycle+step
                files_expected.append(os.path.join(vfld_path,model,fstring))
    #all the files present
    files_present = glob.glob(os.path.join(vfld_path,model,str_watch))
    files_present.sort()
    #summarize missing of present
    files_missing=[]
    for _file in files_expected:
        if not(os.path.exists(_file) and os.path.getsize(_file) > 0):
            files_missing.append(_file)      
    nm=len(files_missing)
    np=len(files_present)
    print(f"{nm} missing")
    print(f"{np} present")
    #diff =list(set(files_expected)^set(files_present))
    if nm != np:
        import re
        print("Following files missing")
        diff = list(set(files_expected).difference(set(files_present)))
        diff.sort()
        for i in diff:
            print(i)
        #files_only=[os.path.split(s)[-1] for s in diff]
        #for i in files_only:
        #    print(i)
        #dates = [re.findall(r"\d+",x)[2] for x in files_only]
if __name__=="__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''If no arguments it will check output from bash script
             Example usage: ./check_vobs.py''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-date','--check_date',metavar="Date in YYYYMMDD format",default=datetime.strftime(datetime.today(),"%Y%m%d"),
                        type=str,
                        required=True)

    parser.add_argument('-model',metavar="model",default=None,
                        type=str,
                        required=True)
    args = parser.parse_args()
    date = args.check_date
    model = args.model
    vfld_path = "/ec/res4/scratch/nhd/verification/vfld/"
    flen=models[model]["flen"]
    fstep=models[model]["fstep"]
    step_cyc=models[model]["step_cyc"]
    eps=True
    count_vfld(date,model,eps,flen,fstep,step_cyc,vfld_path)
