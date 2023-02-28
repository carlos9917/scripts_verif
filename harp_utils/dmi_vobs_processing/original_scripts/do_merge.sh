#!/usr/bin/env bash
if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate py38
else
  module load python3	
fi
python3 merge_tables_dmi_mars.py
python3 merge_tables_imo_dmi_mars.py
