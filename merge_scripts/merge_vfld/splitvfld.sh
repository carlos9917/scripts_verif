#!/bin/bash
#
# Script to split a vfld file into SYNOP and TEMP data.
# This way it is easier to feed the data to the python script
# which compares the data
# NOTE: Call the python script ONLY from this wrapper!
#
#
#
#export PATH=/data/cap/miniconda2/bin:$PATH
#source activate py37
#py36=/data/cap/miniconda2/envs/py37/bin/python


if [ $# -eq 2 ] ; then
  vfldfile=$1  # file name
  model=$2 #model
else
  echo "Please provide file and model name"
  echo "Example: /netapp/dmiusr/aldtst/vfld/igb40h11/vfldigb40h11201907150310 igb40h11"
    exit 1
fi

TMPDIR=${model}_tmp
echo "Splitting file $vfldfile in directory $TMPDIR"
#FOR VFLD file:
header=`head -1 $vfldfile`
nvars_synop=`awk 'NR==2' $vfldfile`
read nsynop ntemp verflag <<< "$header"

rm -rf $TMPDIR #Delete it if it is there!
#create file with synop data from VFLD
mkdir $TMPDIR 
#echo "Processing $nsynop synop stations for $1"
let lstart="3 + $nvars_synop"
let lend="$lstart + $nsynop - 1"
let vend="$lstart - 1"
let tmpstart="$lend + 1"
awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile |  awk '{$2=$2};1' > $TMPDIR/synopData
#awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopVars
awk -v b="$vend" 'NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopVars
#awk -v b="$lend" 'NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopData
#create temporary file(s) with tmp data (if any)
if [[ $ntemp -ne 0 ]]; then
  #echo "Processing $ntemp temp stations for VFLD"
  nlevs_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
  #echo "nlevs_tmp $nlevs_tmp"
  let tmpstart="tmpstart+1"
  nvars_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
  #echo "nvars_tmp $nvars_tmp"
  let lstart="2+ $nvars_synop + $nsynop + 2 + $nvars_tmp + 1"
  let lend="lstart+$nlevs_tmp"
  for i in   $(seq "$ntemp"); do
    #echo $lstart $lend
    awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile >> $TMPDIR/tempData
    lstart=$lend
    let lstart="lstart + 1"
    lend=$lstart
    let lend="lend + $nlevs_tmp"
  done
fi

#print the name of the synop output file, the name of the temp output file and the number of temp stations
#echo $TMPDIR/synopData $TMPDIR/tempData $ntemp
