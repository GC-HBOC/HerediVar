#!/bin/bash
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

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

# close all existing connections
mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW $DB_NAME -e "select GROUP_CONCAT(stat SEPARATOR ' ') from (select concat('KILL ',id,';') as stat from information_schema.processlist) as stats;" > /tmp/killall.sql
tail -n +2 /tmp/killall.sql > /tmp/killall2.sql
mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW $DB_NAME < /tmp/killall2.sql

# init structure of the database
cat $DB_STRUCTURE | mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW $DB_NAME 

# init static information
mysql_errors=$(mysql -h $DB_HOST -P $DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW  $DB_NAME < $DB_STATIC_SEED 2>&1)
if [ $? = "1" ]; then
    echo $mysql_errors
    exit 1
fi
