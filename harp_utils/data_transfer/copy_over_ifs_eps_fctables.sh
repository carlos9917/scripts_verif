#!/usr/bin/env bash

# Copying locally some of the EPS data from the IFS model to compare with COMEPS

MODEL=IFSENS
DEST=$SCRATCH/verification/DMI_data/FCTABLE/$MODEL
[ ! -d $DEST ] && mkdir -p $DEST
YYYY=2022
MM=12
ecp ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/* $DEST/
