#!/usr/bin/env bash
export YEAR=2023

#set it to 1 for doing it, 0 for not
export DO_FC=0
export DO_OB=1
export SCRATCH=/ec/res4/scratch/nhd

#these are the paths were the data is stored with the processed sqlite files from julia
#glatmodel data:
export fcst_path=$SCRATCH/ROAD_MODEL/fcst_raw

#this one I was using for the R01 model. 
#export fcst_path=$SCRATCH/ROAD_MODEL/glatmodel_no_obs

#the observation data
export obs_path=$SCRATCH/ROAD_MODEL/obs_raw
#export obs_path=$SCRATCH/ROAD_MODEL/fcst_raw

CONFIG_FILE=config_atos.yml
export MODEL=glatmodel
