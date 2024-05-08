#!/usr/bin/env bash
#SBATCH --error=era5_pre.%j.err
#SBATCH --output=era5_pre.%j.out
#SBATCH --job-name=era5_pre
#SBATCH --qos=nf
#SBATCH --mem-per-cpu=16000

source env.sh
source $HOME/bin/utils.sh

MODEL=ERA5
if [ -z $1 ]; then
  echo "Please provide period ie 202309 and alternatively first and last day"
  exit 1
else
  PERIOD=$1
  echo "Using given model $MODEL"
fi

ml eclib
ml R
YYYY=$(substring $PERIOD 1 4)
MM=$(substring $PERIOD 5 6)
maxday_month
#choose start and end day, otherwise define below
D1=$2
D2=$3
[ -z $2 ] && D1=01
[ -z $3 ] && D2=$MAXDAY

date_beg=20120120
date_end=20120120
#Rscript read_save_era5.R -start_date $YYYY${MM}$D1 -end_date $YYYY${MM}$D2 -model $MODEL
#Rscript read_save_era5.R -start_date $date_beg -end_date $date_end -model $MODEL
#exit

change_db()
{
ml python3
for CY in 06 18; do
  VAR="T2m"
  DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
  echo "Updating $DBASE with the correct column name for $VAR"
  #Note: this commits the changes to file already
  sqlite3 $DBASE 'UPDATE FC SET parameter = "T2m";'
  #
  VAR="Pmsl"
  DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
  echo "Updating $DBASE with the correct column name for $VAR"
  sqlite3 $DBASE "UPDATE FC SET parameter = '$VAR';"
  sqlite3 $DBASE "UPDATE FC SET '${MODEL}_det' = '${MODEL}_det'/100.0;"
  sqlite3 $DBASE "UPDATE FC SET units = 'hPa';"
  
  # velocity components. Calculating u10 from the two temporary sqlite files
  # and renaming the one I modified as S10m
  VAR="S10m"
  echo "Calculating S10m based on the 10u and 10v data"
  DBASE_10u=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10u_${YYYY}${MM}_${CY}.sqlite
  DBASE_10v=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10v_${YYYY}${MM}_${CY}.sqlite
  DBASE_S10=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
  ./calc_u10m.py $YYYY$MM $MODEL $CY
  mv $DBASE_10u $DBASE_S10
  rm $DBASE_10v
done
}
change_db
