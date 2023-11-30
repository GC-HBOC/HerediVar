#!/bin/bash


set -e
set -o pipefail


helpFunction()
{
    echo ""
    echo "Usage: $0 -w env"
    echo "This script starts the heredivar frontend gunicorn or development server"
    echo -e "\t-w Provide 'dev' for development server and 'prod' for production gunicorn server."
    exit 1 # Exit script after printing help
}

while getopts "w:" opt
do
   case "$opt" in
        w ) we="$OPTARG" ;;
        ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$we" ]
then
    echo "Some or all of the parameters are empty";
    helpFunction
fi

echo "preparing keycloak startup"


# set paths
SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
TOOLS=$ROOT/tools
KEYCLOAK_PATH=$TOOLS/keycloak
cd $ROOT
pwd


source .venv/bin/activate


export WEBAPP_ENV=$we
if [ -z "${WEBAPP_ENV}" ]
then
    echo Environment variable WEBAPP_ENV not set.
    exit 1
fi


set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport



if [ "${WEBAPP_ENV}" == "dev" ]
then
    export NO_PROXY=$KEYCLOAK_HOST
    $KEYCLOAK_PATH/bin/kc.sh start-dev --hostname $KEYCLOAK_HOST --http-port $KEYCLOAK_PORT #--features=admin-fine-grained-authz # --log-level debug
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    $KEYCLOAK_PATH/bin/kc.sh start --proxy=edge --hostname-strict=false --hostname=$KEYCLOAK_HOST #heredivar.uni-koeln.de --log-level INFO
fi


