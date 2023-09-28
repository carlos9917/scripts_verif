#!/usr/bin/env bash
#SBATCH --error=ai_model_pre.%j.err
#SBATCH --output=ai_model_pre.%j.out
#SBATCH --job-name=ai_model_pre
#SBATCH --qos=nf
#SBATCH --mem-per-cpu=16000

YYYY=2023
MM=09
CY=12
ml R/4.0.4
Rscript read_save_pangu.R
#
#
VAR="T2m"
DBASE=/ec/res4/scratch/nhd/verification/DMI_data/FCTABLE/panguweather/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
#Note: this commits the changes to file already
sqlite3 $DBASE 'UPDATE FC SET parameter = "T2m";'

#Panguweather pressure in Pa, converting to hPa below
VAR="Pmsl"
DBASE=/ec/res4/scratch/nhd/verification/DMI_data/FCTABLE/panguweather/$YYYY/$MM/FCTABLE_${VAR}_${YYYY}${MM}_${CY}.sqlite
echo "Updating $DBASE with the correct column name for $VAR"
#Note: this commits the changes to file already
sqlite3 $DBASE "UPDATE FC SET parameter = '$VAR';"
sqlite3 $DBASE "UPDATE FC SET panguweather_det = panguweather_det/100.0;"
sqlite3 $DBASE "UPDATE FC SET units = 'hPa';"
