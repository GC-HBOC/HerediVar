#!/bin/bash -e

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH
cd ../
pwd

echo "Installing keycloak for tests to " $(pwd)

# install keycloak
wget -q https://github.com/keycloak/keycloak/releases/download/18.0.0/keycloak-18.0.0.zip
unzip keycloak-18.0.0.zip
rm keycloak-18.0.0.zip

# initialize keycloak
keycloak-18.0.0/bin/kc.sh import --file ../../../resources/backups/keycloak_export/Heredivar-realm-test.json
#/mnt/storage2/users/ahdoebm1/HerediVar/resources/backups/keycloak_export/Heredivar-realm-test.json