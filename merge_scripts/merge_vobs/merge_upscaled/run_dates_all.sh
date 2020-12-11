#!/bin/bash
# Call all files in date range indicated below.
# Assumming first file is old, second files is the new one.
#
year=2019
month=(01) #02 03 04 05 06 07 08 09 10 11 12)
fstep=3
fend=23
SRCDIR1=/netapp/dmiusr/aldtst/upscale/igb40h11
SRCDIR2=/netapp/dmiusr/aldtst/upscale/sgl40h11
updist1=('06' '12' '36')
updist2=('20' '60' '120')
pref1='igb40h11'
pref2='sgl40h11'
WORKDIR=/home/cap/scripts/convert_obs2_obs4/Combine_data_ver4/merge_upscaled

cd $WORKDIR
for m in ${month[*]};do
  echo $m
  case $m in
    01|03|05|07|08|10|12)
        days=(01) # 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31)
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
      for i in {0..2}; do

      for hour in `seq -w 0 ${fstep} ${fend}`; do
          echo "hour $hour"
          for xx in `seq -w 0 66`; do
              echo "upscaling ${updist1[i]}"
            ln -sf $SRCDIR1/vups${updist1[i]}${pref1}$year$m${d}$hour$xx vups${updist1[i]}${pref1}$year$m${d}$hour$xx
            ln -sf $SRCDIR2/vups${updist2[i]}${pref2}$year$m${d}$hour$xx vups${updist2[i]}${pref2}$year$m${d}$hour$xx
            file1=vups${updist1[i]}${pref1}$year$m${d}$hour$xx
            file2=vups${updist2[i]}${pref2}$year$m${d}$hour$xx
            if [[ -f ${file1} && -f ${file2} ]]; then
            echo "merging ${file1} and ${file2}"
            else
                echo "One of the files not available "
            fi
            ./merge_vobs_ver2.pl ${file1} ${file2}
            mv vobs$year$m${d}${hour}.merged vobs$year$m${d}$hour
            rm -f $file1 #delete the soft link
            rm -f $file2 #delete the soft link
        done # xx
      done
     done # upscaling dist
    done
done
