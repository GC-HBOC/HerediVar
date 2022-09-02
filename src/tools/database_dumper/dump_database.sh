#!/bin/bash
set -e
set -o pipefail
set -o verbose

#-P 3306 -h SRV011.img.med.uni-tuebingen.de 
#mysqldump -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 -p HerediVar_ahdoebm1 > db_backup.sql
DATE=$(date '+%F');
#path_to_dump=./dumps/dump-$DATE.sql
path_to_structure=./structure/structure-$DATE.sql
path_to_data=./data/data-$DATE.sql

mysqldump --quick HerediVar_ahdoebm1 -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-data -r $path_to_structure -p
gzip $path_to_structure


mysqldump --quick HerediVar_ahdoebm1 -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-create-info -r $path_to_data -p
gzip $path_to_data



echo $DATE > most_recent_dump.txt