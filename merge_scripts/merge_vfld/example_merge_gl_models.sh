#!/bin/bash 

#Example script to combine all 750m Greenland models

#Load Carlos' python 
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py3=/data/cap/miniconda2/envs/py37/bin/python

#out and in directories:
outdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/gl
vfldir=/netapp/dmiusr/aldtst/vfld
scrdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
cd $scrdir
$py3 ./merge_750models.py -pe 20190102-20190131 -fl 52 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir
