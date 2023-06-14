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
#11002 S10m, 12201: T2m
var=12201 #TROAD
var=12200 #T2m
var=11002 #S10m
if [[ $OB == 1 ]]; then
  for filename in $obs_path/dump_${var}_2023*.db; do
     # echo $filename
     python restructure_db.py --file=$filename --year $year 1 0 --param $var
  done
fi




