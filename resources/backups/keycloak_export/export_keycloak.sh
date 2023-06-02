#!/bin/bash -e


SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH

keycloak_path=/mnt/storage2/users/ahdoebm1/HerediVar/src/tools/keycloak/bin

$keycloak_path/kc.sh export --file Heredivar-realm.json --realm HerediVar

sed 's/"directAccessGrantsEnabled" : false,/"directAccessGrantsEnabled" : true,/g' Heredivar-realm.json > Heredivar-realm-test.json