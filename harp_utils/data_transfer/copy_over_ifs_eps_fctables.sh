#!/usr/bin/env bash

# Copying locally some of the EPS data from the IFS model to compare with COMEPS

MODEL=IFSENS
YYYY=2022
MM=12
DEST=$SCRATCH/verification/DMI_data/FCTABLE/$MODEL/$YYYY/$MM
[ ! -d $DEST ] && mkdir -p $DEST
FILES=$(els ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/*)

for F in ${FILES[@]}; do
 [ ! -f $DEST/$F ] && ecp ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/$F $DEST/
done

cd $DEST
for TAR in *tar.gz;do
  tar zxvf $TAR
  rm $TAR  
done
