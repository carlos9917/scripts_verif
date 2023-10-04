#!/usr/bin/env bash
source env.sh
cd $VFLD_PATH/panguweather
ml eclib
for F in $(find -iname "*.grib"); do
DIR=$(dirname $F)
BNAME=$(basename $F)
DATE=$(substring $F 3 12) # | sed 's/^\///;s/\///g')
HH=$(substring $F 11 12)
FC=$(basename $F .grib | awk '{print substr($1,3,4)}')
#echo $DATE $HH $FC
if [ $HH == 12 ]; then
 ln -sf $PWD/${DATE}00/T-$FC.grib pangu${DATE}${FC}
fi
done
cd -
