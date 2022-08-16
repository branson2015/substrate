#!/bin/bash -l

#load python module
module load python

#make sure conda is initialized and activate substrate_server
SHELL_NAME=$(cut -d/ -f3 <<< $SHELL)
conda init $SHELL_NAME &> /dev/null
eval "$(conda shell.bash hook)"
conda activate substrate_server

#setup environment variables
export FLASK_APP=server.py
export FLASK_ENV=development
