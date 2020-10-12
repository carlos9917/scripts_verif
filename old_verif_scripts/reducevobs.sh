#!/bin/bash
#Reduce the size of the vobs files. Uses the same script to reduce the vfld files
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
         days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30)
      ;;
      esac
}

#using my conda installation:
export PATH=/data/cap/miniconda2/bin:$PATH
source activate py37
py36=/data/cap/miniconda2/envs/py37/bin/python
EXP=nea40h11 #nea40h11 #CHANGE
#for hpc:
VOBSDIR=/data/cap/VOBS
VFLDDIR=/data/xiaohua/vfld/$EXP
BINDIR=/home/cap/verify/scripts_verif
#for my local expts:
#VFLDDIR=/data/cap/code_development_hpc/scripts_verif
#VOBSDIR=/data/cap/code_development_hpc/scripts_verif
#BINDIR=/data/cap/code_development_hpc/scripts_verif
#WRKDIR=/data/cap/vfld_reduced/$EXP
#WRKDIR=/data/cap/verif_formatted_data/$EXP
CYINT=24

hour_ini=00 #use 2 digits for defining the Start and Lastob properly
hour_end=23
reduce=False #CHANGE. if True, will reduce the file size. If not only split the files
years=(2019) #(2017 2018)
month=(07) # 02 03 04 05 06 07 08 09 10 11 12)
vars=(PS RH TD) # Not active yet. ONLY needed by the conversion script, not to split the files
init_times=(00 06 12 18)
region=Greenland
WRKDIR=/data/cap/vobs_reduced/$region/split_only
stnlist=/home/cap/verify/scripts_verif/stngreenland.dat

mkdir -p $WRKDIR || exit
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
        TMPDIR=$WRKDIR/data_$DATE$HH
        mkdir -p $TMPDIR
        vobsfile=$VOBSDIR/vobs$DATE$HH
        #echo "Processing time $DATE$HH"
        #echo "vobs and vfld files "
        #echo $vobsfile
        #echo "vfld file: $vfldfile"
        #FOR VOBS file:
        header=`head -1 $vobsfile`
        read nsynop ntemp verflag <<< "$header"
        nvars_synop=`awk 'NR==2' $vobsfile`


        #create file with synop data from VOBS
        echo "Processing $nsynop synop stations for VOBS"
        let lstart="3 + $nvars_synop"
        let lend="$lstart + $nsynop - 1"
        let vend="$lstart - 1"
        let tmpstart="$lend + 1"
        #this one prints the data and 2nd awk gets rid of undesirable extra spaces!
        awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1' > $TMPDIR/synopOBSData_$DATE$HH
        awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vobsfile | awk '{$2=$2};1'  > $TMPDIR/synopOBSVars_$DATE$HH

        #create temporary file(s) with tmp data (if any)
        #TURNING THIS OFF FOR THE MOMENT, since verif does not use TEMP data
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
        #echo "Processing $nsynop synop stations for VFLD"
        #let lstart="3 + $nvars_synop"
        #let lend="$lstart + $nsynop - 1"
        #let vend="$lstart - 1"
        #let tmpstart="$lend + 1"
        #awk -v a="$lstart" -v b="$lend" 'NR >= a && NR <= b' $vfldfile |  awk '{$2=$2};1' > $TMPDIR/synopEXPData_$DATE$HH
        #awk -v a=3 -v b="$vend" 'NR >= a && NR <= b' $vfldfile | awk '{$2=$2};1'  > $TMPDIR/synopEXPVars_$DATE$HH

        #create temporary file(s) with tmp data (if any)
        #TURNING THIS OFF FOR THE MOMENT, since verif does not use TEMP data
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

      if [ $reduce == True ]; then
       echo "Reducing vobs file $vobsfile"
        chead=`head -1 $vobsfile`
        read num_synop stuff stuff <<< "$chead"
        echo "NSYNOP before reduction: $num_synop"
        $py36 $BINDIR/reducevfld.py -vexp $TMPDIR/synopOBSVars_$DATE$HH -model vobs -ofile $WRKDIR/vobs$DATE${HH} -stn $stnlist
        chead=`head -1 $WRKDIR/vobs$DATE${HH}`
        read num_synop stuff stuff <<< "$chead"
        echo "NSYNOP after reduction: $num_synop"
        rm -rf $TMPDIR # $WRKDIR/data_${DATE}??
       else
           echo "only splitting VOBS files"
      fi

      done # hour loop

   Start=`$BINDIR/mandtg $Start + $CYINT`
   echo start is $Start
  done #start /lastob
  done #days
  done #months
  done #year
