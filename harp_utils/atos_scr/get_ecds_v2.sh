#!/usr/bin/env bash
MODEL=ecds_v2
D1=20230110
D2=20230121
TODO=1
if [ $# -ne 3 ]; then
    echo "Please provide first and last date (ie, $D1 $D2)"
    echo "Optionall indicate if send to DMI (1: send to DMI, 2: copy here, 3: fetch from ecfs. Default: $TODO)"
    exit 1
  else
    D1=$1
    D2=$2
    TODO=$3
    [ -z $TODO ] && TODO=1
fi


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

copy_unpack_locally() 
{
  [ ! -d $DEST ] && mkdir -p $DEST
  for D in $(seq $D1 $D2); do
   cp $DATA/vfld${MODEL}${D}??.tar.gz $DEST
  done
  cd $DEST
  for TAR in *.tar.gz; do
   tar zxvf $TAR
   rm $TAR   
  done
  cd -
}

fetch_ecfs()
{
  YYYY=${D1:0:4}
  MM=${D1:4:2}
  echo "Fetching tarball for $YYYY $MM"
  PACK=vfldecds_v2${YYYY}${MM}.tar
  echo "Copying $PACK to $DEST"
  [ ! -f $DEST/$PACK ] && ecp ec:/duuw/harmonie/ecds_v2/vfld/$PACK $DEST
  cd $DEST
  for DATE in $(seq $D1 $D2); do  
   tar xvf $PACK vfldecds_v2${DATE}??.tar.gz
   for TAR in vfldecds_v2${DATE}??.tar.gz; do
     tar zxvf $TAR
     rm $TAR
   done
  done
  rm $PACK
  cd -
}

[ $TODO == 1 ] && copy_and_send
[ $TODO == 2 ] && copy_unpack_locally
[ $TODO == 3 ] && fetch_ecfs
