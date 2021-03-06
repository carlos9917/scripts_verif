#!/bin/bash 
#SBATCH --error=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.err
#SBATCH --output=/perm/ms/dk/nhd/carra_merge_vfld/runout-%J.out
##SBATCH --workdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld

##SBATCH --error=/scratch/ms/dk/nhx/oprint/runout/runout-%J.err
##SBATCH --output=/scratch/ms/dk/nhx/oprint/runout/runout-%J.out
#SBATCH --job-name=ext200907


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

#pe: period to process (do not use more than 1 month at a time, otherwise it is too slow!)
#fl: forecast length
#fi: init times
wrkdir=/home/ms/dk/nhx/scr/merge_scripts/git_repo/scripts_verif/merge_scripts/merge_vfld
wrkdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
#wrkdir=/perm/ms/dk/nhd/scripts_verif/merge_scripts/merge_vfld
cd $wrkdir
#$py3 ./merge_carra_vfld.py -pe 20160701-20160710 -fl 31 -fi 00,06,12,18 -dvfl $vfldir -dout $outdir # -fw
$py3 check_merge_availability.py
