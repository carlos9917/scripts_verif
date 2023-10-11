#!/usr/bin/env bash
#SBATCH --error=ai_model_pre.%j.err
#SBATCH --output=ai_model_pre.%j.out
#SBATCH --job-name=ai_model_pre
#SBATCH --qos=nf
#SBATCH --mem-per-cpu=16000

source env.sh
source $HOME/bin/utils.sh

MODEL=panguweather
if [ -z $1 ]; then
  echo "Using hard coded model $MODEL"
  [ -z $2 ] && PERIOD=202309
  [ -z $3 ] && CY=12
else
  MODEL=$1
  PERIOD=$2
  CY=$3
  [ -z $2 ] && PERIOD=202309
  [ -z $3 ] && CY=12
  echo "Using given model $MODEL"
fi

ml eclib
ml R/4.0.4
YYYY=$(substring $PERIOD 1 4)
MM=$(substring $PERIOD 5 6)
maxday_month
echo "Doing $YYYY $MM for cycle $CY of $MODEL"

#Rscript read_save_pangu.R -start_date $YYYY${MM}01 -end_date $YYYY${MM}$MAXDAY -model $MODEL

VAR="T2m"
Rscript read_save_fourcast.R -start_date $YYYY${MM}01 -end_date $YYYY${MM}$MAXDAY -model $MODEL  -param $VAR
DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
#Note: this commits the changes to file already
sqlite3 $DBASE 'UPDATE FC SET parameter = "T2m";'

#Panguweather pressure in Pa, converting to hPa below
VAR="Pmsl"
Rscript read_save_fourcast.R -start_date $YYYY${MM}01 -end_date $YYYY${MM}$MAXDAY -model $MODEL  -param $VAR
DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
sqlite3 $DBASE "UPDATE FC SET parameter = '$VAR';"
sqlite3 $DBASE "UPDATE FC SET '$MODEL'_det = '$MODEL'_det/100.0;"
sqlite3 $DBASE "UPDATE FC SET units = 'hPa';"

#Panguweather velocity componenents. Calculating u10 from the two temporary sqlite files
# and renaming the one I modified as S10m
VAR="S10m"
Rscript read_save_fourcast.R -start_date $YYYY${MM}01 -end_date $YYYY${MM}$MAXDAY -model $MODEL  -param $VAR
echo "Calculating S10m based on the 10u and 10v data"
DBASE_10u=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10u_${YYYY}${MM}_${CY}.sqlite
DBASE_10v=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10v_${YYYY}${MM}_${CY}.sqlite
DBASE_S10=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
ml python3
./calc_u10m.py $YYYY$MM $MODEL
mv $DBASE_10u $DBASE_S10
rm $DBASE_10v
