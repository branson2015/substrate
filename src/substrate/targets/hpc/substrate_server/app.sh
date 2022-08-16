#!/bin/bash

#get args from client
set -a
eval "$@"
set +a

curl "${INTERMEDIATE_MACHINE}:${INTERMEDIATE_APP_PORT}/cluster_connected"

python ./remote_server/server.py & 

