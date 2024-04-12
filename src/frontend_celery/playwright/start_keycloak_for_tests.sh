
#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
pwd
ROOT=$(dirname $(dirname $(dirname "$SCRIPTPATH")))

function waitForServer {
  dist=$1
  echo -n "Starting $dist"
  # Give the server some time to start up. Look for a well-known
  # bit of text in the log file. Try at most 50 times before giving up.
  C=500
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

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

keycloak_path=$SCRIPTPATH/keycloak_for_tests

# install keycloak for tests if it is missing
if [ ! -d "${keycloak_path}" ]; then
  wget -q https://github.com/keycloak/keycloak/releases/download/18.0.0/keycloak-18.0.0.zip
  unzip keycloak-18.0.0.zip
  rm keycloak-18.0.0.zip
  mv keycloak-18.0.0 keycloak_for_tests
  mkdir -p $keycloak_path/data/import
  cp $ROOT/resources/backups/keycloak_export/test_config/HerediVar-test-users.json $keycloak_path/data/import/HerediVar-test-users.json
  sleep 5
fi

$keycloak_path/bin/kc.sh import --file $SCRIPTPATH/data/keycloak_config/HerediVar-realm-test.json
sleep 5

$keycloak_path/bin/kc.sh start-dev --hostname $KEYCLOAK_HOST --http-port $KEYCLOAK_PORT --import-realm > keycloak.log 2>&1 & # --log-level debug
waitForServer "Keycloak"