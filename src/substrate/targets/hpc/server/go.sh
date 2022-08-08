#!/bin/bash -l

check_args_set(){
    requiredVariables=('INTERMEDIATE_HOST' 'INTERMEDIATE_ARB_PORT' 'INTERMEDIATE_APP_PORT' 'REMOTE_MACHINE' 'REMOTE_SUBSTRATE_DIR' 'REMOTE_HOST' 'REMOTE_APP_PORT')
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
	#get args from client
	set -a
	#delete me!
	source config.sh
	#delete me!
	eval "$@"
	INTERMEDIATE_MACHINE=$(hostname)
	set +a

	echo "Connected to ${INTERMEDIATE_MACHINE}"
	
	#set up HPC-specific environment (python, conda, etc)
	. ./environment_setup.sh

	#start server
	#python "server.py -p ${INTERMEDIATE_ARB_PORT} -h ${INTERMEDIATE_HOST} -d true" &

	#submit the job
	./submit.sh --cluster andes --interactive -A csc143 -N 1 -t 00:10:00 ./reverse_ssh.sh "$@"

	#await connection
	#./connect_ssh.sh "$@"

}

main $@
