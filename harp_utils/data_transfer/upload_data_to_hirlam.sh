#!/usr/bin/env bash

# Upload some data to atos via hirlam
if [ $# -lt 2 ]; then
    echo "Please provide year and month (2022 01)"
    exit 1
  else
    YYYY=$1
    MM=$2
    if [ -z $3 ]; then
      MODEL=vobs
    else
      MODEL=$3
    fi	
fi

FCT=/data/projects/nckf/danra/verification/FCTABLE
OBS=/data/projects/nckf/danra/vfld/vobs_to_merge/OBSTABLE_MERGED
FCT_hirlam=/data/www/project/portal/uwc_west_validation/DMI_vfld/FCTABLE
OBS_hirlam=/data/www/project/portal/uwc_west_validation/DMI_vfld/OBSTABLE

if [ -z $MODEL ] ; then
   MODELS=(EC9 ecds_v2  enea43h22opr MEPS_prodmbr000  enea43h22mbr000  igb40h11)
   for MODEL in ${MODELS[@]}; do
      rsync -avz $FCT/$MODEL/$YYYY/$MM/ cperalta@hirlam.org:$FCT_hirlam/$MODEL/$YYYY/$MM
   done
else
     if [ $MODEL == vobs ]; then	
       rsync -avz $OBS/ cperalta@hirlam.org:$OBS_hirlam
     else	     
       rsync -avz $FCT/$MODEL/$YYYY/$MM/ cperalta@hirlam.org:$FCT_hirlam/$MODEL/$YYYY/$MM
     fi
fi
