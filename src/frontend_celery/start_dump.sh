#!/bin/bash
set -e
set -o pipefail
#set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
   echo "This script creates a full backup for HerediVar"
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

echo "Dumping all data, creating backups and creating new HerediVar version...."




SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
cd $ROOT
pwd

source .venv/bin/activate


# create new version
DOWNLOADSDIR=$ROOT/downloads
full_dump_path=$DOWNLOADSDIR/full_dump
mkdir -p $full_dump_path


DATE=$(date '+%F');

python3 $ROOT/src/frontend_celery/webapp/utils/create_db_version.py -d $DATE
bgzip $ROOT/downloads/all_variants/$DATE.vcf

# create data dump backup
DB_DUMP_DIR=$ROOT/resources/backups/database_dumper
$DB_DUMP_DIR/dump_database.sh -w $WEBAPP_ENV

# create keycloak backup
KEYCLOAK_DUMP_DIR=$ROOT/resources/backups/keycloak_export
$KEYCLOAK_DUMP_DIR/export_keycloak.sh -w $WEBAPP_ENV