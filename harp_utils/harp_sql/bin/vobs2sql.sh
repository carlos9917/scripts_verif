#!/usr/bin/env bash

# Do the conversion of local vobs data to sqlite format.
# The sqlite files will be used to merge the data 

NDELAY=3

YMD=$1
YDAY=$(date -d "$YMD - $NDELAY days" +'%Y%m%d')
YYYY=${YDAY:0:4}
MM=${YDAY:4:2}
DD=${YDAY:6:2}


SDATE=${YYYY}${MM}${DD}00
EDATE=${YYYY}${MM}${DD}23

cd $HARP_DIR/pre_processing

for SOURCE in DMI IMO MARS; do
  CONFIG=config_dmi/config_$SOURCE.yml
  echo "Using $CONFIG"
  ./vobs2sql.R -start_date $SDATE -end_date $EDATE -config_file $CONFIG
done
