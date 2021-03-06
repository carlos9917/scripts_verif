#!/bin/bash
###SBATCH --error=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.out
###SBATCH --output=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.out
###SBATCH --workdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
#SBATCH --error=/scratch/ms/dk/nhx/oprint/runout/vfldmerge-%J.err
#SBATCH --output=/scratch/ms/dk/nhx/oprint/runout/vfldmerge-%J.out
#SBATCH --job-name=b2_1701


#Example script to combine carra NE and IGB data
#The python script below takes into account the overlapping
#of the domains, and keeps only the data from NE
#Load Carlos' python 
#export PATH=/perm/ms/dk/nhd/miniconda3/bin:$PATH
#source activate py37
py3=/perm/ms/dk/nhd/miniconda3/envs/py37/bin/python

#out and in directories:
#outdir=/perm/ms/dk/nhd/carra_merge_vfld
yy=2017
branch='carra_beta2'
outdir=/scratch/ms/dk/nhx/oprint/${branch}
#vfldir=/scratch/ms/dk/nhz/oprint/
vfldir=/scratch/ms/dk/nhd/carra_links/
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
#yymm : possible command line option here. calculate num of days in month and set command line args below
#yymm=$1
#April 2007, Sep 1997
#Also: Jan 2000, 2017 and July 2012
logfile=merge_${branch}_${yy}.log
#wrkdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
wrkdir=/home/ms/dk/nhx/scr/merge_scripts/git_repo/scripts_verif/merge_scripts/merge_vfld
cd $wrkdir
#for mm in 01 02 03 04 05 06 07 08 09 10 11 12; do
for mm in 01; do
yymm=$yy$mm
yymmdd=`$py3 ./finaldate.py $yy${mm}01`
echo "Doing period: $yy${mm}27-$yymmdd"
$py3 ./merge_carra_vfld.py -pe $yy${mm}01-$yymmdd -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir -log $logfile -branch $branch
#$py3 ./merge_carra_vfld.py -pe 20070401-20070401 -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir -log $logfile -branch $branch
done
