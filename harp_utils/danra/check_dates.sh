#!/usr/bin/env bash
module load R/4.0.4
#module load R

if [ -z $1 ]; then
  echo "Please provide at least year"
  echo "Other arguments: YYYY MM MODEL"
  echo "Use SYNOP for model for OBSTABLE"
  exit 1
else
  YYYY=$1
  MM=$2
  MODEL=$3
fi
[ -z $4 ] && CY=00 || CY=$4
[ -z $5 ] && VAR="T2m" || VAR=$5
echo "Checking $VAR file for $YYYY $MM and start time $CY"
FPATH=/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/FCTABLE/$MODEL
#FPATH=/ec/res4/scratch/nhd/test_data_harp/FCTABLE/$MODEL
OPATH=/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/OBSTABLE
echo "Base path for FCTABLE data: $FPATH"
echo "Base path for OBSTABLE data: $OPATH"

if [ ! -f $DBASE ]; then
echo "$DBASE does not exist!"
fi

if [ $MM == "SYNOP" ]; then
 if [ -z $MODEL ]; then
  DBASE=$OPATH/OBSTABLE_${YYYY}.sqlite
  Rscript ./pull_dates_sql.R -dbase  $DBASE -table "SYNOP"
 else
  DBASE=$OPATH/$MODEL/OBSTABLE_${YYYY}.sqlite
  Rscript ./pull_dates_sql.R -dbase  $DBASE -table "SYNOP" | awk -F "|" 'NR > 8 { print $3 }' > dates_month.txt 
  module unload R/4.0.4
  module load conda
  conda activate glat
  python parse_dates_screen.py
 fi

else
#### MODEL=DKREA
DBASE=$FPATH/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_$CY.sqlite
[ ! -f $DBASE ] && echo "$DBASE does not exist!" && exit 1
echo "Using $DBASE"
#Rscript ./pull_dates_sql.R -dbase  $DBASE 
#clean the output and parse it to the python script to clean it up
Rscript ./pull_dates_sql.R -dbase  $DBASE | awk '/value/ {found=1; next} {print}' |  awk -F "|" '/:---/ {found=1; next} { print $3 }' | sed '/./,$!d' > dates_month.txt
module unload R #/4.0.4
module load conda
conda activate glat
python parse_dates_screen.py
fi

