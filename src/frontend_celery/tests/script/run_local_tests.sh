#!/bin/bash -e


export WEBAPP_ENV=localtest
export NO_PROXY=SRV018.img.med.uni-tuebingen.de
export CLIENT_SECRET=NRLzlQfotGy9W8hkuYFm3T48Bjnti15k
export CLIENT_ID=flask-webapp
export FLASK_SECRET_KEY=736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b



MOST_RECENT_DUMP_DATE=$(cat src/tools/database_dumper/most_recent_dump.txt)
BASE_PATH=/mnt/users/ahdoebm1/HerediVar


#gunzip $BASE_PATH/src/tools/database_dumper/structure/structure-$MOST_RECENT_DUMP_DATE.sql.gz
zcat $BASE_PATH/src/tools/database_dumper/structure/structure-$MOST_RECENT_DUMP_DATE.sql.gz | mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test
#mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $BASE_PATH/src/tools/database_dumper/structure/structure-$MOST_RECENT_DUMP_DATE.sql
mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test < $BASE_PATH/src/frontend_celery/tests/data/heredivar_test_data.sql
mysql --host SRV011.img.med.uni-tuebingen.de -uahdoebm1 -p20220303 HerediVar_ahdoebm1_test -e "SHOW TABLES"
#gzip src/tools/database_dumper/structure/structure-$MOST_RECENT_DUMP_DATE.sql


cd $BASE_PATH/src/frontend_celery
python -m pytest -k 'test_dev'