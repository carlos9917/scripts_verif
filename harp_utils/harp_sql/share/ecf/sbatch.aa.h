#!/bin/bash
#SBATCH --job-name=%TASK%
#SBATCH --qos=%QUEUE%
#SBATCH --output=%ECF_JOBOUT%
#SBATCH --error=%ECF_JOBOUT%
#SBATCH --mem-per-cpu=16000
#SBATCH --time=02:00:00
source /etc/profile
