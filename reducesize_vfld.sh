#!/bin/bash
# Reduces the size of the vfld files
#
# Essentially a trimmed-down version of splitvfld_all.sh
#
# CURRENTLY only working for Surface data!
# To be used with monitor for verification only.
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
         days=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30)
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
hour_end=51
rvfld=True #CHANGE. if True, will reduce the file size. If False, it will only split the files
            # This last option is useful to examine the file contents.
years=(2019) #(2017 2018)
month=(05 06 07 08) # 02 03 04 05 06 07 08 09 10 11 12)#
models=(nea40h11)
#models=(EC9)
init_hours=(00 06 12 18)
#stnlist=/home/cap/verify/scripts_verif/stngreenland_bjarne.dat
#stnlist=/home/cap/verify/scripts_verif/stntasii.dat
#stnlist=/home/cap/verify/scripts_verif/stncoord.dat
stnlist=/home/cap/verify/scripts_verif/stncoord_dk_monitor.dat
region=monitor_selection_dk


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
            vfldfile=$VFLDDIR/vfld$EXP$DATE${FINI}${HH}

            if [[ $EXP == 'tasii' ]]; then
                vold=$vfldfile
                dtgtas=`$HOME/bin/mandtg $year$m$d$FINI + -3 | cut -c1-10`
                HH3=`expr $HH + 3`
                HH3=`perl -e "printf('%2.2i', $HH3)"`
                vfldfile=$VFLDDIR/vfld$EXP$dtgtas${HH3}
                echo "Processing tasii. This requires a shift in init_time/hour"
                echo "$vold corresponds to $vfldfile"
            fi    
    
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
