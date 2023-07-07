#!/usr/bin/env bash

HIRLAM_PATH=/data/www/project/portal/uwc_west_validation/DMI_vfld/plots_from_atos
PLOTS_PATH=/ec/res4/scratch/nhd/verification/plots

RESULTS=$1
[ -z $RESULTS ] && RESULTS=enea43_intercomparison
DIR=$PLOTS_PATH/$RESULTS
echo "Sending plots under $DIR"
if [ $RESULTS != glatmodel ]; then
  rsync -avz $DIR/* cperalta@hirlam.org:$HIRLAM_PATH/$RESULTS/
else
  PLOTS_PATH=/ec/res4/scratch/nhd/verification/ROAD_MODEL/plots
  DIR=$PLOTS_PATH/$RESULTS
  rsync -avz $DIR/* cperalta@hirlam.org:$HIRLAM_PATH/$RESULTS/
fi
