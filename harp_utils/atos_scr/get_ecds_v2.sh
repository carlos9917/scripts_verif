#!/usr/bin/env bash
MODEL=ecds_v2
D1=20230110
D2=20230121
DATA=/ec/res4/hpcperm/duuw/hm_home/ecds_v2/parchive/archive/extract/
DEST=/ec/res4/scratch/nhd/verification/vfld/$MODEL

copy_and_unpack() 
{
  [ ! -d $DEST ] && mkdir -p $DEST
  for D in $(seq $D1 $D2); do
   cp $DATA/vfld${MODEL}${D}??.tar.gz $DEST
   cd $DEST 
   for TB in *.tar.gz; do
     tar zxvf $TB
     rm $TB
   done
   cd -
  done

}
copy_and_send() 
{
#pack to send back to DMI
  [ ! -d $DEST ] && mkdir -p $DEST
  for D in $(seq $D1 $D2); do
   cp $DATA/vfld${MODEL}${D}??.tar.gz $DEST
  done
  cd $DEST
  tar czvf vfld_${MODEL}_${D1}_${D2}.tgz *.tar.gz
  $HOME/bin/send_with_ectrans.sh vfld_${MODEL}_${D1}_${D2}.tgz
}

copy_and_send
