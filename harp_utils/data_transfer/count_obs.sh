#!/usr/bin/env bash
ml conda
conda activate glat

check_years_carra2()
{
for Y in 1986 1991 1996 2001 2006 2011 2016 2021; do
M=01
#for M in $(seq 09 12); do
python obstable_availability.py $Y $M -v T2m
#done
done
}

#check_years_carra2
#exit

Y=2021
for M in $(seq -w 1 12); do
python obstable_availability.py $Y $M -v T2m
done
