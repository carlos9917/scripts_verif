#!/usr/bin/env bash
module load R/4.2.2

MM=02
VAR=T2m
CY=00
BPATH=/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/FCTABLE/carra2

#first year of production, then add a year as needed
prod_years=($(seq 1985 5 2020))

new_years=()
add_year=1
for year in "${prod_years[@]}"; do
  # Add the given number to each element
  new_year=$((year + add_year))
  # Append the result to the new array
  new_years+=($new_year)
done

dbases=()
for year in ${new_years[@]}; do
DBASE=$BPATH/$year/$MM/FCTABLE_${VAR}_${year}${MM}_${CY}.sqlite
if [ ! -f $DBASE ]; then
echo "$DBASE is missing!"
exit 1
else
dbases+=($BPATH/$year/$MM/FCTABLE_${VAR}_${year}${MM}_${CY}.sqlite)
fi
done

# Define the separator
separator=","

# Use IFS to join the array elements
use_dbases=$(IFS="$separator"; echo "${dbases[*]}")
use_years=$(IFS="$separator"; echo "${new_years[*]}")

Rscript query_dbases.R -dbase "${use_dbases}" -years $use_years -table FC -output report.html