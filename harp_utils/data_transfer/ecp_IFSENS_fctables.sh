#!/usr/bin/env bash
#SBATCH --error=ifs_%j.err
#SBATCH --output=ifs_%j.out
#SBATCH --job-name=ecp_ifsens



# Copying locally some of the EPS data from the IFS model to compare with COMEPS

MODEL=IFSENS
YYYY=2023
MM=01
if [[ -z $1 ]]; then
   echo "Please provide YYYY and MM"
   exit 1
else
   YYYY=$1
   MM=$2
fi


DEST=$SCRATCH/verification/DMI_data/FCTABLE/$MODEL/$YYYY/$MM
[ ! -d $DEST ] && mkdir -p $DEST
FILES=$(els ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/*)

for F in ${FILES[@]}; do
 [ ! -f $DEST/$F ] && ecp ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/$F $DEST/
 #ecp ec:/hlam/harp_bologna/FCTABLE/IFSENS/$YYYY/$MM/$F $DEST/
done

cd $DEST
for TAR in *tar.gz;do
  tar zxvf $TAR
  rm $TAR  
done
