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

# load venv
source $ROOT/.venv/bin/activate

# setup paths
path_to_structure=$SCRIPTPATH/data/db_structure
mkdir -p $path_to_structure
path_to_structure=$path_to_structure/structure.sql
path_to_data=$SCRIPTPATH/data/db_seeds
mkdir -p $path_to_data
path_to_data=$path_to_data/static.sql

update_truncate_sql_script=$SCRIPTPATH/update_truncate_sql.py
path_to_truncate=$SCRIPTPATH/data/truncate.sql

echo $path_to_structure
echo $path_to_data


static_data_tables="annotation_type classification_scheme classification_criterium classification_criterium_strength classification_scheme_alias mutually_exclusive_criteria mutually_inclusive_criteria user heredicare_ZID classification_final_class assay_metadata_type assay_type"


# dump structure
mysqldump --quick --column-statistics=0 $DB_NAME -P $DB_PORT -h $DB_HOST -u $DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-data -r $path_to_structure
#gzip --force $path_to_structure

# dump static data
mysqldump --quick --column-statistics=0 $DB_NAME -P $DB_PORT -h $DB_HOST -u $DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-create-info -r $path_to_data $static_data_tables
#gzip $path_to_data


python3 $update_truncate_sql_script -e $static_data_tables -o $path_to_truncate


# dump keycloak config
path_to_keycloak_config=$SCRIPTPATH/data/keycloak_config
mkdir -p $path_to_keycloak_config
$ROOT/tools/keycloak/bin/kc.sh export --dir $path_to_keycloak_config --realm HerediVar --users skip
sed 's/srv018.img.med.uni-tuebingen.de/localhost/g' $path_to_keycloak_config/HerediVar-realm.json > $path_to_keycloak_config/HerediVar-realm-test.json
mv $path_to_keycloak_config/HerediVar-realm-test.json $path_to_keycloak_config/HerediVar-realm.json
sed 's/localhost:5000/localhost:4000/g' $path_to_keycloak_config/HerediVar-realm.json > $path_to_keycloak_config/HerediVar-realm-test.json
rm $path_to_keycloak_config/HerediVar-realm.json

sed -i '$ d' $path_to_keycloak_config/HerediVar-realm-test.json
echo , >> $path_to_keycloak_config/HerediVar-realm-test.json
tail -n +3 /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/keycloak_export/test_config/HerediVar-test-users.json >> $path_to_keycloak_config/HerediVar-realm-test.json

sed -i 's/"verifyEmail" : true,/"verifyEmail" : false,/g' $path_to_keycloak_config/HerediVar-realm-test.json
