#!/bin/bash

# stop any running keycloak instances if there are any
export WEBAPP_ENV=localtest

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../../../../
pwd

DATABASE_DUMPER_DIR=resources/backups/database_dumper
TEST_DATA_DIR=src/frontend_celery/tests/data
TEST_SCRIPT_DIR=src/frontend_celery/tests/script
MOST_RECENT_DUMP_DATE=$(cat $DATABASE_DUMPER_DIR/most_recent_dump.txt)
source .venv/bin/activate


zcat $DATABASE_DUMPER_DIR/structure/structure-$MOST_RECENT_DUMP_DATE.sql.gz | mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test
mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $TEST_DATA_DIR/heredivar_test_data.sql
#mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $DATABASE_DUMPER_DIR/users/user_privileges_test.sql
#mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test -e "SHOW TABLES"


# start keycloak
$TEST_SCRIPT_DIR/start_keycloak_for_tests.sh

# run tests
cd src/frontend_celery
python -m pytest #-k 'test_dev'

# stop keycloak
pkill -s 0 -e java
