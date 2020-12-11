#!/bin/bash
# Creates soft links for the tasii files,
# since the finit and hour need to be shifted accordingly
# to coincide what time of igb40h11 and the rest of the models
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

BINDIR=/home/cap/verify/scripts_verif
VOBSDIR=/data/cap/VOBS
CYINT=51 # CHANGE, for example for EC9
hour_ini=00 #use 2 digits for defining the Start and Lastob properly
hour_end=51
years=(2018) #(2017 2018)
month=(09 10 11 12) # 02 03 04 05 06 07 08 09 10 11 12)#
models=(tasii) # igb40h11)
#models=(EC9)
init_hours=(00 06 12 18)
#stnlist=/home/cap/verify/scripts_verif/stngreenland_bjarne.dat
stnlist=/home/cap/verify/scripts_verif/stntasii.dat
region=Greenland

EXP='tasii'

#WRKDIR=/data/cap/vfld_reduced/$EXP
WRKDIR=/data/cap/vfld_reduced/links_timeshifted_tasii/$EXP
VFLDDIR=/data/xiaohua/vfld/$EXP
mkdir -p $WRKDIR || exit
echo "Making soft links pointing to the correct time shifted files for  $EXP"
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
      echo "Doing date $DATE" 
        for HH in `seq -w $hour_ini $hour_end`; do
          echo "Doing hour $HH"
          vfldfile=$WRKDIR/vfld$EXP$DATE${FINI}${HH}
          dtgtas=`$HOME/bin/mandtg $year$m$d$FINI + -3 | cut -c1-10`
          HH3=`expr $HH + 3`
          HH3=`perl -e "printf('%2.2i', $HH3)"`
          vfldfile_shift=$VFLDDIR/vfld$EXP$dtgtas${HH3}
          if [[ -f $vfldfile_shift ]]; then
          ln -sf $vfldfile_shift $vfldfile
          else
          echo "file $vfldfile_shift not available"
          fi
  
        done # hour loop
  
     Start=`$BINDIR/mandtg $Start + $CYINT`
     echo start is $Start
    done #start /lastob
    done #days
    done #months
  done #year
done # init hours   
