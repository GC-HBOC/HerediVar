#!/bin/bash


root="$(dirname `pwd`)"
tools=$root/tools
keycloak_path=$tools/keycloak-18.0.0

export NO_PROXY=srv018.img.med.uni-tuebingen.de

$keycloak_path/bin/kc.sh start-dev --hostname srv018.img.med.uni-tuebingen.de --http-port 5050 --features=admin-fine-grained-authz # --log-level debug