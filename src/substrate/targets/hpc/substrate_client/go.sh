#https://unix.stackexchange.com/questions/115897/whats-ssh-port-forwarding-and-whats-the-difference-between-ssh-local-and-remot

#LOCAL_ARB_PORT=5001
#LOCAL_APP_PORT=5000

#INTERMEDIATE_MACHINE=
#INTERMEDIATE_USER=
#INTERMEDIATE_SUBSTRATE_DIR=
#INTERMEDIATE_HOST="127.0.0.1"
#INTERMEDIATE_ARB_PORT=8029
#INTERMEDIATE_APP_PORT=8028

#REMOTE_SUBSTRATE_DIR=
#REMOTE_USER=
#REMOTE_HOST="127.0.0.1"
#REMOTE_APP_PORT=8030


source_config="config.sh"
_ARGS=()

parseArgs() {
	while [[ $# -gt 0 ]]; do 
		case $1 in
			-c|--config)
				source_config=$2
				shift
				;;
			*) 
				_ARGS="$_ARGS $1"
				;;
		esac
		shift
	done
}

check_args_set(){
    requiredVariables=('LOCAL_ARB_PORT' 'LOCAL_APP_PORT' 'INTERMEDIATE_MACHINE' 'INTERMEDIATE_USER' 'INTERMEDIATE_SUBSTRATE_DIR' 'INTERMEDIATE_HOST' 'INTERMEDIATE_ARB_PORT' 'INTERMEDIATE_APP_PORT' 'REMOTE_SUBSTRATE_DIR' 'REMOTE_HOST' 'REMOTE_APP_PORT')
    unset_vars=false
    for varName in "${requiredVariables[@]}"; do
        if [[ -z ${!varName} ]]
        then
            echo "$varName not set!"
            unset_vars=true
        fi
    done

    if $unset_vars; then
        echo "quitting"
        exit
    fi
}


main() {
	parseArgs "$@"
	set -- "${_ARGS[@]}"

    if [[ -f $source_config ]]
    then
        source $source_config
    fi
    
    check_args_set
    
    ARGS="$(cat $source_config)"
    
    ssh -4 -t \
        -L ${LOCAL_ARB_PORT}:${INTERMEDIATE_HOST}:${INTERMEDIATE_ARB_PORT} \
        -L ${LOCAL_APP_PORT}:${INTERMEDIATE_HOST}:${INTERMEDIATE_APP_PORT} "${INTERMEDIATE_USER}@${INTERMEDIATE_MACHINE}" \
        -L ${LOCAL_REM_PORT}:${INTERMEDIATE_HOST}:${INTERMEDIATE_REM_PORT} "${INTERMEDIATE_USER}@${INTERMEDIATE_MACHINE}" "
            cd ${INTERMEDIATE_SUBSTRATE_DIR}
            ./go.sh '${ARGS}'
    "
}


main $@
