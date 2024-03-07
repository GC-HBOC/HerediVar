#!/bin/bash
set -e
set -o pipefail
set -o verbose

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
pwd

#-P 3306 -h SRV011.img.med.uni-tuebingen.de 
#mysqldump -P 3306 -h SRV011.img.med.uni-tuebingen.de -u ahdoebm1 -p HerediVar_ahdoebm1 > db_backup.sql
DATE=$(date '+%F');
#path_to_dump=./dumps/dump-$DATE.sql
path_to_structure=./structure/structure-$DATE.sql
path_to_data=./data/data-$DATE.sql

mysqldump --quick --column-statistics=0 HerediVar_ahdoebm1 -P 3306 -h sql.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-data -r $path_to_structure -p
gzip $path_to_structure


mysqldump --quick --column-statistics=0 HerediVar_ahdoebm1 -P 3306 -h sql.img.med.uni-tuebingen.de -u ahdoebm1 --no-tablespaces --no-create-info -r $path_to_data -p
gzip $path_to_data



echo $DATE > most_recent_dump.txt



# information after init_db.py
##mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/init_transcripts_w_tables.sql HerediVar_ahdoebm1  gene gene_alias transcript exon

##mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/task_force_protein_domains.sql HerediVar_ahdoebm1 task_force_protein_domains


#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/init.sql HerediVar_ahdoebm1 annotation_type classification_criterium classification_criterium_strength classification_scheme mutually_exclusive_criteria gene gene_alias pfam_id_mapping pfam_legacy task_force_protein_domains transcript 


#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_new.sql HerediVar_ahdoebm1 classification_criterium_strength classification_criterium
#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_old.sql HerediVar_ahdoebm1_test classification_criterium_strength classification_criterium

#mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/temp.sql HerediVar_ahdoebm1 classification_scheme classification_criterium classification_criterium_strength mutually_exclusive_criteria mutually_inclusive_criteria

#mysql -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p HerediVar_ahdoebm1_test < /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_new.sql


