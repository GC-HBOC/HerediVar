#!/bin/bash
set -e
set -o pipefail
#set -o verbose


helpFunction()
{
   echo ""
   echo "Usage: $0 -w env"
   echo "This script dumps the static data from HerediVar for tests. This data is used for seeding the database during tests."
   echo -e "\t-w Provide 'dev' for development server and 'prod' for production config."
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
   echo Environment variable WEBAPP_ENV not set. Use -w option
   exit 1
fi

echo using "${WEBAPP_ENV}" config


SCRIPTPATH=$(dirname "$SCRIPT")
echo script: $SCRIPT
echo scriptpath: $SCRIPTPATH
ROOT=$(dirname $(dirname $(dirname $(dirname "$SCRIPT"))))
echo Root dir: $ROOT

#cd $SCRIPTPATH


# load environment variables
set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport


# setup paths
path_to_structure=$SCRIPTPATH/data/db_structure
mkdir -p $path_to_structure
path_to_structure=$path_to_structure/structure.sql
path_to_data=$SCRIPTPATH/data/db_seeds
mkdir -p $path_to_data
path_to_data=$path_to_data/static.sql

echo $path_to_structure
echo $path_to_data

# dump structure
mysqldump --quick --column-statistics=0 $DB_NAME -P $DB_PORT -h $DB_HOST -u $DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-data -r $path_to_structure
#gzip --force $path_to_structure

# dump static data
mysqldump --quick --column-statistics=0 $DB_NAME -P $DB_PORT -h $DB_HOST -u $DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-create-info -r $path_to_data annotation_type classification_scheme classification_criterium classification_criterium_strength classification_scheme_alias mutually_exclusive_criteria mutually_inclusive_criteria user
#gzip $path_to_data
