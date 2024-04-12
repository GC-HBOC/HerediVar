#!/bin/bash
#set -e
#set -o pipefail
#set -o verbose

export WEBAPP_ENV=localtest

SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname $(dirname "$SCRIPT"))))
cd $ROOT
pwd

TESTDIR=$ROOT/src/frontend_celery/playwright
TEST_DATA_DIR=$TESTDIR/data
DB_STRUCTURE=$TEST_DATA_DIR/db_structure/structure.sql
DB_STATIC_SEED=$TEST_DATA_DIR/db_seeds/static.sql

cd $TESTDIR
rm -r screenshots

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

source $ROOT/.venv/bin/activate



# init structure of the database
cat $DB_STRUCTURE | mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW $DB_NAME 

# init static information
mysql_errors=$(mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW  $DB_NAME < $DB_STATIC_SEED 2>&1)
if [ $? = "1" ]; then
    echo $mysql_errors
    exit 1
fi


##mysql --host sql.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $DATABASE_DUMPER_DIR/users/user_privileges_test.sql
##mysql --host sql.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test -e "SHOW TABLES"


# start keycloak - this also seeds keycloak
$TESTDIR/start_keycloak_for_tests.sh


# start heredivar
$TESTDIR/start_heredivar_for_tests.sh


# run tests
cd $TESTDIR
export TESTUSER=$TEST_READONLY
export TESTUSERPW=$TEST_READONLY_PW
pytest --screenshot=only-on-failure --browser firefox tests/read_only/ -k 'test_index' #-k 'test_dev' --browser webkit --browser chromium --numprocesses 2

# stop services
pkill -s 0 -e java
pkill -s 0 -e python3
