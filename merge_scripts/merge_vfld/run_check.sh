#!/bin/bash
module load python3
years=2018 
submit=F
check=F
clean=F
if [ -z $1 ] && [ -z $2 ] && [ -z $3 ] && [ -z $4 ]; then
echo Please provide parameters!
echo "example: $years $submit $check $clean"
echo "          year(s)  submitOrNot checkOrNot cleanOrNot"
echo "NOTE: it will only execute the links when looking into nhz data (checkOrNot F)"
exit
else
years=$1
submit=$2
check=$3
clean=$4
python3 ./check_merge_availability.py $years $submit $check $clean
fi
