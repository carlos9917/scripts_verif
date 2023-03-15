#!/usr/bin/env bash

MODELS=(ecds_v2 enea43h22mbr000 EC9 enea43h22opr)
module load R
# SLURM cript to run the conversion from vfld and vobs to sqlite format.
if [[ -z $1 ]] &&  [[ -z $2 ]]; then 
   echo "Please provide at least 2 arguments"
   echo "ARG1: start date  ARG2: end date (in format YYYYMMDDHH)"
   echo "Example: ./conv2sql.sh 2022020100 2022013123"
   echo "Optionally add 3rd arg as model"
   echo "Some models available: ${MODELS[@]}"
   exit 1
else
   SDATE=$1
   EDATE=$2
fi

YYYY=`echo $EDATE | awk '{print substr($1,1,4)}'`
MM=`echo $EDATE | awk '{print substr($1,5,2)}'`
if [ -z $3 ]; then
  for MODEL in ${MODELS[@]}; do
  echo "Doing $MODEL"
  CONFIG=config_dmi/config_$MODEL.yml
  ./vfld2sql.R -start_date $SDATE -end_date $EDATE -config_file $CONFIG
  # Quick check the availabilty of each
    DBASE=/ec/res4/scratch/duuw/verification/FCTABLE/$MODEL/$YYYY/$MM/FCTABLE_T2m_${YYYY}${MM}_00.sqlite
    Rscript ./pull_dates_sql.R -dbase  $DBASE
  done
else
  MODEL=$3
  if [ $MODEL == "vobs" ]; then
    ./vobs2sql.R -start_date $SDATE -end_date $EDATE -config_file config_dmi/config_enea43h22mbr000.yml
  else
      CONFIG=config_dmi/config_$MODEL.yml
      echo "Using $CONFIG"
    ./vfld2sql.R -start_date $SDATE -end_date $EDATE -config_file $CONFIG
  fi
fi
