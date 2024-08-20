#!/bin/bash
set -e
set -o pipefail
#set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
   echo "This script starts a full import from HerediCaRe"
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

export WEBAPP_ENV=$we

echo "Importing HerediCaRe and updating upload stati...."

SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
cd $ROOT
pwd

source .venv/bin/activate

python3 $ROOT/src/frontend_celery/webapp/utils/import_heredicare.py
