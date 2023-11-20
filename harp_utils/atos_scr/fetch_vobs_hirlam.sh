#!/usr/bin/env bash
#backup server
SERVER=tenantadmin@136.156.130.100
#SERVER=cperalta@hirlam.org

VOBS=(DMI IMO MARS)
if [ $# -lt 2 ]; then
    echo "Please provide year and month (2022 01)"
    exit 1
  else
    YYYY=$1
    MM=$2
fi


fetch_vobs()
{
  DIR=$SCRATCH/verification/DMI_data/vobs/$CENTER
  [ ! -d $DIR ] &&  mkdir -p $DIR
  echo "Destination: $DIR"
  rsync -avz $SERVER:/data/www/project/portal/uwc_west_validation/DMI_vfld/vobs/$CENTER/vobs${YYYY}${MM}* $DIR/
  echo "removing the data from hirlam"
  ssh $SERVER "cd /data/www/project/portal/uwc_west_validation/DMI_vfld/vobs/$CENTER; rm -f vobs${YYYY}${MM}*"

}
if [ -z $3 ]; then
   echo "Doing all ${VOBS[@]}"
   for CENTER in ${VOBS[@]}; do
     echo "Fetching $CENTER"
     fetch_vobs
   done
else
   CENTER=$3
   echo "Doing ${CENTER}"
   fetch_vobs
fi
