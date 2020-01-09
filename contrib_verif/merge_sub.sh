#!/bin/bash
#SBATCH --error=/perm/ms/dk/nhd/carra_merge_vfld/verif-%J.err
#SBATCH --output=/perm/ms/dk/nhd/carra_merge_vfld/verif-%J.out
#SBATCH --job-name=verifmerge


#Example script to combine vobs and vfld data
#source activate py37
py3=/perm/ms/dk/nhd/miniconda3/envs/py37/bin/python

#out and in directories:
#outdir=/perm/ms/dk/nhd/carra_merge_vfld
outdir=/scratch/ms/dk/nhx/oprint/carra
vfldir=/scratch/ms/dk/nhz/oprint/
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
#yymm : possible command line option here. calculate num of days in month and set command line args below
#yymm=$1
yy=2016
logfile=merge_${yy}.log
wrkdir=/perm/ms/dk/nhd/scripts_verif/contrib_verif
cd $wrkdir
$py3 ./merge_vobs_vfld.py
#for mm in 06; do
#yymm=$yy$mm
#yymmdd=`$py3 ./finaldate.py $yy${mm}01`
#echo "Doing period: $yy${mm}01-$yymmdd"
#$py3 ./merge_carra_vfld.py -pe $yy${mm}01-$yymmdd -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir -log $logfile -fw
#done
