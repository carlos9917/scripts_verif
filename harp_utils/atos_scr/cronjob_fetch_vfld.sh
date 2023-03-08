#!/usr/bin/env bash

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

echo "Doing $YYYY $MM $DD"
if [ -z $MODEL ]; then
  for MODEL in EC9 enea43h22mbr000 MEPS_prodmbr000 enea43h22opr; do
     echo "Fetching vfld for $MODEL"
    ./fetch_vfld_hirlam.sh $YYYY $MM $MODEL
  done
     echo "Fetching vfld for ECDS" #last option means copy here
  ./get_ecds_v2.sh ${YYYY}${MM}${DD} ${YYYY}${MM}${DD} 2
  
     echo "Fetching vobs"
  ./fetch_vobs_hirlam.sh $YYYY $MM
else
   echo "User provided: $MODEL"
  [ $MODEL != "ecds_v2" ] && ./fetch_vfld_hirlam.sh $YYYY $MM $MODEL
  [ $MODEL == "ecds_v2" ] && ./get_ecds_v2.sh ${YYYY}${MM}${DD} ${YYYY}${MM}${DD} 2
fi
