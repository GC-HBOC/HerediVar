#!/bin/bash



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

echo "preparing celery startup"



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


if [ "${WEBAPP_ENV}" == "dev" ]
then
    celery -A celery_worker.celery worker --loglevel=info --concurrency=5 #--pool=solo
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    celery -A celery_worker.celery worker --loglevel=info -Ofair --concurrency=5 --without-heartbeat --without-gossip --without-mingle
fi
