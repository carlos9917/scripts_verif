#!/bin/bash 
#PBS -v OMP_NUM_THREADS=1
#PBS -N 202005_merge
#PBS -l pvmem=20gb
#PBS -o /data/cap/out
#PBS -j oe -W umask=022
#PBS -q gpc
#PBS -V
#PBS -l walltime=24:00:00

export MPPEXEC=""
export MPPGL=""
export NPOOLS=1
export NPROC=1
ulimit -S -s unlimited || ulimit -s
ulimit -S -m unlimited || ulimit -m
ulimit -S -d unlimited || ulimit -d
#Example script to combine all 750m Greenland models

#Load Carlos' python 
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py3=/data/cap/miniconda2/envs/py37/bin/python

#out and in directories:
#outdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_ondemand
outdir=/data/cap/VFLD
vfldir=/netapp/dmiusr/aldtst/vfld
scrdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld
date_ini=20200501
date_end=20200527
logfile=merge_2005.log
flen=24
merge_ondemand=0 #0: no processing, 1: process this model
merge_opr=0
merge_hi_res=1

# Parameters of the Python script:
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#mm: models to merge.NOTE: write as a string with names separated by commas. 
#    The last model in the list will be the one used as reference for any repeated stations
#on: Indicate if models overlap or not (default: nonverlap)

#$py3 ./merge_750models.py -pe 20190102-20190131 -fl 52 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir
echo "----------------------------------------"
echo "Period to process: ${date_ini}-${date_end}"
echo "----------------------------------------"
cd $scrdir



if [[ $merge_ondemand == 1 ]]; then
    #1. Merge the models sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand. Produce model ondemand_
    echo "--------------------------------------------------------"
    echo "Merge --> sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand"
    echo "--------------------------------------------------------"
    outmodel=gl_ondemand
    $py3 ./merge_on_demand_750.py -pe ${date_ini}-${date_end} -fl $flen -dvfl $vfldir -dout $outdir/$outmodel -mm "sc_ondemand,db_ondemand,nk_ondemand,qa_ondemand"  -on $outmodel -lg $logfile
    echo "-------------------------"
    echo ">>> $outmodel generated <<<"
    echo "-------------------------"
fi


if [[ $merge_opr == 1 ]]; then
    #2. Merge the models IGB,tasii,sgl40h11. Produce gl_opr
    echo "-----------------------------------------------------------"
    echo "Merge --> igb40h11,tasii,sgl40h11"
    echo "Merging precedence: data from sgl40h11 replaces any repeated stations"
    echo "-----------------------------------------------------------"
    outmodel=gl_opr
    $py3 ./merge_on_demand_750.py -pe ${date_ini}-${date_end} -fl $flen -dvfl $vfldir -dout $outdir/$outmodel -mm "igb40h11,tasii,sgl40h11"  -mt 'overlap' -on $outmodel -lg $logfile
    echo "----------------------------"
    echo ">>> $outmodel generated <<<"
    echo "----------------------------"
fi   


if [[ $merge_hi_res == 1 ]]; then
    #3. Merge the models 
    #gl_hires (IGB + TASII + SGL40h11 +  "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" 
    #In other words,  merging: gl_opr and gl_ondemand. 
    echo "----------------------------------------------------------------"
    echo "Merge --> gl_opr and gl_ondemand"
    echo "Merging precedence: data from gl_ondemand replaces any repeated stations"
    echo "----------------------------------------------------------------"
    outmodel=gl_hires
    $py3 ./merge_on_demand_750.py -pe ${date_ini}-${date_end} -fl $flen -dvfl $outdir -dout $outdir/$outmodel -mm "gl_opr,gl_ondemand"  -mt 'overlap' -on $outmodel -lg $logfile
    echo "---------------------------"
    echo ">>> $outmodel generated <<<"
    echo "---------------------------"
fi   
