#!/bin/bash -l

#get args from client
set -a
eval "$@"
set +a

pipenv run python __main__.py --server remote

