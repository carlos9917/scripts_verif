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

#VOBSDIR=/data/cap/VOBS
#VFLDDIR=/data/xiaohua/vfld/nea40h11
VFLDDIR=/data/cap/code_development_hpc/scripts_verif
VOBSDIR=/data/cap/code_development_hpc/scripts_verif
#BINDIR=/home/cap/verify/scripts_verif
BINDIR=/data/cap/code_development_hpc/scripts_verif
WRKDIR=/data/cap/tmp
CYINT=24
EXP=nea40h11
FINI="00"

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
  
  
Start=$year$m${d}00
Lastob=$year$m${d}23
  while [ $Start -le $Lastob ]
  do
    DATE=`$BINDIR/mandtg -date $Start`
    # 0. Read 1st line of header to determine:
    # n_synop  n_temp version_flag
    # 1. Read 2nd line to determine: n_vars (number of variables in file)
      for HH in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23; do
        TMPDIR=$WRKDIR/data_$DATE$HH
        mkdir -p $TMPDIR
        vobsfile=$VOBSDIR/vobs$DATE$HH
        vfldfile=$VFLDDIR/vfld$EXP$DATE${FINI}${HH}
        #echo "Processing time $DATE$HH"
        #echo "vobs and vfld files "
        #echo $vobsfile
        #echo $vfldfile
        #FOR VOBS file:
        header=`head -1 $vobsfile`
        read nsynop ntemp verflag <<< "$header"
        nvars_synop=`awk 'NR==2' $vobsfile`


        #create file with synop data from VOBS
        echo "Processing synop data for VOBS"
        let lstart="3 + $nvars_synop"
        let lend="$lstart + $nsynop - 1"
        let vend="$lstart - 1"
        let tmpstart="$lend + 1"
        #this one prints the data and 2nd awk gets rid of undesirable extra spaces!
        awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1' > $TMPDIR/synopOBSData_$DATE$HH
        awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1'  > $TMPDIR/synopOBSVars_$DATE$HH

        #create temporary file(s) with tmp data (if any)
        if [[ $ntemp -ne 0 ]]; then
          echo "Processing $ntemp temp stations for VOBS"
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
            awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile > $TMPDIR/tempOBS_${i}_$DATE$HH
          done
        else 
          echo "no temp data in this VOBS file"
        fi

        #FOR VFLD file:
        header=`head -1 $vfldfile`
        nvars_synop=`awk 'NR==2' $vfldfile`
        read nsynop ntemp verflag <<< "$header"

        #create file with synop data from VFLD
        echo "Processing synop data for VFLD"
        let lstart="3 + $nvars_synop"
        let lend="$lstart + $nsynop - 1"
        let vend="$lstart - 1"
        let tmpstart="$lend + 1"
        awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile |  awk '{$2=$2};1' > $TMPDIR/synopEXPData_$DATE$HH
        awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopEXPVars_$DATE$HH

        #create temporary file(s) with tmp data (if any)
        if [[ $ntemp -ne 0 ]]; then
          echo "Processing $ntemp temp stations for VFLD"
          nlevs_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
          let tmpstart="tmpstart+1"
          nvars_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
          let lstart="$nvars_synop + $nsynop + 5 + $nvars_tmp"
          let lend="lstart+$nlevs_tmp"
          for i in   $(seq "$ntemp"); do
            lstart=$lend
            let lstart="lstart + 1"
            lend=$lstart
            let lend="lend + $nlevs_tmp"
            awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile > $TMPDIR/tempEXP_${i}_$DATE$HH
          done
        else 
          echo "no temp data in this VFLD file"
        fi

      done # hour loop
   #Call the python script to convert data for this hour  
   #SCRIPT HERE:
   #Delete the directories no longer needed for this date
   #rm -rf $WRKDIR/data_${DATE}*

   Start=`$BINDIR/mandtg $Start + $CYINT`
   echo start is $Start
  done #start /lastob
  done #days
  done #months
  done #year
  
