#!/usr/bin/env bash

eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
conda activate py38
DATAPATH=/data/projects/nckf/danra/vfld/vobs_to_merge
echo "Doing merge of data from DMI and MARS sqlite files"
python merge_tables_dmi_mars.py
echo "Doing merge of data from IMO and DMI_MARS sqlite files"
python merge_tables_imo_dmi_mars.py
