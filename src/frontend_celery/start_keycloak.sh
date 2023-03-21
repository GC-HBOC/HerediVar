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



SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../../
pwd



source .venv/bin/activate
export WEBAPP_ENV=$we

if [ -z "${WEBAPP_ENV}" ]
then
    echo Environment variable WEBAPP_ENV not set.
    exit 1
fi

cd src/frontend_celery/

root="$(dirname `pwd`)"
tools=$root/tools
keycloak_path=$tools/keycloak-18.0.0


if [ "${WEBAPP_ENV}" == "dev" ]
then
    export NO_PROXY=srv018.img.med.uni-tuebingen.de
    $keycloak_path/bin/kc.sh start-dev --hostname srv018.img.med.uni-tuebingen.de --http-port 5050 #--features=admin-fine-grained-authz # --log-level debug
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    $keycloak_path/bin/kc.sh start --proxy=edge --hostname-strict=false --log-level INFO --hostname=heredivar.uni-koeln.de
fi





