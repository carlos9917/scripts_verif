#/bin/bash
eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
conda activate py38
FC=0
OB=1
year=2023
fcst_path=/data/projects/glatmodel/fcst #dump_202301_00.db
obs_path=/data/projects/glatmodel/obs #dump_202301_00.db

if [[ $FC == 1 ]]; then
  for filename in $fcst_path/*.db; do
      echo $filename
      python restructure_db.py --file=$filename 0 1
  done
fi

if [[ $OB == 1 ]]; then
  for filename in $obs_path/dump_12201*.db; do
     # echo $filename
     python restructure_db.py --file=$filename --year $year 1 0 
  done
fi




