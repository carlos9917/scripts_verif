#!/bin/bash 

#Example script to combine all 750m Greenland models

#Load Carlos' python 
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py3=/data/cap/miniconda2/envs/py37/bin/python

#out and in directories:
outdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_750_test/may_2020
vfldir=/netapp/dmiusr/aldtst/vfld
scrdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
cd $scrdir
#$py3 ./merge_750models.py -pe 20190102-20190131 -fl 52 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir
$py3 ./merge_on_demand_750.py -pe 20200401-20200430 -fl 24 -dvfl $vfldir -dout $outdir

#1. Merge the models sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand. Produce model ondemand_
$py3 ./merge_on_demand_750.py -pe 20200401-20200430 -fl 24 -dvfl $vfldir -dout $outdir -mm "sc_ondemand,db_ondemand,nk_ondemand,qa_ondemand" 
#2. Merge the models IGB,tasii,sgl40h11. Produce gl_opr
#3. Merge the models 
#gl_hires (IGB + TASII + SGL40h11 +  "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" 
