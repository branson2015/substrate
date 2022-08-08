#!/bin/bash

main() {
	#get args from client
	set -a
	#delete me!
	source config.sh
	#delete me!
	eval "$@"
	set +a


	ssh -4 -t -R ${INTERMEDIATE_APP_PORT}:${REMOTE_HOST}:${REMOTE_APP_PORT} "${INTERMEDIATE_USER}@${INTERMEDIATE_MACHINE}" "
		cd ${REMOTE_SUBSTRATE_DIR}
		./app.sh 
	"
}
eval "$@"
main $@

