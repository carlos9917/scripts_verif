#!/usr/bin/env bash
if [ $# -ne 2 ]; then
    echo "Please provide year and month (2022 01)"
    exit 1
  else
    YYYY=$1
    MM=$2
fi
MODELS=(EC9 ecds_v2  enea43h22opr MEPS_prodmbr000  enea43h22mbr000  igb40h11)
for MODEL in ${MODELS[@]}; do
  DIR=./$MODEL/$YYYY
  [ ! -d $DIR ] &&  mkdir -p $DIR
  rsync -avz cperalta@hirlam.org:/data/www/project/portal/uwc_west_validation/DMI_vfld/FCTABLE/$MODEL/$YYYY/$MM/ ./$MODEL/$YYYY/$MM
done
