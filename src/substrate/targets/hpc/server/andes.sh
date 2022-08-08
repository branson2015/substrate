CLUSTER="andes"
INTERACTIVE=

# I put --test-only in the submit commands so I don't accidentally submit yet - just testing for now
submit() {
	if [[ $INTERACTIVE -eq 0 ]]; then
		sbatch --test-only $@
	else
		salloc $@
	fi

}

main() {
	INTERACTIVE=$1
	shift
	submit $@
}

main $@
