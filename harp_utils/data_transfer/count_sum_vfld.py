#!/usr/bin/env python
import glob
import os
import time
from datetime import datetime
import sys
from calendar import monthrange
models={
        "enea43h22opr":{"flen":52,"fstep":3,"step_cyc":6,"mems":[i for i in range(0,19)]},
        "enea43h22mbr000":{"flen":60,"fstep":3,"step_cyc":3},
        "EC9":{"flen":60,"fstep":3,"step_cyc":6},
        "MEPS_prodmbr000":{"flen":60,"fstep":3,"step_cyc":3}
        }
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
    print(f"{nm} missing on {date}")
    print(f"{np} present on {date}")
    #diff =list(set(files_expected)^set(files_present))
    if nm != 0:
        import re
        diff = list(set(files_expected).difference(set(files_present)))
        diff.sort()
        if eps:
            cut_these=len("vfld")+len(model)+len("mbr")+3
        else:    
            cut_these=len("vfld")+len(model)
        DTGs=[os.path.split(s)[-1][cut_these:] for s in diff]
        dates=[os.path.split(s)[-1][cut_these:cut_these+8] for s in diff]
        dates_sum=list(set(dates))
        hours={}
        cycles={}
        #print("Following dates missing data")
        for d in dates_sum:
            cycles[d] =[]
            hours[d] =[]
            for dtg in DTGs:
                if d == dtg[0:8]:
                    cycles[d].append(dtg[8:10])
                    hours[d].append(dtg[10:12])
            missing_cycles=",".join(list(set(cycles[d])))
            missing_hours=",".join(sorted(set(hours[d])))
            out_model=model+"_missing_vfld.csv"
            with open(out_model,"a+") as f:
                f.write(f"{model} missing data on {d} for cycle(s) {missing_cycles} with hour(s) {missing_hours}\n")
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
    parser.add_argument('-eps',action='store_true') # set to false by default. If given, do eps


    args = parser.parse_args()
    date = args.check_date
    model = args.model
    eps = args.eps
    vfld_path = "/ec/res4/scratch/nhd/verification/vfld/"
    flen=models[model]["flen"]
    fstep=models[model]["fstep"]
    step_cyc=models[model]["step_cyc"]
    count_vfld(date,model,eps,flen,fstep,step_cyc,vfld_path)
