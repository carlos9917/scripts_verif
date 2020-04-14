#!/bin/bash
###SBATCH --error=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.out
###SBATCH --output=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.out
###SBATCH --workdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
#SBATCH --error=/scratch/ms/dk/nhx/oprint/runout/vfldmerge-%J.err
#SBATCH --output=/scratch/ms/dk/nhx/oprint/runout/vfldmerge-%J.out
#SBATCH --job-name=merge00


#Example script to combine carra NE and IGB data
#The python script below takes into account the overlapping
#of the domains, and keeps only the data from NE
#Load Carlos' python 
#export PATH=/perm/ms/dk/nhd/miniconda3/bin:$PATH
#source activate py37
py3=/perm/ms/dk/nhd/miniconda3/envs/py37/bin/python

#out and in directories:
#outdir=/perm/ms/dk/nhd/carra_merge_vfld
outdir=/scratch/ms/dk/nhx/oprint/carra
vfldir=/scratch/ms/dk/nhz/oprint/
#vfldir=/scratch/ms/dk/nhd/tmp/carra_temp/
#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
#yymm : possible command line option here. calculate num of days in month and set command line args below
#yymm=$1
yy=2000
logfile=merge_${yy}_partial.log
FORCE_OVERWRITE=1
#wrkdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
wrkdir=/home/ms/dk/nhx/scr/merge_scripts/git_repo/scripts_verif/merge_scripts/merge_vfld
cd $wrkdir
#for mm in 01 02 03 04 05 06 07 08 09 10 11 12; do
for mm in 06 08; do
logfile=merge_${yy}${mm}.log
yymm=$yy$mm
yymmdd=`$py3 ./finaldate.py $yy${mm}01`
echo "Doing period: $yy${mm}01-${yymmdd}"
if (($FORCE_OVERWRITE)); then
  echo "forcing overwriting of old data"
  $py3 ./merge_carra_vfld.py -pe $yy${mm}01-${yymmdd} -fl 31 -dvfl $vfldir -dout $outdir -log $logfile
  ###$py3 ./merge_carra_vfld.py -pe $yy${mm}01-$yy${mm}01 -fl 31 -dvfl $vfldir -dout $outdir -log $logfile
else
 echo "no overwriting of old data"
  $py3 ./merge_carra_vfld.py -pe $yy${mm}01-${yymmdd} -fl 31 -dvfl $vfldir -dout $outdir -log $logfile -fw 
  ###$py3 ./merge_carra_vfld.py -pe $yy${mm}01-$yy${mm}01 -fl 31 -dvfl $vfldir -dout $outdir -log $logfile -fw 
fi
done
