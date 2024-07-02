
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
    grep ".* Ready to accept connections tcp" redis.log
    if [ $? -eq 0 ]; then
      echo " server started."
      break
    elif [ $C -gt 0 ]; then
      echo -n "."
      C=$((C-1))
      sleep 1
    else
      echo " timeout!"
      cat redis.log
      exit 1
    fi
  done
}

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

TOOLS=$ROOT/tools

redis_path=$SCRIPTPATH/redis_for_tests

# install keycloak for tests if it is missing
if [ ! -d "${redis_path}" ]; then
  $TOOLS/script/install_redis.sh -p $SCRIPTPATH -n redis_for_tests
  sleep 5
fi

redis_for_tests/src/redis-server --port $REDIS_PORT > redis.log 2>&1 &
waitForServer "Redis"