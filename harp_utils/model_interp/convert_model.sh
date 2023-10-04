#!/usr/bin/env bash
#SBATCH --error=ai_model_pre.%j.err
#SBATCH --output=ai_model_pre.%j.out
#SBATCH --job-name=ai_model_pre
#SBATCH --qos=nf
#SBATCH --mem-per-cpu=16000

source env.sh

MODEL=panguweather
YYYY=2023
MM=09
CY=12

ml R/4.0.4
Rscript read_save_pangu.R -start_date $YYYY${MM}01 -end_date $YYYY${MM}28

VAR="T2m"
DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
#Note: this commits the changes to file already
sqlite3 $DBASE 'UPDATE FC SET parameter = "T2m";'

#Panguweather pressure in Pa, converting to hPa below
VAR="Pmsl"
DBASE=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
sqlite3 $DBASE "UPDATE FC SET parameter = '$VAR';"
sqlite3 $DBASE "UPDATE FC SET panguweather_det = panguweather_det/100.0;"
sqlite3 $DBASE "UPDATE FC SET units = 'hPa';"

#Panguweather velocity componenents. Calculating u10 from the two temporary sqlite files
# and renaming the one I modified as S10m

echo "Calculating S10m based on the 10u and 10v data"
DBASE_10u=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10u_${YYYY}${MM}_${CY}.sqlite
DBASE_10v=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_10v_${YYYY}${MM}_${CY}.sqlite
DBASE_S10=$FC_PATH/$MODEL/$YYYY/$MM/FCTABLE_S10m_${YYYY}${MM}_${CY}.sqlite
ml python3
./calc_u10m.py $YYYY$MM
mv $DBASE_10u $DBASE_S10
rm $DBASE_10v
