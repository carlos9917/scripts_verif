#!/usr/bin/env bash

# Do the conversion of vfld data to sqlite format.

YMD=$1
MODEL=$2

# do it from 2 days ago to yesterday, since today there is no data
YDAY=$(date -d "$YMD - 2 days" +'%Y%m%d')
YYYY=${YDAY:0:4}
MM=${YDAY:4:2}
DD=${YDAY:6:2}
SDATE=${YYYY}${MM}${DD}

YDAY=$(date -d "$YMD - 1 days" +'%Y%m%d')
YYYY=${YDAY:0:4}
MM=${YDAY:4:2}
DD=${YDAY:6:2}
EDATE=${YYYY}${MM}${DD}

cd $HARP_DIR/pre_processing
CONFIG=config_dmi/config_$MODEL.yml
echo "Using $CONFIG"
./vfld2sql.R -start_date $SDATE -end_date $EDATE -config_file $CONFIG
