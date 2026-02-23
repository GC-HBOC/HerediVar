#!/bin/bash
set -euo pipefail

# set defaults
is_dry="False"
PREFIX=""
EXT=""

helpFunction()
{
   echo ""
   echo "Usage: $0 -w env"
   echo "This script cleans old backup files"
   echo -e "\t-w Provide 'dev' for development server and 'prod' for production environment"
   echo -e "\t-d Perform a dry run (ie. list files which would be deleted without actually deleting them)"
   echo -e "\t-p Path with files to cleanup"
   echo -e "\t-f Prefix for files to cleanup"
   echo -e "\t-e File extension to cleanup"
   exit 1 # Exit script after printing help
}

while getopts "w:p:f:e:d" opt
do
   case "$opt" in
      w ) we="$OPTARG" ;;
      d ) is_dry="True" ;;
      p ) dump_path="$OPTARG" ;;
      f ) PREFIX="$OPTARG" ;;
      e ) EXT="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$we" ] || [ -z "$dump_path" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

export WEBAPP_ENV=$we

if [ "$we" = "dev" ]; then
    echo "Automatically activating dry run because you are working in dev mode"
    is_dry="True"
fi

if [ "$is_dry" = "True" ]; then
   echo "Running in DRY RUN mode - no files will be deleted!"
fi
echo "Cleaning up database dumps for $WEBAPP_ENV environment"

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
pwd


#dump_path=$SCRIPTPATH/$WEBAPP_ENV

NOW=$(date +%s)
DAY_7_AGO=$(date -d "7 days ago" +%s)
DAY_30_AGO=$(date -d "30 days ago" +%s)
DAY_365_AGO=$(date -d "730 days ago" +%s)
declare -A weekly_keep
declare -A monthly_keep

cd $dump_path

# Sort newest first
for file in $(
    ls -1 ${PREFIX}*${EXT} ${PREFIX}*${EXT}.gz 2>/dev/null | sort -r
); do
    # Extract date: YYYY-MM-DD
    date_str=$(echo "$file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}') || continue
    file_ts=$(date -d "$date_str" +%s)

    # Case 1: keep all dumps last week
    if (( file_ts >= DAY_7_AGO )); then
        continue
    fi

    # Case 2: delete older than 1 year
    if (( file_ts < DAY_365_AGO )); then
        if [ "$is_dry" = "True" ]; then
            echo "Dry run: Deleting (older than 2 years): $file"
        else
            echo "Deleting (older than 2 years): $file"
            rm "$file"
        fi
        continue
    fi


    # Case 3: Keep newest from each week (8–30 days old)
    if (( file_ts >= DAY_30_AGO )); then
        week_key=$(date -d "$date_str" +%G-%V) # ISO year-week
        if [[ -z "${weekly_keep[$week_key]:-}" ]]; then
            weekly_keep[$week_key]="$file"
        else
            if [ "$is_dry" = "True" ]; then
                echo "Dry run: Deleting (extra weekly $week_key): $file"
            else
                echo "Deleting (extra weekly $week_key): $file"
                rm "$file"
            fi
        fi
        continue
    fi

    # Case 4: Keep newest from each month (31–365 days old)
    month_key=$(date -d "$date_str" +%Y-%m)
    if [[ -z "${monthly_keep[$month_key]:-}" ]]; then
        monthly_keep[$month_key]="$file"
    else
        if [ "$is_dry" = "True" ]; then
            echo "Dry run: Deleting (extra monthly $month_key): $file"
        else
            echo "Deleting (extra monthly $month_key): $file"
            rm "$file"
        fi
    fi
done





