#!/usr/bin/env bash
if [ $# -lt 2 ]; then
    echo "Please provide year and month (2022 01)"
    echo "optionally provide model Default: enea43h22opr"
    exit 1
  else
    YYYY=$1
    MM=$2
    MODEL=$3
    [ -z $MODEL ] && MODEL=enea43h22opr
fi


fetch_comeps()
{
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

fetch_model()
{
  DIR=$SCRATCH/verification/vfld/$MODEL
  [ ! -d $DIR ] &&  mkdir -p $DIR
  rsync -avz cperalta@hirlam.org:/data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL/vfld${MODEL}${YYYY}${MM}* $DIR/

}

if [ $MODEL == enea43h22opr ]; then

echo "Fetching comeps"
  fetch_comeps
else
echo "Fetching $MODEL"
  fetch_model
fi

