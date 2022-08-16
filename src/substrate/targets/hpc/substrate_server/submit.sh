#!/bin/bash

CLUSTER=
INTERACTIVE=0
_ARGS=()

parseArgs() {
	while [[ $# -gt 0 ]]; do 
		case $1 in
			-c|--cluster)
				CLUSTER=$2
				shift
				;;

			--interactive)
				INTERACTIVE=1
				;;
			
			*) 
				_ARGS="$_ARGS $1"
				;;
		esac
		shift
	done
}

main() {
	parseArgs "$@"
	set -- "${_ARGS[@]}"
	CLUSTERSCRIPT="./$CLUSTER.sh"
	$SHELL $CLUSTERSCRIPT $INTERACTIVE $@
}

main $@
