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





SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../../
pwd

export WEBAPP_ENV=$we

source .venv/bin/activate
cd $SCRIPTPATH

echo starting Heredivar in "${WEBAPP_ENV}" mode

if [ -z "${WEBAPP_ENV}" ]
then
   echo Environment variable WEBAPP_ENV not set.
   exit 1
fi

if [ "${WEBAPP_ENV}" == "dev" ]
then
   python3 main.py
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
   export CURL_CA_BUNDLE=""
   gunicorn -b heredivar.uni-koeln.de:8000 -w 4 'webapp:create_app()'
   #gunicorn -b SRV018.img.med.uni-tuebingen.de:8001 -w 1 'webapp:create_app()'
fi