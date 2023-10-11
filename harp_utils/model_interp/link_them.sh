#!/usr/bin/env bash


source env.sh
MODEL=panguweather
if [ -z $1 ]; then
  echo "Using hard coded model $MODEL to link files in $VFLD_PATH"
else
  MODEL=$1
  echo "Using given model $MODEL"
fi


cd $VFLD_PATH/$MODEL
ml eclib
for F in $(find -iname "*.grib"); do
DIR=$(dirname $F)
BNAME=$(basename $F)
DATE=$(substring $F 3 12) # | sed 's/^\///;s/\///g')
HH=$(substring $F 11 12)
FC=$(basename $F .grib | awk '{print substr($1,3,4)}')
#echo $DATE $HH $FC
if [ $HH == 12 ]; then
 ln -sf $PWD/${DATE}00/T-$FC.grib ${MODEL}${DATE}${FC}
fi
done
cd -
