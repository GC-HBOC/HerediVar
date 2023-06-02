
#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../
pwd


function waitForServer {
  dist=$1
  echo -n "Starting $dist"
  # Give the server some time to start up. Look for a well-known
  # bit of text in the log file. Try at most 50 times before giving up.
  C=50
  while :
  do
    grep "$dist .* (powered by Quarkus .*) started" keycloak.log
    if [ $? -eq 0 ]; then
      echo " server started."
      break
    elif [ $C -gt 0 ]; then
      echo -n "."
      C=$((C-1))
      sleep 1
    else
      echo " timeout!"
      cat keycloak.log
      exit 1
    fi
  done
}

keycloak-18.0.0/bin/kc.sh start-dev --hostname 127.0.0.1 --http-port 5050 > keycloak.log 2>&1 & # --log-level debug
waitForServer "Keycloak"