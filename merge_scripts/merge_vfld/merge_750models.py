# Merge all the non-overlapping data from the 750 models:
#
# /netapp/dmiusr/aldtst/vfld/tasii
# /netapp/dmiusr/aldtst/vfld/sgl40h11
# /netapp/dmiusr/aldtst/vfld/nuuk750
# /netapp/dmiusr/aldtst/vfld/qaan40h11 (runs at 00, 06, 12, 18)
#
# The aim is to combine all the data produced by the 750 models
# in one file named vfldgl750_*
# Two options here:
# non-overlapping (default): domains don't overlap, hence they all contain different stations
# overlapping: domains share some stations. In this case the priority of
# one model over another must be set
#
# The data is assumed to be split into SYNOPVar/Data and TEMPVar/Data
# as in the merge_models750_IGB.py script
#
import logging
import pandas as pd
import os
import sys
import glob
import fileinput
import datetime
import numpy as np
from collections import OrderedDict
import csv
import subprocess
import re
from vfld import vfld as vf
from vfld import vfld_monitor as monitor

if __name__ == '__main__':
    period='20190601-20190630'
    finit='00,06,12,18'
    flen=52
    datadir='/netapp/dmiusr/aldtst/vfld'
    outdir='/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test'
    tasii = vf(model='tasii', period=period, finit=finit, flen=52, datadir=datadir)
    print("tasii done")
    sgl40h11 = vf(model='sgl40h11', period=period, finit=finit, flen=52, datadir=datadir)
    print("sgl done")
    nuuk750 = vf(model='nuuk750', period=period, finit=finit, flen=52, datadir=datadir)
    print("nuuk done")
    qaan40h11 = vf(model='qaan40h11', period=period, finit=finit, flen=52, datadir=datadir)
    print("qaan done")
    models=[tasii, sgl40h11, nuuk750, qaan40h11]
    print("merge synop data from all stations (non-overlapping assumed)")
    for date in tasii.dates:
        print("Merging date %s"%date)
        #Only collect those dates which contain any data:
        frames_synop = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
        frames_temp = [f for f in models if isinstance(f.data_temp[date],pd.DataFrame)]
        dfs=[f.data_synop[date] for f in frames_synop]
        dft=[f.data_temp[date] for f in frames_temp]
        df_synop = pd.concat(dfs,sort=False)
        df_temp = pd.concat(dft)
        mon_save= monitor(model='gl',date=date,df_synop=df_synop,df_temp=df_temp,outdir=outdir)
        mon_save.write_vfld()
        del df_synop
        del df_temp
        del mon_save
