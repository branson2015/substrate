from config.sh:

tunnel 1: intermediate server arbitration ports
LOCAL_ARB_PORT => INTERMEDIATE_ARB_PORT

tunnel 2: remote server arbitration ports
LOCAL_REM_PORT => INTERMEDIATE_REM_PORT => REMOTE_ARB_PORT

tunnel 3: application ports
LOCAL_APP_PORT => INTERMEDIATE_APP_PORT => REMOTE_APP_PORT

LOCAL_APP_PORT, LOCAL_ARB_PORT, LOCAL_REM_PORT, INTERMEDIATE_APP_PORT, and INTERMEDIATE_REM_PORT are all just passthrough ports for ssh.
INTERMEDIATE_ARB_PORT hosts the arbitration server that sits on the login node
REMOTE_ARB_PORT hosts the arbitration server that sits on the cluster
REMOTE_APP_PORT hosts the main application.



