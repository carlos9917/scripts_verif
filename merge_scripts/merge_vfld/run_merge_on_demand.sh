#!/bin/bash 
#PBS -v OMP_NUM_THREADS=1
#PBS -N merge_models
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
outdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld/merged_ondemand
vfldir=/netapp/dmiusr/aldtst/vfld
scrdir=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld

#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#mm: models to merge.NOTE: write as a string with names separated by commas. 
#    The last model in the list will be the one used as reference for any repeated stations
#on: Indicate if models overlap or not (default: nonverlap)

#$py3 ./merge_750models.py -pe 20190102-20190131 -fl 52 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir

cd $scrdir
#1. Merge the models sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand. Produce model ondemand_
echo "Merge sc_ondemand, db_ondemand, nk_ondemand, qa_ondemand"
$py3 ./merge_on_demand_750.py -pe 20200401-20200430 -fl 24 -dvfl $vfldir -dout $outdir/gl_ondemand -mm "sc_ondemand,db_ondemand,nk_ondemand,qa_ondemand"  -on "gl_ondemand"

#2. Merge the models IGB,tasii,sgl40h11. Produce gl_opr
echo "Merge igb40h11,tasii,sgl40h11"
echo "Merging precedence: sgl40h11 replaces any repeated stations"
$py3 ./merge_on_demand_750.py -pe 20200401-20200430 -fl 24 -dvfl $vfldir -dout $outdir/gl_opr -mm "igb40h11,tasii,sgl40h11"  -mt 'overlap' -on "gl_opr"

#3. Merge the models 
#gl_hires (IGB + TASII + SGL40h11 +  "sc_ondemand", "db_ondemand", "nk_ondemand", "qa_ondemand" 
#In other words,  merging: gl_opr and gl_ondemand. 
echo "Merge gl_opr and gl_ondemand"
echo "Merging precedence: gl_ondemand replaces any repeated stations"
$py3 ./merge_on_demand_750.py -pe 20200401-20200430 -fl 24 -dvfl $outdir -dout $outdir/ondemand -mm "gl_opr,gl_ondemand"  -mt 'overlap' -on "ondemand" 
