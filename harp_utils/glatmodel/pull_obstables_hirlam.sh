#!/usr/bin/env bash
ORIG=/data/www/project/portal/uwc_west_validation/DMI_vfld/glatmodel/OBSTABLE
DEST=/ec/res4/scratch/nhd/verification/ROAD_MODEL/OBSTABLE
for VAR in S10m T2m TROAD; do
  scp cperalta@hirlam.org:$ORIG/OBSTABLE_${VAR}_2023.sqlite $DEST
done
