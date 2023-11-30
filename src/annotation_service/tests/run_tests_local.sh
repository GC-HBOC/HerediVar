
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../../..
pwd

MOST_RECENT_DUMP_DATE=$(cat src/tools/database_dumper/most_recent_dump.txt)
BASE_PATH=/mnt/users/ahdoebm1/HerediVar


zcat $BASE_PATH/src/tools/database_dumper/structure/structure-$MOST_RECENT_DUMP_DATE.sql.gz | mysql --host sql.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test
mysql --host sql.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $BASE_PATH/src/frontend_celery/tests/data/heredivar_test_data.sql
mysql --host sql.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test -e "SHOW TABLES"

export WEBAPP_ENV=localtest

cd $BASE_PATH/src/annotation_service
python -m pytest #-k 'test_dev'