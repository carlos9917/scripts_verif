#!/usr/bin/env bash
#backup server
SERVER=tenantadmin@136.156.130.100
#SERVER=cperalta@hirlam.org
AVAIL_MODELS=(EC9 ecds_v2  enea43h22opr MEPS_prodmbr000  enea43h22mbr000  igb40h11)
AI_MODELS=(panguweather fourcastnet)
if [ $# -lt 2 ]; then
    echo "Please provide year and month (2022 01)"
    echo "optionally provide model Default: enea43h22opr"
    echo "Other models: ${AVAIL_MODELS[@]}"
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
  rsync -avz $SERVER:/data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL/vfld${YYYY}${MM}*.tgz $DIR/

  echo "removing the data from remote server $SERVER"
  ssh $SERVER "cd /data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL; rm -f vfld${YYYY}${MM}*.tgz"
  #now unpack locally
  cd $DIR
  for TAR in vfld${YYYY}${MM}*.tgz; do
    tar zxvf $TAR 
    rm $TAR
  done
}
ecp_ec9()
{
  DIR=$SCRATCH/verification/vfld/$MODEL
  ecp ec:/hlam/vfld_bologna/HRES/${YYYY}/${MM}/* 
  cd $DIR
  for TAR in *gz;  do
   tar zxvf $TAR 
   rm $TAR
  done
  cd -
}

fetch_model()
{
  DIR=$SCRATCH/verification/vfld/$MODEL
  [ ! -d $DIR ] &&  mkdir -p $DIR
  rsync -avz $SERVER:/data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL/vfld${MODEL}${YYYY}${MM}* $DIR/
  echo "removing the data from $SERVER"
  ssh $SERVER "cd /data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL; rm -f vfld${MODEL}${YYYY}${MM}*"
  if [ $MODEL == MEPS_prodmbr000 ]; then
    cd $DIR 
    for TAR in *.tar.gz; do
      tar zxvf $TAR
      rm $TAR
    done    
  fi

}

fetch_ai_model()
{
  DIR=$SCRATCH/verification/vfld/$MODEL
  [ ! -d $DIR ] &&  mkdir -p $DIR
  rsync -avz $SERVER:/data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL/${YYYY}${MM}* $DIR
  echo "removing the $MODEL data from $SERVER"
  ssh $SERVER "cd /data/www/project/portal/uwc_west_validation/DMI_vfld/$MODEL; rm -rf ${YYYY}${MM}*"
}

if [[ ${AI_MODELS[@]} =~ $MODEL ]]; then
  fetch_ai_model
  exit 0
fi

if [[ $MODEL == enea43h22opr ]] || [[ $MODEL == comeps ]]; then
MODEL=enea43h22opr
echo "Fetching comeps ($MODEL)"
  fetch_comeps
else
echo "Fetching $MODEL"
  fetch_model
fi

