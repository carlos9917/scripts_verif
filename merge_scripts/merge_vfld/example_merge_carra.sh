#!/bin/bash 

#Example script to combine carra NE and IGB data
#The python script below takes into account the overlapping
#of the domains, and keeps only the data from NE
#Load Carlos' python 
#export PATH=/perm/ms/dk/nhd/miniconda3/bin:$PATH
#source activate py37
py3=/perm/ms/dk/nhd/miniconda3/envs/py37/bin/python

#out and in directories:
outdir=/perm/ms/dk/nhd/carra_merge_vfld
vfldir=/scratch/ms/dk/nhz/oprint/

#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
wrkdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
cd $wrkdir
$py3 ./merge_carra_vfld.py -pe 19970906-19970906 -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir
