#!/usr/bin/env bash

# Upload some data to atos via hirlam
YYYY=2022
MM=11
FCT=/data/projects/nckf/danra/verification/FCTABLE
FCT_hirlam=/data/www/project/portal/uwc_west_validation/DMI_vfld/FCTABLE
MODELS=(EC9 ecds_v2  enea43h22opr MEPS_prodmbr000  enea43h22mbr000  igb40h11)
for MODEL in ${MODELS[@]}; do
 rsync -avz $FCT/$MODEL/$YYYY/$MM/* cperalta@hirlam.org:$FCT_hirlam/$MODEL/$YYYY/$MM/
done
