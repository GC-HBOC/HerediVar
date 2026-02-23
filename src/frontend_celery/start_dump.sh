#!/bin/bash
set -uo pipefail

we=""
args=("$@")
for ((i=0; i<${#args[@]}; i++)); do
  if [[ ${args[i]} == "-w" ]]; then
    we="${args[i+1]}"
    break
  fi
done

# Print helpFunction in case mandatory parameters are empty
if [ -z "$we" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

export WEBAPP_ENV=$we

MAIL_SUBJECT_SUCCESS="Backup SUCCESS on $(hostname)"
MAIL_SUBJECT_FAIL="Backup FAILED on $(hostname)"

DATE=$(date '+%F');

SCRIPT=$(readlink -f "$0")
ROOT=$(dirname $(dirname $(dirname "$SCRIPT")))
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
pwd

TOOSDIR=$ROOT/tools

set -o allexport
extension=env_
source $ROOT/.$extension$WEBAPP_ENV
set +o allexport

BACKUP_LOG_DIR=$ROOT/logs/backup
mkdir -p "$BACKUP_LOG_DIR"
BACKUP_LOG_FILE="$BACKUP_LOG_DIR/backup_$DATE.log"

./start_dump_worker.sh "$@" >> "$BACKUP_LOG_FILE" 2>&1
EXIT_CODE=$?

$TOOSDIR/script/cleanup.sh -w $WEBAPP_ENV -p $BACKUP_LOG_DIR -f backup_ -e .log >> "$BACKUP_LOG_FILE" 2>&1

if [ $EXIT_CODE -eq 0 ]; then
    echo "" >> "$BACKUP_LOG_FILE"
    echo "Backup completed successfully at $(date)." >> "$BACKUP_LOG_FILE"
    #mail -aFrom:$BACKUP_MAIL_FROM \
    #     -s "$MAIL_SUBJECT_SUCCESS" "$BACKUP_MAIL_TO" < "$BACKUP_LOG_FILE"
else
    echo "" >> "$BACKUP_LOG_FILE"
    echo "BACKUP FAILED at $(date) with code $EXIT_CODE." >> "$BACKUP_LOG_FILE"
    mail -aFrom:$BACKUP_MAIL_FROM \
         -s "$MAIL_SUBJECT_FAIL" "$BACKUP_MAIL_TO" < "$BACKUP_LOG_FILE"
fi



