#!/usr/bin/env bash
module load R/4.2.2

MM=02
VAR=T2m
CY=00
set_prod_years()
{
new_years=()
add_year=0
for year in "${prod_years[@]}"; do
  # Add the given number to each element
  new_year=$((year + add_year))
  # Append the result to the new array
  new_years+=($new_year)
done
}

if [ -z $1 ]; then
MODEL=DKREA
BPATH=/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/FCTABLE/$MODEL
#first year of production, then add a year as needed
set_prod_years
else
MODEL=$1
MONTHS=$2
prod_years=($3)
#set_prod_years
BPATH=/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/FCTABLE/$MODEL
fi


new_years=($(seq 1990 2023))
echo "Processing $MODEL and $MONTHS for ${new_years[@]}"


dbases=()
miss=0
dbmiss=()
MODEL=$(basename $BPATH)
echo $MODEL

MONTHS=($(seq -w 1 12))

for MM in ${MONTHS[@]}; do
for year in ${new_years[@]}; do
  DBASE=$BPATH/$year/$MM/FCTABLE_${VAR}_${year}${MM}_${CY}.sqlite
  if [ ! -f $DBASE ]; then
  echo "$DBASE is missing!"
  miss+=1
  dbmiss+=($DBASE)
else
  dbases+=($DBASE)
fi
done
done
if [ $miss != 0 ]; then
  echo "There was missing data. Stopping here."
  exit 1
fi
# Define the separator
separator=","

# Use IFS to join the array elements
use_dbases=$(IFS="$separator"; echo "${dbases[*]}")
use_years=$(IFS="$separator"; echo "${new_years[*]}")
echo ${use_years[@]}

Rscript query_dbases.R -dbase "${use_dbases}" -years $use_years -table FC -output report.html
mv availability_grid.png availability_grid_${MODEL}.png
