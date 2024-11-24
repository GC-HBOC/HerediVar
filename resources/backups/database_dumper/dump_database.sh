#!/bin/bash
set -e
set -o pipefail
#set -o verbose

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env -h path"
   echo "This script starts the heredivar frontend gunicorn or development server"
   echo -e "\t-w Provide 'dev' for development server and 'prod' for production gunicorn server."
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

export WEBAPP_ENV=$we

echo "Creating database dump for $WEBAPP_ENV environment"


SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
pwd

ROOT=$(dirname $(dirname $(dirname "$SCRIPTPATH")))
set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

DATE=$(date '+%F');

if [ "${WEBAPP_ENV}" == "dev" ]
then
    # dump structure
    structure_path=$SCRIPTPATH/dev/structure
    mkdir -p $structure_path
    structure_name=structure-$DATE.sql
    mysqldump --quick --column-statistics=0 -P$DB_PORT -h$DB_HOST -u$DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-data -r$structure_path/$structure_name $DB_NAME
    gzip -f $structure_path/$structure_name

    # dump data
    data_path=$SCRIPTPATH/dev/data
    mkdir -p $data_path
    data_name=data-$DATE.sql
    mysqldump --quick --column-statistics=0 -P$DB_PORT -h$DB_HOST -u$DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-create-info -r$data_path/$data_name $DB_NAME
    gzip -f $data_path/$data_name

    # dump static data
    static_path=$SCRIPTPATH/dev/static
    mkdir -p $static_path
    static_name=static-$DATE.sql
    mysqldump --quick --column-statistics=0 -P$DB_PORT -h$DB_HOST -u$DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces --no-create-info -r $static_path/$static_name $DB_NAME coldspots task_force_protein_domains annotation_type
    gzip -f $static_path/$static_name

    # dump grant statements
    users_path=$SCRIPTPATH/dev/users
    mkdir -p $users_path
    users_name=users-$DATE.sql
    mysql --host $DB_HOST --port $DB_PORT -u$DB_READ_ONLY -p$DB_READ_ONLY_PW -e "SHOW GRANTS FOR CURRENT_USER();" $DB_NAME | grep $DB_NAME | sed "s/HerediVar_ahdoebm1/HerediVar/g" > $users_path/$users_name
    mysql --host $DB_HOST --port $DB_PORT -u$DB_USER -p$DB_USER_PW -e "SHOW GRANTS FOR CURRENT_USER();" $DB_NAME | grep $DB_NAME | sed "s/HerediVar_ahdoebm1/HerediVar/g" >> $users_path/$users_name
    mysql --host $DB_HOST --port $DB_PORT -u$DB_SUPER_USER -p$DB_SUPER_USER_PW -e "SHOW GRANTS FOR CURRENT_USER();" $DB_NAME | grep $DB_NAME | sed "s/HerediVar_ahdoebm1/HerediVar/g" >> $users_path/$users_name
    mysql --host $DB_HOST --port $DB_PORT -u$DB_ANNOTATION_USER -p$DB_ANNOTATION_USER_PW -e "SHOW GRANTS FOR CURRENT_USER();" $DB_NAME | grep $DB_NAME | sed "s/HerediVar_ahdoebm1/HerediVar/g" >> $users_path/$users_name
    gzip -f $users_path/$users_name


    # save data in local backup
    local_backup_folder=$(dirname "$ROOT")/backup/heredivar_data
    mkdir -p $local_backup_folder
    last_date=$(cat $SCRIPTPATH/most_recent_dump.txt)
    rm -f $local_backup_folder/data-$last_date.sql.gz
    cp $data_path/$data_name.gz $local_backup_folder/$data_name.gz

    # update most recent dump date
    echo $DATE > $SCRIPTPATH/most_recent_dump.txt
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    dump_path=$SCRIPTPATH/prod
    mkdir -p $dump_path
    dump_name=production-dump-$DATE.sql

    mysqldump --quick -h$DB_HOST -P$DB_PORT -u$DB_ADMIN -p$DB_ADMIN_PW --no-tablespaces -r$dump_path/$dump_name $DB_NAME
    gzip -f $dump_path/$dump_name
fi


# information after init_db.py
##mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/init_transcripts_w_tables.sql HerediVar_ahdoebm1  gene gene_alias transcript exon

##mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/task_force_protein_domains.sql HerediVar_ahdoebm1 task_force_protein_domains


#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/init.sql HerediVar_ahdoebm1 annotation_type classification_criterium classification_criterium_strength classification_scheme mutually_exclusive_criteria gene gene_alias pfam_id_mapping pfam_legacy task_force_protein_domains transcript 


#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_new.sql HerediVar_ahdoebm1 classification_criterium_strength classification_criterium
#mysqldump --quick -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_old.sql HerediVar_ahdoebm1_test classification_criterium_strength classification_criterium

#mysqldump --quick -h sql.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p --column-statistics=0 --no-tablespaces --no-create-info -r /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/temp.sql HerediVar_ahdoebm1 classification_scheme classification_criterium classification_criterium_strength mutually_exclusive_criteria mutually_inclusive_criteria

#mysql -h SRV011.img.med.uni-tuebingen.de -P 3306 -u ahdoebm1 -p HerediVar_ahdoebm1_test < /mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/database_dumper/init_db/criterium_new.sql



