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
from vfld_lite import vfld_lite as vfld

if __name__ == '__main__':
    models=[]
    period='20190601-20190630'
    finit='00,06,12,18'
    flen=52
    datadir='/netapp/dmiusr/aldtst/vfld'
    tasii = vfld(model='tasii', period=period, finit=finit, flen=52, datadir=datadir)
    sgl40h11 = vfld(model='sgl40h11', period=period, finit=finit, flen=52, datadir=datadir)
    nuuk750 = vfld(model='nuuk750', period=period, finit=finit, flen=52, datadir=datadir)
    qaan40h11 = vfld(model='qaan40h11', period=period, finit=finit, flen=52, datadir=datadir)
    models=[tasii, sgl40h11, nuuk750, qaan40h11]
    print("merge synop data from all stations (non-overlapping assumed)")
    for date in tasii.dates
        #Only collect those dates which contain any data:
        frames = [f for f in models if isinstance(f.data_synop[date],pd.DataFrame)]
        print("frames active ")
        print([f.model for f in frames])
        dfs=[f.data_synop[date] for f in frames]
        df_row = pd.concat(dfs)
        print("result")
        print(df_row)
        del df_row
