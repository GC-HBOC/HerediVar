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


# set paths
SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
cd $ROOT
pwd


export WEBAPP_ENV=$we
if [ -z "${WEBAPP_ENV}" ]
then
   echo Environment variable WEBAPP_ENV not set.
   exit 1
fi

echo starting Heredivar in "${WEBAPP_ENV}" mode


source .venv/bin/activate
cd src/frontend_celery

if [ "${WEBAPP_ENV}" == "dev" ]
then
   python3 main.py
fi

if [ "${WEBAPP_ENV}" == "localtest" ]
then
   python3 main.py
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
   #export CURL_CA_BUNDLE=""
   set -o allexport
   extension=env_
   source $ROOT/.$extension$WEBAPP_ENV
   set +o allexport
   
   logsdir=$ROOT/logs
   mkdir -p $logsdir/gunicorn-access-logs
   mkdir -p $logsdir/gunicorn-error-logs
   gunicorn -b $HOST:$PORT -w 4 'webapp:create_app()' --access-logfile $logsdir/gunicorn-access-logs/access.log --error-logfile $logsdir/gunicorn-error-logs/error.log # heredivar.uni-koeln.de:8000
   #gunicorn -b SRV018.img.med.uni-tuebingen.de:8001 -w 1 'webapp:create_app()'
fi