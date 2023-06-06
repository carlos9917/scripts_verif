#!/usr/bin/env bash
module load R
#MODELS=(enea43h22mbr000 enea43h22opr ecds_v2 MEPS_prodmbr000)
#MODELS=(igb40h11 enea43h22mbr000 MEPS_prodmbr000 EC9 enea43h22opr ecds_v2)
MODELS=(enea43h22mbr000 MEPS_prodmbr000 EC9 enea43h22opr ecds_v2)

if [[ -z $1 ]]; then
   echo "Please provide YYYYMM (ie, 202301)"
   echo "Alternatively, include the model name as second argument (ie, 202211 EC9)"
   echo "Available models: ${MODELS[@]}"
   exit 1
else
   DATE=$1
fi
CY=12 # which cycle I am checking in the T2m data
CY=00

FPATH=$SCRATCH/verification/DMI_data
HVERIF=/home/nhd/R/harp-verif/
if [ $DATE == AVAIL ]; then
        echo "Available model data in:"
        for D in $(ls -d $FPATH/FCTABLE/*); do basename $D; done
        exit 0
fi
YYYY=`echo $DATE | awk '{print substr($1,1,4)}'`
MM=`echo $DATE | awk '{print substr($1,5,2)}'`
echo "Checking data in cycle $CY (FCTABLE_T2m_${YYYY}${MM}_$CY.sqlite)"

if [ -z $2 ]; then
  for MODEL in ${MODELS[@]}; do
  CHECK=$(printf "\nchecking $MODEL\n")
  echo $CHECK
  # Quick check the availabilty of each
  DBASE=$FPATH/FCTABLE/$MODEL/$YYYY/$MM/FCTABLE_T2m_${YYYY}${MM}_$CY.sqlite
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
  if [ $MODEL = check ] ; then
    ls $SCRATCH/verification/vfld/
    exit 1
  fi
  DBASE=$FPATH/FCTABLE/$MODEL/$YYYY/$MM/FCTABLE_T2m_${YYYY}${MM}_$CY.sqlite
  if [ -f $DBASE ]; then
     cd $HVERIF/pre_processing
     Rscript ./pull_dates_sql.R -dbase  $DBASE
     cd -
   else
     echo "$DBASE does not exist for $MODEL"   
  fi

fi
                                                                                        
