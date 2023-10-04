#!/usr/bin/env bash
source env.sh
cd $VFLD_PATH/panguweather
for F in $(find -iname T-6.grib); do
DIR=$(dirname $F)
mv $F $DIR/T-06.grib
done

for F in $(find -iname "*.nc"); do
echo "Deleting $F"
rm $F
done
cd -
