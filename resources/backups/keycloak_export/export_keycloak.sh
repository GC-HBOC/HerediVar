#!/bin/bash -e


SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH


ROOT=$(dirname $(dirname $(dirname "$SCRIPTPATH")))
TOOLS=$ROOT/tools
KEYCLOAK=$TOOLS/keycloak/bin

backups_folder=$SCRIPTPATH/backups
mkdir -p $backups_folder
DATE=$(date '+%F');
mkdir -p $backups_folder/$DATE

$KEYCLOAK/kc.sh export --dir $backups_folder/$DATE --realm HerediVar --users same_file

#sed 's/"directAccessGrantsEnabled" : false,/"directAccessGrantsEnabled" : true,/g' Heredivar-realm.json > test_config/Heredivar-realm-test.json