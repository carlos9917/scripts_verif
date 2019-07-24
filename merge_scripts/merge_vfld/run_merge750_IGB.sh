#!/bin/bash
# Call all files in date range indicated below.
# Assumming first file is old, second files is the new one.
#
#set -x
year=2019
month=(06) #02 03 04 05 06 07 08 09 10 11 12)
fstep=6
fend=18
SRCDIR1=/netapp/dmiusr/aldtst/vfld/igb40h11
SRCDIR2=/netapp/dmiusr/aldtst/vfld/sgl40h11
SRCDIR3=/netapp/dmiusr/aldtst/vfld/tasii #vups18tasii201905302150
updist1=('06' )
updist2=('20' )
updist3=('20' )
pref1='igb40h11'
pref2='sgl40h11'
pref3='tasii'
resexp='opr_gl'
WORKDIR=/data/cap/merge_upscale/mergevfld_750_models/
mergeddir=merged_june

#using my conda installation:
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py36=/data/cap/miniconda2/envs/py37/bin/python

cd $WORKDIR
mkdir $mergeddir
for m in ${month[*]};do
  echo $m
  case $m in
    01|03|05|07|08|10|12)
        days=(01 02 03 04 05  06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31)
    ;;
    02)
       #Evaluation for leap years from https://bash.cyberciti.biz/time-and-date/find-whether-year-ls-leap-or-not/
       if [ $((year % 4)) -ne 0 ];then
           days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28)
       elif [ $((year % 400)) -eq 0 ];then
           days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29)
       elif [ $((year % 100)) -eq 0 ];then
           days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28)
       else
           days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29)
       fi
    ;;
    04|06|09|11)
       days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30)
    ;;
    esac
    for d in ${days[*]};do
      for i in {0..0}; do

      for hour in `seq -w 0 ${fstep} ${fend}`; do
          echo "hour $hour"
          for xx in `seq -w 0 51`; do
            file1=$SRCDIR1/vfld${pref1}$year$m${d}$hour$xx
            file2=$SRCDIR2/vfld${pref2}$year$m${d}$hour$xx
            dtgtas=`$HOME/bin/mandtg $year$m$d$hour + -3 | cut -c1-10`
            #daytas=$(date +%Y%m%d -d "$year$m${d} - 1 day")
            #dtgtas=${daytas}21
            xx3=`expr $xx + 3`
            xx3=`perl -e "printf('%2.2i', $xx3)"`
            file3=$SRCDIR3/vfld${pref3}$dtgtas$xx3
            fout=$mergeddir/vfld${resexp}$year$m${d}$hour$xx
            if [[ ! -f $fout && -f ${file1} && -f ${file2} && -f ${file3} ]]; then
                echo "merging ${file1} and ${file2} and $file3"
                #split data
                /bin/bash splitvfld.sh $file1 igb40h11
                /bin/bash splitvfld.sh $file2 sgl40h11
                /bin/bash splitvfld.sh $file3 tasii
                $py36 merge_750models_IGB.py -fIGB_synop igb40h11_tmp/synopData -f750_synop sgl40h11_tmp/synopData,tasii_tmp/synopData -fo $fout
                rm -rf $WORKDIR/igb40h11_tmp
                rm -rf $WORKDIR/sgl40h11_tmp
                rm -rf $WORKDIR/tasii_tmp
            elif [[ ! -f $fout && -f ${file1} && -f ${file2} && ! -f ${file3} ]]; then
                echo "merging ${file1} and ${file2}"
                /bin/bash splitvfld.sh $file1 igb40h11
                /bin/bash splitvfld.sh $file2 sgl40h11
                $py36 merge_750models_IGB.py -fIGB_synop igb40h11_tmp/synopData -f750_synop sgl40h11_tmp/synopData -fo $fout
                rm -rf $WORKDIR/igb40h11_tmp
                rm -rf $WORKDIR/sgl40h11_tmp
            elif [[ ! -f $fout && -f ${file1} && ! -f ${file2} && -f ${file3} ]]; then
                echo "merging ${file1} and ${file3}"
                /bin/bash splitvfld.sh $file1 igb40h11
                /bin/bash splitvfld.sh $file3 tasii
                $py36 merge_750models_IGB.py -fIGB_synop igb40h11_tmp/synopData -f750_synop tasii_tmp/synopData -fo $fout
                rm -rf $WORKDIR/igb40h11_tmp
                rm -rf $WORKDIR/tasii_tmp
            elif [[ ! -f $fout && -f ${file1} && ! -f ${file2} && ! -f ${file3} ]]; then
                echo "copying the same ${file1} to the result directory"
                cp $file1 $fout
            else
                echo "neither of the files available "
            fi
        done # xx
      done
     done # upscaling dist
    done
done
