#!/bin/bash
set -e
set -o pipefail
set -o verbose

#-P 3306 -h SRV011.img.med.uni-tuebingen.de 
#mysqldump -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 -p HerediVar_ahdoebm1 > db_backup.sql
DATE=$(date '+%F');
path_to_dump=./dumps/dump-$DATE.sql

mysqldump --quick HerediVar_ahdoebm1 -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces -r $path_to_dump -p
gzip $path_to_dump


echo dumps/dump-$DATE.sql > most_recent_dump.txt