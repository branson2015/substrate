#!/bin/bash

main() {
	ssh -4 -t -L ${INTERMEDIATE_APP_PORT}:${REMOTE_HOST}:${REMOTE_APP_PORT} "${REMOTE_USER}@${REMOTE_MACHINE}" "
		cd ${REMOTE_SUBSTRATE_DIR}
		./go.sh "$@"
	"
}
eval "$@"
main $@

