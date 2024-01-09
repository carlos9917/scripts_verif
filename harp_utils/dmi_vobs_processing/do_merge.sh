#!/usr/bin/env bash
#SBATCH --error=obs_merge.%j.err
#SBATCH --output=obs_merge.%j.out
#SBATCH --job-name=obs_merge
#SBATCH --qos=nf
#SBATCH --mem-per-cpu=48000

#if [ $HOSTNAME == glatmodelvm1p ]; then
#  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
#  conda activate py38
#else
#  module load python3	
#fi
YEAR=2024
DBASE_PATH=/ec/res4/scratch/nhd/verification/DMI_data/vobs
echo "Cleaning the databases first"
for SOURCE in DMI IMO MARS; do
 source ./clean_dbases.sh $YEAR $SOURCE
done
source ./clean_dbases.sh $YEAR

echo "End database cleaning"
module load python3	
echo "Merging DMI and MARS"
python3 merge_tables_dmi_mars.py $DBASE_PATH $YEAR
echo "Merging DMI, MARS and IMO"
python3 merge_tables_imo_dmi_mars.py $DBASE_PATH $YEAR
