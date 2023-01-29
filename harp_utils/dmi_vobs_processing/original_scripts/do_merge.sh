#!/usr/bin/env bash

eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
conda activate py38
DATAPATH=/data/projects/nckf/danra/vfld/vobs_to_merge
python merge_tables_dmi_mars.py
python merge_tables_imo_dmi_mars.py
