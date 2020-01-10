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
yy=2019
logfile=merge_${yy}.log
wrkdir=/perm/ms/dk/nhd/scripts_verif/contrib_verif
var='TT'
model='EC9'
cd $wrkdir
for mm in 06; do
    for dd in 01 11 21; do
    #for dd in 21; do
    let df=dd+9
    df=`printf "%02d\n" $df`
    echo "Doing period: $yy${mm}$dd-$yy$mm$df"
    $py3 ./merge_vobs_vfld.py -pe $yy$mm$dd-$yy$mm$df -m $model -fi 00 -fl 61 -var $var -din '/scratch/ms/dk/nhz/oprint' -dout '/perm/ms/dk/nhd/carra_merge_vfld'
done
done
