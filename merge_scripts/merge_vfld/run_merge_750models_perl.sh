#!/bin/bash
# Call all files in date range indicated below.
# Assumming first file is old, second files is the new one.
#
#set -x
year=2019
month=(06) #02 03 04 05 06 07 08 09 10 11 12)
fstep=6
fend=18
SRCDIR=/netapp/dmiusr/aldtst/vfld
#SRCDIR1=/netapp/dmiusr/aldtst/vfld/igb40h11
#SRCDIR2=/netapp/dmiusr/aldtst/vfld/sgl40h11
#SRCDIR3=/netapp/dmiusr/aldtst/vfld/tasii #vups18tasii201905302150
pref1='tasii' #this one should always be tasii, to ensure it does the 3h displacement below
pref2='sgl40h11'
pref3='nuuk750' 
pref4='qaan40h11'
resexp='gl750'
WORKDIR=/home/cap/verify/scripts_verif/merge_scripts/merge_vfld
mergeddir=merged_750_test

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
            file1=vfld${pref1}$year$m${d}$hour$xx #taas, will be a link below
            file2=$SRCDIR/${pref2}/vfld${pref2}$year$m${d}$hour$xx #sgl
            file3=$SRCDIR/${pref3}/vfld${pref3}$year$m${d}$hour$xx #nuuk
            file4=$SRCDIR/${pref4}/vfld${pref4}$year$m${d}$hour$xx #qaan
            dtgtas=`$HOME/bin/mandtg $year$m$d$hour + -3 | cut -c1-10`
            #daytas=$(date +%Y%m%d -d "$year$m${d} - 1 day")
            #dtgtas=${daytas}21
            xx3=`expr $xx + 3`
            xx3=`perl -e "printf('%2.2i', $xx3)"`
            file1_tas=$SRCDIR/$pref1/vfld${pref1}$dtgtas$xx3 # tasii, which needs a 3 hour displacement
            ln -sf $file1_tas $file1
            fout=$mergeddir/vfld${resexp}$year$m${d}$hour$xx
            echo "file1 $file1"
            echo "file2 $file2"
            echo "file3 $file3"
            echo "file4 $file4"
            #need to determine which files are available below. 
            #gets more complicated with 4 files, but testing some options below...
            #maybe replace by python script to make choices easier to determine
            #NOTE: in the merge script the 1st file is the old, 2nd is the new,
            #new contents get preference. In this case all data must be 
            # non-overlapping, since all domains are non overlapping
            # Otherwise carefully select which data is to replace which
            # in the perl script order.
            if [[ ! -f $fout && -f ${file1} && -f ${file2} && -f ${file3} && -f ${file4} ]]; then
                echo "case1"
                echo "merging ${file1} and ${file2}"
                ./merge_vfld.pl $file1 $file2 tasii sgl40h11
                mv vfld$year$m${d}$hour${xx}.merged vfldtassgl$year$m${d}$hour${xx}
                echo "merging ${file3} and ${file4}"
                ./merge_vfld.pl $file3 $file4 nuuk750 qaan40h11
                rm -f vfldtassgl$year$m${d}$hour${xx}
                mv vfld$year$m${d}$hour${xx}.merged vfldnuuqaa$year$m${d}$hour${xx}
                rm -f vfldnuuqaa$year$m${d}$hour${xx}
                echo "merging vfldtassgl$year$m${d}$hour${xx} and vfldnuuqaa$year$m${d}$hour${xx}"
                ./merge_vfld.pl vfldtassgl$year$m${d}$hour${xx} vfldnuuqaa$year$m${d}$hour${xx} tassgl nuuqaa
                mv vfld$year$m${d}$hour${xx}.merged $fout
                exit
            elif [[ ! -f $fout && -f ${file1} && -f ${file2} && -f ${file3} && ! -f ${file4} ]]; then
                echo "case2"
                echo "merging ${file1} and ${file2}"
                ./merge_vfld.pl $file1 $file2 tasii sgl40h11
                mv vfld$year$m${d}$hour${xx}.merged vfldtassgl$year$m${d}$hour${xx}
                echo "merging ${file3} and vfldtassgl$year$m${d}$hour${xx}"
                ./merge_vfld.pl $file3 vfldtassgl$year$m${d}$hour${xx} nuuk750 tassgl
                rm -f vfldtassgl$year$m${d}$hour${xx}
                mv vfld$year$m${d}$hour${xx}.merged $fout
                exit
            elif [[ ! -f $fout && -f ${file1} &&  -f ${file2} && ! -f ${file3} && -f ${file4} ]]; then
                echo "case3"
                echo "merging ${file1} and ${file2}"
                ./merge_vfld.pl $file1 $file2 tasii sgl40h11
                cp vfld$year$m${d}$hour${xx}.merged vfldtassgl$year$m${d}$hour${xx}
                echo "merging ${file4} and vfldtassgl$year$m${d}$hour${xx}"
                ./merge_vfld.pl vfldtassgl$year$m${d}$hour${xx} $file4  tassgl qaan40h11
                #rm -f vfldtassgl$year$m${d}$hour${xx}
                cp vfld$year$m${d}$hour${xx}.merged $fout
                exit
            elif [[ ! -f $fout && -f ${file1} && ! -f ${file2} && -f ${file3} && -f ${file4} ]]; then
                echo "case4"
                echo "merging ${file1} and ${file3}"
                ./merge_vfld.pl $file1 $file3 tasii nuuk750
                mv vfld$year$m${d}$hour${xx}.merged vfldtasnuu$year$m${d}$hour${xx}
                echo "merging $file4 and vfldtasnuu$year$m${d}$hour${xx}"
                ./merge_vfld.pl $file4 vfldtasnuu$year$m${d}$hour${xx} qaan40h11 tasnuu
                rm -f vfldtasnuu$year$m${d}$hour${xx}
                mv vfld$year$m${d}$hour${xx}.merged $fout
                exit
            elif [[ ! -f $fout && -f ${file1} && -f ${file2} && ! -f ${file3} && ! -f ${file4} ]]; then
                echo "case5"
                echo "merging ${file1} and ${file2}"
                ./merge_vfld.pl $file1 $file2 tasii sgl40h11
                mv vfld$year$m${d}$hour${xx}.merged $fout
                exit
            elif [[ ! -f $fout && ! -f ${file1} && ! -f ${file2} && -f ${file3} && -f ${file4} ]]; then
                echo "case6"
                echo "merging ${file3} and ${file4}"
                ./merge_vfld.pl $file3 $file4 nuuk750 qaan40h11
                mv vfld$year$m${d}$hour${xx}.merged $fout
                exit
            else
                echo "neither of the files available (MISING OPTIONS) "
            fi
            rm -f $file1 #delete soft link for tasii
        done # xx
      done
     done # upscaling dist
    done
done
