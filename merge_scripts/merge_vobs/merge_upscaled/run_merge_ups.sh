#!/bin/bash
# Call all files in date range indicated below.
# Assumming first file is old, second files is the new one.
#
set -x
year=2019
month=(06) #02 03 04 05 06 07 08 09 10 11 12)
fstep=6
fend=18
SRCDIR1=/netapp/dmiusr/aldtst/upscale/igb40h11
SRCDIR2=/netapp/dmiusr/aldtst/upscale/sgl40h11
SRCDIR3=/netapp/dmiusr/aldtst/upscale/tasii #vups18tasii201905302150
#updist1=('06' '12' '36')
#updist2=('20' '60' '120')
updist1=('06' )
updist2=('20' )
updist3=('20' )
pref1='igb40h11'
pref2='sgl40h11'
pref3='tasii'
resexp='gl_hm'
WORKDIR=/lustre/research/xiaohua/upscale/merge3

#using my conda installation:
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py36=/data/cap/miniconda2/envs/py37/bin/python

cd $WORKDIR
mkdir merged
for m in ${month[*]};do
  echo $m
  case $m in
    01|03|05|07|08|10|12)
        days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31)
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
            file1=$SRCDIR1/vups${updist1[i]}${pref1}$year$m${d}$hour$xx
            file2=$SRCDIR2/vups${updist2[i]}${pref2}$year$m${d}$hour$xx
            dtgtas=`$HOME/bin/mandtg $year$m$d$hour + -3 | cut -c1-10`
            #daytas=$(date +%Y%m%d -d "$year$m${d} - 1 day")
            #dtgtas=${daytas}21
            xx3=`expr $xx + 3`
            xx3=`perl -e "printf('%2.2i', $xx3)"`
            file3=$SRCDIR3/vups${updist3[i]}${pref3}$dtgtas$xx3
            fout=merged/vups${updist1[i]}${resexp}$year$m${d}$hour$xx
            if [[ ! -f $fout && -f ${file1} && -f ${file2} && -f ${file3} ]]; then
                echo "merging ${file1} and ${file2} and $file3"
                #clean extra spaces  
                awk '{$2=$2};1' $file1 > vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                awk '{$2=$2};1' $file2 > vups${updist2[i]}${pref2}$year$m${d}$hour$xx
                awk '{$2=$2};1' $file3 > vups${updist3[i]}${pref3}$dtgtas
                igbfile=vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                sglfile=vups${updist2[i]}${pref2}$year$m${d}$hour$xx
                tasfile=vups${updist3[i]}${pref3}$dtgtas
                $py36 ./merge_ups.py -f1 $igbfile  -f2 $sglfile,$tasfile -fo $fout
                rm -f $igbfile $sglfile $tasfile
            elif [[ ! -f $fout && -f ${file1} && -f ${file2} && ! -f ${file3} ]]; then
                echo "merging ${file1} and ${file2}"
                awk '{$2=$2};1' $file1 > vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                awk '{$2=$2};1' $file2 > vups${updist2[i]}${pref2}$year$m${d}$hour$xx
                igbfile=vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                sglfile=vups${updist2[i]}${pref2}$year$m${d}$hour$xx
                $py36 ./merge_ups.py -f1 $igbfile  -f2 $sglfile -fo $fout
                rm -f $igbfile $sglfile
            elif [[ ! -f $fout && -f ${file1} && ! -f ${file2} && -f ${file3} ]]; then
                echo "merging ${file1} and ${file3}"
                awk '{$2=$2};1' $file1 > vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                awk '{$2=$2};1' $file3 > vups${updist3[i]}${pref3}$dtgtas
                igbfile=vups${updist1[i]}${pref1}$year$m${d}$hour$xx
                tasfile=vups${updist3[i]}${pref3}$dtgtas
                $py36 ./merge_ups.py -f1 $igbfile  -f2 $tasfile -fo $fout
                rm -f $igbfile $tasfile
            elif [[ ! -f $fout && -f ${file1} && ! -f ${file2} && ! -f ${file3} ]]; then
                echo "copy the same ${file1} to the result directory"
                cp $file1 $fout
                rm -f $igbfile
            else
                echo "neither of the files available "
            fi
        done # xx
      done
     done # upscaling dist
    done
done
