

#!/bin/bash


#keycloak-18.0.0/bin/kcadm.sh config credentials --server http://localhost:5050/auth --realm master --user admin --client admin

keycloak-18.0.0/bin/kcadm.sh create realms -f src/frontend_celery/keycloak_export/HerediVar-realm.json --server http://localhost:5050/auth

keycloak-18.0.0/bin/kcadm.sh get realms