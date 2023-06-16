#!/usr/bin/env bash
ORIG=/data/www/project/portal/uwc_west_validation/DMI_vfld/glatmodel/FCTABLE
YM=$1
[ -z $YM ] && YM=202301
DEST=/ec/res4/scratch/nhd/verification/ROAD_MODEL/FCTABLE/glatmodel/${YM:0:4}/${YM:4:2}
echo "Transferring $YM from hirlam to $DEST"
for VAR in S10m T2m TROAD; do
   [ ! -d $DEST ] && mkdir -p $DEST
  scp cperalta@hirlam.org:$ORIG/FCTABLE_${VAR}_${YM}_??.sqlite $DEST
  #remove the files in the origin
  echo "Removing $VAR files with $YM in hirlam server"
  ssh cperalta@hirlam.org "cd $ORIG; rm -f FCTABLE_${VAR}_${YM}_??.sqlite"
done
