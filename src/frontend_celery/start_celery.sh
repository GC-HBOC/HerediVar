#!/bin/bash


set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
   echo "This script starts the heredivar frontend gunicorn or development server"
   echo -e "\t-w Provide 'dev' for development server and 'prod' for production gunicorn server."
   echo -e "\t-h The path to the users home directory."
   exit 1 # Exit script after printing help
}

while getopts "w:" opt
do
   case "$opt" in
      w ) we="$OPTARG" ;;
      h ) localhome="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$we" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# set home for production environment. In systemd $HOME is not available but required for VEP
if [ -n "$localhome"]
then
   echo set home to $localhome
   export HOME=$localhome
fi

echo "preparing celery startup"



SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../../
pwd



source .venv/bin/activate
export WEBAPP_ENV=$we
vep_install_dir=src/tools/ensembl-vep-release-107.0
cpan_dir=$vep_install_dir/cpan
export PERL5LIB=$vep_install_dir/Bio/:$cpan_dir/lib/perl5/:$PERL5LIB


if [ -z "${WEBAPP_ENV}" ]
then
    echo Environment variable WEBAPP_ENV not set.
    exit 1
fi

cd src/frontend_celery/

if [ "${WEBAPP_ENV}" == "dev" ]
then
    celery -A celery_worker.celery worker --loglevel=info --concurrency=5 #--pool=solo
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    celery -A celery_worker.celery multi start single-worker --pidfile=/var/run/celery/celery.pid --logfile=/var/log/celery/celery.log --loglevel=info -Ofair --concurrency=5 --without-heartbeat --without-gossip --without-mingle
fi
