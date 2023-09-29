#!/usr/bin/env bash
# send the plots to hirlam or the linux vm with the shiny server

PLOTS_PATH=/ec/res4/scratch/nhd/verification/plots

road_models=(glatmodel R01 glatmodel_6h R01_6h R01_6h_redo glat_6h_redo)
RESULTS=$1
if [ -z $RESULTS ]; then
echo "Please provide the name of the project (ie, enea_intercomparison)"
echo "Alternatively include second argument with destination"
echo "vm = virtual server, else default is hirlam server"
exit 1
fi

if [ -z $2 ]; then
    echo "Sending plots to hirlam server"
    SERVER=cperalta@hirlam.org
    REMOTE_PATH=/data/www/project/portal/uwc_west_validation/DMI_vfld/plots_from_atos
elif [ $2 == "vm" ]; then
    echo "Sending plots to shiny vm"
    SERVER=tenantadmin@136.156.132.116
    REMOTE_PATH=/home/tenantadmin/verification/plots
fi
[ -z $RESULTS ] && RESULTS=enea43_intercomparison
DIR=$PLOTS_PATH/$RESULTS

if [[ ${road_models[@]} =~ $RESULTS ]]; then
  PLOTS_PATH=/ec/res4/scratch/nhd/verification/ROAD_MODEL/plots
  DIR=$PLOTS_PATH/$RESULTS
  echo "Sending plots under $DIR"
  rsync -avz $DIR/* $SERVER:$REMOTE_PATH/$RESULTS/
else
  echo "Sending plots under $DIR"
  rsync -avz $DIR/* $SERVER:$REMOTE_PATH/$RESULTS/
fi
