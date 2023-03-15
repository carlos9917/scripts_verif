#!/usr/bin/env bash
if [ $# -ne 1 ]; then
    echo "Please provide year (2023)"
    exit 1
  else
    YYYY=$1
fi
DIR=$SCRATCH/verification/DMI_data/OBSTABLE

[ ! -d $DIR ] &&  mkdir -p $DIR
rsync -avz cperalta@hirlam.org:/data/www/project/portal/uwc_west_validation/DMI_vfld/OBSTABLE/ $DIR/


