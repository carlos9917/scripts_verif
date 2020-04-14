#!/bin/bash
#SBATCH --error=/scratch/ms/dk/nhx/oprint/runout/dayvfmerge-%J.err
#SBATCH --output=/scratch/ms/dk/nhx/oprint/runout/dayvfmerge-%J.out
#SBATCH --job-name=dayvfmerge

#Script to merge latest data available from all 3 streams
#Load Carlos' python 
#export PATH=/perm/ms/dk/nhd/miniconda3/bin:$PATH
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
timestamp=`date '+%Y%m%d'`
echo "Daily merging of IGB and NE on: $timestamp"
logfile=mergedaily_${timestamp}.log
wrkdir=/home/ms/dk/nhx/scr/merge_scripts/git_repo/scripts_verif/merge_scripts/merge_vfld
cd $wrkdir
yymmdd_range=($($py3 ./update_vfld.py))
i=0
for yymmdd in ${yymmdd_range[@]}; do
let i++
logfile=mergedaily_${timestamp}_${i}.log
echo "Doing period: $yymmdd"
$py3 ./merge_carra_vfld.py -pe $yymmdd -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir -log $logfile -fw
done
