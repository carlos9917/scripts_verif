#!/bin/bash
#SBATCH --job-name=road_rest
#SBATCH --qos=nf
#SBATCH --error=road_rest-%j.err
#SBATCH --output=road_rest-%j.out
#SBATCH --mem-per-cpu=48000

source env.sh

local_hosts=(glatmodelvm1p volta)

if [[ ! ${local_hosts[@]} =~ $HOSTNAME ]]; then
  echo "Assuming I am using atos. Loading the local conda module and glat conda env"
  ml conda
  conda activate glat
else
  echo "Assuming I am at DMI. Using py38 conda environment"
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate py38
fi

#11002 S10m, 12201: T2m
var=11002 #S10m
var=12200 #T2m
var=12201 #TROAD
if [[ $DO_OB == 1 ]]; then
  echo "Processing observation data"
  #for var in 11002 12200 12201; do
  for var in 12201; do
    for filename in $obs_path/dump_${var}_${YEAR}*.db; do
       # echo $filename
       # python restructure_db.py --file=$filename --year $YEAR 1 0 --param $var --config $CONFIG_FILE
       python restructure_db_new_format.py --file=$filename --year $YEAR 1 0 --param $var --config $CONFIG_FILE
    done
  done
fi

if [[ $DO_FC == 1 ]]; then
  echo "Processing forecast data"
  for filename in $fcst_path/dump_${YEAR}??_??.db; do
      echo $filename
      #python restructure_db.py --config $CONFIG_FILE --file=$filename --model $MODEL 0 1
      python restructure_db_new_format.py --config $CONFIG_FILE --file=$filename --model $MODEL 0 1
  done
fi
