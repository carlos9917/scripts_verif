#!/bin/bash
#Script to convert vobs/vfld files to verif ASCII format.
# Each variable is separated in a different file 
#
#It only works with files in vobs format 4 (convert files in format 2 with
# the other script!)
#
# First decide which variables are stored in each file by reading
# the header after second line:
# The header also indicates where the TEMP data (if any) starts.
# The first part is SYNOP data
#

SCRDIR=/home/cap/verify/scripts_verif
#VOBSDIR=/data/cap/VOBS
VOBSDIR=/data/cap/code_development_hpc/scripts_verif
BINDIR=$VOBSDIR
WRKDIR=/home/cap/tmp
CYINT=24

years=(2019) #(2017 2018)
month=(01) # 02 03 04 05 06 07 08 09 10 11 12)
#TMPDIR=$WRKDIR/wrk$$
#mkdir -p $TMPDIR

for year in ${years[*]}; do
  echo "processing year $year"

  for m in ${month[*]};do
    echo "Doing month $m"
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
  
  #VOBS_START=$year$m${d}00
  #VOBS_STOP=$year$m${d}23
  
Start=$year$m${d}00
Lastob=$year$m${d}23
  while [ $Start -le $Lastob ]
  do
    DATE=`$BINDIR/mandtg -date $Start`
    # 0. Read 1st line of header to determine:
    # n_synop  n_temp version_flag
    # 1. Read 2nd line to determine: n_vars (number of variables in file)
    #RESFIL=vobs$DATE
      for HH in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23; do
        vobsfile=$VOBSDIR/vobs$DATE$HH
        echo "Processing time $DATE$HH"
        #[ -s $VOBSDIR/vobs$DATE$HH ] && header=`head -1 $VOBSDIR/vobs$DATE$HH`
        header=`head -1 $vobsfile`
        nvars_synop=`awk 'NR==2' $vobsfile`
        read nsynop ntemp verflag <<< "$header"
        echo "nsynop $nsynop"
        echo "ntemp $ntemp"
        echo "verflag $verflag"
        echo "nvars_synop $nvars_synop"
        #lstart="(($nsynop - $nvars_synop))"
        #lstart=`echo "$nsynop - $nvars_synop" | bc`
        #create file with synop data
        let lstart="3 + $nvars_synop"
        let lend="$lstart + $nsynop - 1"
        let tmpstart="$lend + 1"
        echo "check lstart $lstart"
        awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile > synop$DATE$HH
        #create file with tmp data (if any)
        if [[ $ntemp -ne 0 ]]; then
          echo "Processing temp stations"
          nlevs_tmp=`awk -v a=$tmpstart 'NR == a' $vobsfile`
          let tmpstart="tmpstart+1"
          nvars_tmp=`awk -v a=$tmpstart 'NR == a' $vobsfile`
          let lstart="$nvars_synop + $nsynop + 5 + $nvars_tmp"
          let lend="lstart+$nlevs_tmp"
          echo "start/end for first tmp file: $lstart $lend"
          for i in   $(seq "$ntemp"); do
            lstart=$lend
            let lstart="lstart + 1"
            lend=$lstart
            let lend="lend + $nlevs_tmp"
            #echo "start/end for tmp $lstart $lend"
            awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile > temp_${i}_$DATE$HH
          done
        else 
          echo "no temp data in this file"
        fi
      done
    #awk 'NF>=4' t2m > t2m.tmp
    
    # this gives me only the number of lines and the list of vars
    # for SYNOP and TEMP
    #awk 'NF <= 2' vobs2019010100
   Start=`$BINDIR/mandtg $Start + $CYINT`
   echo start is $Start
  done #start /lastob
  done #days
  done #months
  done #year
  
