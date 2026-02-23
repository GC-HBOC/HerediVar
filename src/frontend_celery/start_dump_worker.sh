#!/bin/bash
set -euo pipefail
#set -o verbose

# set defaults
dump_keycloak="False"
dump_database="False"
create_version="False"
we=""

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -k -d -v"
   echo "This script creates a full backup for HerediVar"
   echo -e "\t-w Provide 'dev' for development server and 'prod' for production gunicorn server."
   echo -e "\t-k Optional: provide to dump the keycloak database."
   echo -e "\t-d Optional: provide to dump the heredivar database."
   echo -e "\t-v Optional: provide to create a new heredivar version (vcf file)."
   exit 1 # Exit script after printing help
}

while getopts "w:kdv" opt
do
   case "$opt" in
      w ) we="$OPTARG" ;;
      k ) dump_keycloak="True" ;;
      d ) dump_database="True" ;;
      v ) create_version="True" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case mandatory parameters are empty
if [ -z "$we" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

export WEBAPP_ENV=$we

echo "Dumping data for..."
if [ "$dump_keycloak" = "True" ]; then
   echo "... keycloak"
fi
if [ "$dump_database" = "True" ]; then
   echo "... database"
fi
if [ "$create_version" = "True" ]; then
   echo "... new version (vcf)"
fi

SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
cd $ROOT
pwd

TOOSDIR=$ROOT/tools

source .venv/bin/activate


# Start log
echo "----------------------------------------"
echo "Backup started: $(date)"
echo "----------------------------------------"
echo ""

# create new version
if [ "$create_version" = "True" ]; then
   echo "----------------------------------------"
   echo "Started creating version: $(date)"
   
   DOWNLOADSDIR=$ROOT/downloads
   full_dump_path=$DOWNLOADSDIR/full_dump
   mkdir -p $full_dump_path
   DATE=$(date '+%F');

   python3 $ROOT/src/frontend_celery/webapp/utils/create_db_version.py -d $DATE
   bgzip $ROOT/downloads/all_variants/$DATE.vcf

   echo "Finished creating version: $(date)"
   echo "----------------------------------------"
   echo ""
fi

# create data dump backup
if [ "$dump_database" = "True" ]; then
   echo "----------------------------------------"
   echo "Starting database backup: $(date)"
   DB_DUMP_DIR=$ROOT/resources/backups/database_dumper
   $DB_DUMP_DIR/dump_database.sh -w $WEBAPP_ENV
   echo "Finished database backup: $(date)"
   echo "----------------------------------------"
   echo ""
   echo "----------------------------------------"
   echo "Starting database backup cleaning: $(date)"
   $TOOSDIR/script/cleanup.sh -w $WEBAPP_ENV -p $DB_DUMP_DIR/$WEBAPP_ENV -f production-dump- -e .sql -d
   #$DB_DUMP_DIR/cleanup.sh -w $WEBAPP_ENV -d # cleanup old files
   echo "Finished database backup cleaning: $(date)"
   echo "----------------------------------------"
   echo ""
fi


# create keycloak backup
if [ "$dump_keycloak" = "True" ]; then
   echo "----------------------------------------"
   echo "Starting Keycloak backup: $(date)"
   KEYCLOAK_DUMP_DIR=$ROOT/resources/backups/keycloak_export
   $KEYCLOAK_DUMP_DIR/export_keycloak.sh -w $WEBAPP_ENV
   echo "Finished Keycloak backup: $(date)"
   echo "----------------------------------------"
   echo ""
   echo "----------------------------------------"
   echo "Starting Keycloak backup cleaning: $(date)"
   $TOOSDIR/script/cleanup.sh -w $WEBAPP_ENV -p $KEYCLOAK_DUMP_DIR/$WEBAPP_ENV -f production-dump- -e .sql -d
   #$KEYCLOAK_DUMP_DIR/cleanup.sh -w $WEBAPP_ENV -d
   echo "Finished Keycloak backup cleaning: $(date)"
   echo "----------------------------------------"
   echo ""
fi

echo "----------------------------------------"
echo "Backup finished: $(date)"
echo "----------------------------------------"