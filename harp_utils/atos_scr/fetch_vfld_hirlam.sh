#!/usr/bin/env bash
if [ $# -ne 2 ]; then
    echo "Please provide year and month (2022 01)"
    exit 1
  else
    YYYY=$1
    MM=$2
fi


fetch_comeps()
{
  MODEL=enea43h22opr
  DIR=$SCRATCH/verification/vfld/$MODEL
  [ ! -d $DIR ] &&  mkdir -p $DIR
  rsync -avz cperalta@hirlam.org:/data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL/vfld${YYYY}${MM}*.tgz $DIR/

  echo "removing the data from hirlam"
  ssh cperalta@hirlam.org "cd /data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL; rm -f vfld${YYYY}${MM}*.tgz"
  #now unpack locally
  cd $DIR
  for TAR in vfld${YYYY}${MM}*.tgz; do
    tar zxvf $TAR 
    rm $TAR
  done
}

fetch_comeps
