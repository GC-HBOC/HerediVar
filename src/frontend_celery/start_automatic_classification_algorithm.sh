#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
   echo "This script starts the fastAPI service of the automatic classification algorithm"
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


echo "preparing automatic classification startup"



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

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport


autoclass_path=$ROOT/tools/variant_classification
cd $autoclass_path

source .venv/bin/activate

if [ "${WEBAPP_ENV}" == "dev" ]
then
    python3 variant_classification/webservice.py --port $AUTOCLASS_PORT --host $AUTOCLASS_HOST
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    python3 variant_classification/webservice.py --port $AUTOCLASS_PORT --host $AUTOCLASS_HOST
fi
