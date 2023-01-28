#!/usr/bin/env bash
module load conda
conda activate py38

D1=20230101
D2=20230125
MODEL=enea43h22mbr000
MODEL=EC9
MODEL=MEPS_prodmbr000
for date in $(seq -w $D1 $D2); do
./count_sum_vfld.py -date $date -model $MODEL
done
