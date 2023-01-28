#!/usr/bin/env bash
module load R

if [[ -z $1 ]]; then
   echo "Please provide YYYY"
   exit 1
else
   DATE=$1
fi

FPATH=$SCRATCH/verification/DMI_data
HVERIF=/home/nhd/R/harp-verif

YYYY=`echo $DATE | awk '{print substr($1,1,4)}'`
MM=`echo $DATE | awk '{print substr($1,5,2)}'`
dbase=/data/projects/nckf/danra/verification/OBSTABLE/OBSTABLE_${YYYY}.sqlite
dbase=$FPATH/OBSTABLE/OBSTABLE_${YYYY}.sqlite
table=SYNOP
cd $HVERIF/pre_processing
Rscript ./pull_dates_sql.R -dbase  $dbase -table $table
cd -

