#!/bin/bash
# Process al models and init times at once
#
# Script to convert vobs/vfld files to verif ASCII format.
# Each variable is separated in a different file by the bash process.
# The script calls a python code at the end to convert the data to
# a verif-compatible ASCII format
#
# It only works with files in vobs format 4 (convert files in format 2 with
# the python script!)
#
# First read the first line to determine number of synop and temp variables in file
# Then decide which variables are stored in each file by reading
# the header after second line.
# The header also indicates where the TEMP data (if any) starts.
# The first part of the file contains the SYNOP data
#
# Output:
# The files are split into a synopEXPData_YYYYMMDDFI (FI forecast initial hour)
# and synopOBS_YYYYMMDDFI for vlfd/vobs
# Additionally, an extra Vars file contains the list of variables in each file
# (essentially the header).
# The data is placed into directories data_YYYYMMDDFI
# Separate files are created for the TEMP data (one per station)
#
# CURRENTLY only working for Surface data, but the TEMP data
# is already being split into separate files
# No functionality for adding the TEMP data into the verif files
# is included yet in the python script (since verif cannot
# handle TEMP data yet, only surface stations!)
#
#
#Function to determine days in the month:
days_in_month ()
{
    echo "Doing month $m"
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
         #days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30)
         days=(01 02 03)
      ;;
      esac
}

#using my conda installation:
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py36=/data/cap/miniconda2/envs/py37/bin/python
#EXP=EC9 #nea40h11 #CHANGE
#for hpc:
VOBSDIR=/data/cap/VOBS
BINDIR=/home/cap/verify/scripts_verif
#for my local expts:
#VFLDDIR=/data/cap/code_development_hpc/scripts_verif
#VOBSDIR=/data/cap/code_development_hpc/scripts_verif
#BINDIR=/data/cap/code_development_hpc/scripts_verif
CYINT=24 # CHANGE, for example for EC9
hour_ini=00 #use 2 digits for defining the Start and Lastob properly
hour_end=23
rvfld=True #CHANGE. if True, will reduce the file size. If False, it will only split the files
            # This last option is useful to examine the file contents.
years=(2019) #(2017 2018)
month=(05) # 02 03 04 05 06 07 08 09 10 11 12)#
models=(nea40h11) # igb40h11)
#models=(EC9)
init_hours=(00 06 12 18)
stnlist=/home/cap/verify/scripts_verif/stngreenland.dat
region=Greenland


for EXP in ${models[@]}; do
  WRKDIR=/data/cap/vfld_reduced/$region/$EXP
  VFLDDIR=/data/xiaohua/vfld/$EXP
  mkdir -p $WRKDIR || exit
  echo "doing model $EXP"
  for FINI in ${init_hours[@]}; do
  
    echo "doing init hour $FINI"

    for year in ${years[*]}; do
      echo "processing year $year"
    
      for m in ${month[*]};do
    
      days_in_month #calculates days[*]
    
      for d in ${days[*]};do
      
      
      Start=$year$m${d}${hour_ini}
      Lastob=$year$m${d}${hour_end}
      echo "Start and Last hours to analyze: $Start $Lastob"
      while [ $Start -le $Lastob ]
      do
        DATE=`$BINDIR/mandtg -date $Start`
        # 0. Read 1st line of header to determine:
        # n_synop  n_temp version_flag
        # 1. Read 2nd line to determine: n_vars (number of variables in file)
        echo "Doing date $DATE" 
          for HH in `seq -w $hour_ini $hour_end`; do
            echo "Doing hour $HH"
            TMPDIR=$WRKDIR/data_$DATE$HH$FINI
            mkdir -p $TMPDIR
            #vobsfile=$VOBSDIR/vobs$DATE$HH
            vfldfile=$VFLDDIR/vfld$EXP$DATE${FINI}${HH}
            #header=`head -1 $vobsfile`
            #read nsynop ntemp verflag <<< "$header"
            #nvars_synop=`awk 'NR==2' $vobsfile`
    
    
            #create file with synop data from VOBS
            #echo "Processing $nsynop synop stations for VOBS"
            #let lstart="3 + $nvars_synop"
            #let lend="$lstart + $nsynop - 1"
            #let vend="$lstart - 1"
            #let tmpstart="$lend + 1"
            #this one prints the data and 2nd awk gets rid of undesirable extra spaces!
            #awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1' > $TMPDIR/synopOBSData_$DATE$HH
            #awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1'  > $TMPDIR/synopOBSVars_$DATE$HH
    
            #create temporary file(s) with tmp data (if any)
            #if [[ $ntemp -ne 0 ]]; then
            #  echo "Processing $ntemp temp stations for VOBS"
            #  nlevs_tmp=`awk -v a=$tmpstart 'NR == a' $vobsfile`
            #  let tmpstart="tmpstart+1"
            #  nvars_tmp=`awk -v a=$tmpstart 'NR == a' $vobsfile`
            #  let lstart="$nvars_synop + $nsynop + 5 + $nvars_tmp"
            #  let lend="lstart+$nlevs_tmp"
            #  #echo "start/end for first tmp file: $lstart $lend"
            #  for i in   $(seq "$ntemp"); do
            #    lstart=$lend
            #    let lstart="lstart + 1"
            #    lend=$lstart
            #    let lend="lend + $nlevs_tmp"
            #    #echo "start/end for tmp $lstart $lend"
            #    awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile > $TMPDIR/tempOBS_${i}_$DATE$HH
            #  done
            #else 
            #  echo "no temp data in this VOBS file"
            #fi
    
            #FOR VFLD file:
            header=`head -1 $vfldfile`
            nvars_synop=`awk 'NR==2' $vfldfile`
            read nsynop ntemp verflag <<< "$header"
    
            #create file with synop data from VFLD
            echo "Processing $nsynop synop stations for VFLD"
            let lstart="3 + $nvars_synop"
            let lend="$lstart + $nsynop - 1"
            let vend="$lstart - 1"
            let tmpstart="$lend + 1"
            awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile |  awk '{$2=$2};1' > $TMPDIR/synopEXPData_$DATE$HH
            awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopEXPVars_$DATE$HH
    
            #create temporary file(s) with tmp data (if any)
            #if [[ $ntemp -ne 0 ]]; then
            #  echo "Processing $ntemp temp stations for VFLD"
            #  nlevs_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
            #  let tmpstart="tmpstart+1"
            #  nvars_tmp=`awk -v a=$tmpstart 'NR == a' $vfldfile`
            #  let lstart="$nvars_synop + $nsynop + 5 + $nvars_tmp"
            #  let lend="lstart+$nlevs_tmp"
            #  for i in   $(seq "$ntemp"); do
            #    lstart=$lend
            #    let lstart="lstart + 1"
            #    lend=$lstart
            #    let lend="lend + $nlevs_tmp"
            #    awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile > $TMPDIR/tempEXP_${i}_$DATE$HH
            #  done
            #else 
            #  echo "no temp data in this VFLD file"
            #fi
          #Call the python script to convert SYNOP data for this hour  
          #if [ $cverif == True ]; then
          # echo "Conversion to verif format"
          # $py36 $BINDIR/vobs2verif.py -v 'TT' -vvobs $TMPDIR/synopOBSVars_$DATE$HH -vexp $TMPDIR/synopEXPVars_$DATE$HH
          # $py36 $BINDIR/vobs2verif.py -v 'FF' -vvobs $TMPDIR/synopOBSVars_$DATE$HH -vexp $TMPDIR/synopEXPVars_$DATE$HH
          # #Delete the directories no longer needed for this date
          # rm -rf $WRKDIR/data_${DATE}??
          if [ $rvfld == True ]; then
           echo "Reducing vlfd file $vfldfile"
            chead=`head -1 $vfldfile`
            read num_synop stuff stuff <<< "$chead"
            echo "NSYNOP before reduction: $num_synop"
            $py36 $BINDIR/reducevfld.py -vexp $TMPDIR/synopEXPVars_$DATE$HH -model $EXP -ofile $WRKDIR/vfld$EXP$DATE${FINI}${HH} -stn $stnlist
            chead=`head -1 $WRKDIR/vfld$EXP$DATE${FINI}${HH}`
            read num_synop stuff stuff <<< "$chead"
            echo "NSYNOP after reduction: $num_synop"
            rm -rf $TMPDIR
           else
               echo "only splitting files"
          fi
    
          done # hour loop
    
       Start=`$BINDIR/mandtg $Start + $CYINT`
       echo start is $Start
      done #start /lastob
      done #days
      done #months
    done #year
  done # init hours   
done #model  
