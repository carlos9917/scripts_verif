#!/usr/bin/env bash
# Links some files and renames others in
# the AI models path

MODEL=panguweather
if [ -z $1 ]; then
  echo "Using hard coded model $MODEL"
else
  MODEL=$1
  echo "Using given model $MODEL"
fi

source env.sh

cd $VFLD_PATH/$MODEL
echo "renaming all files T-6.grib as T-06.grib"

for F in $(find -iname T-6.grib); do
DIR=$(dirname $F)
mv $F $DIR/T-06.grib
done

#Removing unnecessary nc files 
for F in $(find -iname "*.nc"); do
echo "Deleting $F"
rm $F
done
cd -
