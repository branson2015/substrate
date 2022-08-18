#!/bin/bash

#get args from client
set -a
eval "$@"
set +a

echo "$@"

pipenv run python __main__.py --server remote

