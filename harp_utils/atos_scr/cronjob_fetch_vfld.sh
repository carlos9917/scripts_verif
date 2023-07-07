#!/usr/bin/env bash

#Setting up SCRATCH and other variables here
source $HOME/verification/scripts_verif/harp_utils/atos_scr/env_cronjobs.sh

yesterday() {
  YYYY=`date --date "1 days ago" +'%Y'`
  MM=`date --date "1 days ago" +'%m'`
  DD=`date --date "1 days ago" +'%d'`
  #DD=$(printf "%02d\n" $D)
}
if [ -z $1 ]; then
  yesterday
else
  YYYY=$1
  MM=$2
  DD=$3
  MODEL=$4
fi

if [ -z $MODEL ]; then
  for MODEL in EC9 enea43h22mbr000 MEPS_prodmbr000 enea43h22opr; do
     echo "Fetching $YYYY $MM vfld for $MODEL"
    ./fetch_vfld_hirlam.sh $YYYY $MM $MODEL
  done
     echo "Fetching $YYYY $MM $DD vfld for ECDS" #last option means copy here
  ./get_ecds_v2.sh ${YYYY}${MM}${DD} ${YYYY}${MM}${DD} 2
  
     echo "Fetching $YYYY $MM vobs"
  ./fetch_vobs_hirlam.sh $YYYY $MM
else
   echo "User provided: $MODEL"
  if [ $MODEL != "ecds_v2" ] && [ $MODEL != "vobs" ]; then  
     ./fetch_vfld_hirlam.sh $YYYY $MM $MODEL
  elif [ $MODEL == "ecds_v2" ]; then 
     ./get_ecds_v2.sh ${YYYY}${MM}${DD} ${YYYY}${MM}${DD} 2
  elif [ $MODEL == "vobs" ]; then
    ./fetch_vobs_hirlam.sh $YYYY $MM
  fi
fi
