# merge data from vobs and vfld in a verif-compatible ascii file
#
import pandas as pd
import os
import sys
import glob
import fileinput
from datetime import datetime
import numpy as np
from collections import OrderedDict
import csv
import subprocess
import re
import csv
import logging
logger = logging.getLogger(__name__)
from vobs import vobs as vobs
from vfld import vfld as vfld

if __name__ == '__main__':
    model='EC9'
    period='20190601-20190601'
    finit='00'
    flen=52
    datadir='/home/cap/data/from_ecmwf/codes/scripts_verif/contrib_verif/data'
    #get vfld and vobs data
    ec9 = vfld(model=model, period=period, finit=finit, flen=flen, datadir=datadir)
    obs = vobs(period=period, flen=24, datadir=datadir) #note: vobs only every 24 h
    #find the matching stations 
    for date in ec9.dates:
        #find matching date and station for this 
        print(date)

