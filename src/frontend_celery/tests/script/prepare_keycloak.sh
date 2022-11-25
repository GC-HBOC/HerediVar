#!/bin/bash -e

# install keycloak
wget -q https://github.com/keycloak/keycloak/releases/download/18.0.0/keycloak-18.0.0.zip
unzip keycloak-18.0.0.zip
rm keycloak-18.0.0.zip

# initialize keycloak
keycloak-18.0.0/bin/kc.sh import --file src/frontend_celery/keycloak_export/Heredivar-realm-test.json