#!/usr/bin/env bash
if [ -z $1 ]; then
  echo "Please provide year in YYYY format"
  exit 1
else
  YYYY=$1
  SOURCE=$2
fi
FPATH=$SCRATCH/verification/DMI_data/harp_v0201
clean_obs()
{
if [ -z $SOURCE ]; then
  dbase=$FPATH/OBSTABLE/OBSTABLE_${YYYY}.sqlite
  echo "cleaning the file $dbase"
  sqlite3 $dbase "VACUUM;"
else
  dbase=$FPATH/vobs/$SOURCE/OBSTABLE_${YYYY}.sqlite
  echo "Cleaning the source in $dbase"
  sqlite3 $dbase "VACUUM;"
fi
}

clean_obs
