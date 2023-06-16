#!/usr/bin/env bash
DEST=/data/www/project/portal/uwc_west_validation/DMI_vfld/glatmodel/FCTABLE
echo $ORIG
YM=$1
[ -z $YM ] && YM=202301
echo "Doing $YM"
ORIG=/data/projects/glatmodel/verification/harp/FCTABLE/${YM:0:4}/${YM:4:2}
for VAR in S10m T2m TROAD; do
  scp $ORIG/FCTABLE_${VAR}_${YM}_??.sqlite cperalta@hirlam.org:$DEST
done
