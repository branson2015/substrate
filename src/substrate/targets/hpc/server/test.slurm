#!/bin/bash
#SBATCH -A csc143
#SBATCH -J test
#SBATCH -N 1
#SBATCH -t 0:01:00
#SBATCH -v

cd $SLURM_SUBMIT_DIR
date
