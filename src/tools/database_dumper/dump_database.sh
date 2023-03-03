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

mysqldump --quick --column-statistics=0 HerediVar_ahdoebm1 -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-data -r $path_to_structure -p
gzip $path_to_structure


mysqldump --quick --column-statistics=0 HerediVar_ahdoebm1 -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-create-info -r $path_to_data -p
gzip $path_to_data



echo $DATE > most_recent_dump.txt



# information after init_db.py
#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage3/users/ahdoebm1/HerediVar/src/tools/database_dumper/init_db/init.sql HerediVar_ahdoebm1 annotation_type classification_criterium classification_criterium_strength classification_scheme mutually_exclusive_criteria gene gene_alias pfam_id_mapping pfam_legacy task_force_protein_domains transcript 