#!/bin/bash
set -e
set -o pipefail
#set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
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

export WEBAPP_ENV=$we

echo "Creating Keycloak dump for $WEBAPP_ENV environment"


SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH


ROOT=$(dirname $(dirname $(dirname "$SCRIPTPATH")))
TOOLS=$ROOT/tools
KEYCLOAK=$TOOLS/keycloak/bin

DATE=$(date '+%F');




if [ "${WEBAPP_ENV}" == "dev" ]
then
    backups_folder=$SCRIPTPATH/dev/$DATE
    mkdir -p $backups_folder
    $KEYCLOAK/kc.sh export --dir $backups_folder --realm HerediVar --users same_file
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    dump_path=$SCRIPTPATH/prod
    mkdir -p $dump_path
    dump_name=production-dump-$DATE.sql

    mysqldump --quick -h$KEYCLOAK_DB_HOST -P$KEYCLOAK_DB_PORT -u$KEYCLOAK_DB_USERNAME -p$KEYCLOAK_DB_PW --no-tablespaces -r$dump_path/$dump_name $KEYCLOAK_DB_SCHEME
    gzip -f $dump_path/$dump_name
fi


#sed 's/"directAccessGrantsEnabled" : false,/"directAccessGrantsEnabled" : true,/g' Heredivar-realm.json > test_config/Heredivar-realm-test.json