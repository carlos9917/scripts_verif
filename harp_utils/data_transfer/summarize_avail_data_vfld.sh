#!/usr/bin/env bash
module load conda
conda activate py38

D1=20230101
D2=20230125
for date in $(seq -w $D1 $D2); do
./count_sum_vfld.py -date $date -model enea43h22opr
done
