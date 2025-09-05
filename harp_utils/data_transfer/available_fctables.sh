#!/usr/bin/env bash
module load R/4.2.2
#module load R/4.0.4
#MODELS=(enea43h22mbr000 enea43h22opr ecds_v2 MEPS_prodmbr000)
#MODELS=(igb40h11 enea43h22mbr000 MEPS_prodmbr000 EC9 enea43h22opr ecds_v2)
MODELS=(enea43h22mbr000 MEPS_prodmbr000 EC9 enea43h22opr ecds_v2 panguweather fourcastnet DKREA)
FPATH=$SCRATCH/verification/DMI_data/harp_v0201
CWD=$PWD
VAR="S10m"
echo "base path for data: $FPATH"

if [[ -z $1 ]]; then
   echo "Please provide YYYYMM (ie, 202301)"
   echo "Alternatively, include the model name as second argument (ie, 202211 EC9)"
   echo "Available models: ${MODELS[@]}"
   exit 1
else
   DATE=$1
fi
if [ ${#DATE} == 6 ]; then
   CY=12 # which cycle I am checking in the $VAR data
   CY=00
   echo "Using hard coded cycle $CY"
elif [ ${#DATE} == 8 ]; then
  CY=${DATE:6:2}
  echo "Taking cycle from date: $CY"
else
  echo "${#DATE}"
fi

HVERIF=/perm/nhd/R/latest_harp_verif/harp-verif
if [ $DATE == AVAIL ]; then
        echo "Available model data in:"
        for D in $(ls -d $FPATH/FCTABLE/*); do basename $D; done
        exit 0
fi
YYYY=`echo $DATE | awk '{print substr($1,1,4)}'`
MM=`echo $DATE | awk '{print substr($1,5,2)}'`
echo "Checking data in cycle $CY (FCTABLE_${VAR}_${YYYY}${MM}_$CY.sqlite)"

if [ -z $2 ]; then
  for MODEL in ${MODELS[@]}; do
  CHECK=$(printf "\nchecking $MODEL\n")
  echo $CHECK
  # Quick check the availabilty of each
  DBASE=$FPATH/FCTABLE/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_$CY.sqlite
  if [ -f $DBASE ]; then
     #Rscript ./pull_dates_sql.R -dbase  $DBASE -csv_file "available_dates_$MODEL.csv"
     cd $HVERIF/pre_processing
     Rscript ./pull_dates_sql.R -dbase  $DBASE
     # to dump the tables availability in csv files
     #Rscript ./pull_dates_sql.R -dbase  $DBASE -csv_file "available_dates_$MODEL.csv"
     cd -
   else
     echo "$DBASE does not exist for $MODEL"   
  fi
  done
else
  MODEL=$2
  [ $MODEL == "comeps" ] && MODEL=enea43h22opr
  if [ $MODEL = check ] ; then
    ls $SCRATCH/verification/vfld/
    exit 1
  fi
  DBASE=$FPATH/FCTABLE/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_$CY.sqlite
  if [ -f $DBASE ]; then
     cd $HVERIF/pre_processing
     Rscript ./pull_dates_sql.R -dbase  $DBASE -csv_file "$CWD/dates_${YYYY}${MM}_$MODEL.csv"
     cd -
   else
     echo "$DBASE does not exist for $MODEL"   
  fi

fi
                                                                                        
