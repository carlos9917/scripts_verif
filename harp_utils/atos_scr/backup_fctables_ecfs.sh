#!/usr/bin/env bash

MODEL=$1
YYYY=$2
MM=$3

cd $SCRATCH/verification/DMI_data/FCTABLE

ECP=ec:verification/FCTABLE/$MODEL
cd $MODEL/$YYYY/$MM
emkdir -p $ECP/$YYYY/$MM
for F in FC*; do
  readarray -d _ -t SPLIT <<< "$F"
  VAR=${SPLIT[1]}
  YYYYMM=${SPLIT[2]}
  TARBALL=FCT-${MODEL}-${VAR}-${YYYYMM}.tgz
  [ ! -f $TARBALL ] && tar czvf $TARBALL FCTABLE_${VAR}_*
  ecp $TARBALL $ECP/$YYYY/$MM
  rm $TARBALL
done
cd -
rm -rf $SCRATCH/verification/DMI_data/FCTABLE/$MODEL/$YYYY/$MM
