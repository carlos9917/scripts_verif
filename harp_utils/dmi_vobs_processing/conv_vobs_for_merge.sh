#!/usr/bin/env bash

# Do the conversion of local vobs data to sqlite format, to merge later

if [[ -z $1 ]] &&  [[ -z $2 ]]; then
   echo "Please provide at least 2 arguments"
   echo "ARG1: start date  ARG2: end date (in format YYYYMMDDHH)"
   echo "Example: ./conv_vobs_for_merge.sh 2022020100 2022013123"
   exit 1
else
   SDATE=$1
   EDATE=$2
fi
HARPV=/dmidata/users/cap/R/harp-verif
cd $HARPV/pre_processing

for SOURCE in DMI IMO MARS; do
  CONFIG=config_for_merge/config_$SOURCE.yml
  echo "Using $CONFIG"
  ./vobs2sql.R -start_date $SDATE -end_date $EDATE -config_file $CONFIG
done
