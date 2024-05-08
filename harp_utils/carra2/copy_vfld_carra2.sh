#!/usr/bin/env bash
#SBATCH --error=danra_ecp_%j.err
#SBATCH --output=danra_ecp_%j.out
#SBATCH --job-name=danra_copy

DEF_USER=nhe
if [ -z $1 ]; then
  echo "Please provide stream and period"
  echo "Example: carra2_spinup 199201"
  echo "For ERA5 use ERA5 as stream: ERA5 199201"
  echo "Extra: add user as 3rd argument if stream not in $DEF_USER"
  exit 1
else
  STREAM=$1
  PERIOD=$2
  [ -z $3 ] && USER=$DEF_USER || USER=$3
fi

copy_CARRA2()
{
  DEST=/ec/res4/scratch/nhd/verification/vfld/CARRA2/$STREAM/
  ORIG=ec:/fac2/CARRA2/vfld/$STREAM/$PERIOD
  ecfsdir $ORIG $DEST/$PERIOD
  mv $DEST/$PERIOD/* $DEST
  rmdir $DEST/$PERIOD
  cd $DEST
  tar xvf vfld${STREAM}${PERIOD}.tar
  rm vfld${STREAM}${PERIOD}.tar
  for TB in vfld${STREAM}${PERIOD}*.tar.gz; do
    tar zxvf $TB
  done
  rm vfld${STREAM}${PERIOD}*.tar.gz  
  cd -
}

copy_ERA5()
{
  declare -i YYYY=${PERIOD:0:4}
  DEST=/ec/res4/scratch/nhd/verification/vfld/ERA5
  echo "$YYYY"
  [ ! -d $DEST ] && mkdir $DEST
  if [[ $YYYY <  2000 ]] ; then
    echo "Copying whole year $YYYY"
    [ -d $DEST/$YYYY ] && rmdir $DEST/$YYYY
    ecfsdir ec:/hirlam/oprint/ECMWF/ERA5/$YYYY $DEST/$YYYY
    mv $DEST/$YYYY/* $DEST
    rmdir $DEST/$YYYY
  else
  [ -d $DEST/$PERIOD ] && rmdir $DEST/$PERIOD
    ecfsdir ec:/hirlam/oprint/ECMWF/ERA5/$YYYY/$PERIOD $DEST/$PERIOD
    mv $DEST/$PERIOD/* $DEST
    rmdir $DEST/$PERIOD
  fi
}

if [ $STREAM == "ERA5" ]; then
  copy_ERA5
else 
  copy_CARRA2
fi
