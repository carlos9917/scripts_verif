#!/bin/bash
module load python3
stream=3 
years=2018 
submit=F
check=F
clean=F
if [ -z $1 ] && [ -z $2 ] && [ -z $3 ] && [ -z $4 ]; then
echo Please provide parameters!
echo example: $stream $years $submit $check $clean
echo          stream  years  submitOrNot checkOrNot cleanOrNot
echo "NOTE: it will only execute the links when looking into nhz data (checkOrNot F)"
exit
else
stream=$1
years=$2
submit=$3
check=$4
clean=$5
python3 ./check_merge_availability.py $stream $years $submit $check $clean
fi
