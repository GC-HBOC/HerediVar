#!/bin/bash


root="$(dirname `pwd`)"
tools=$root/src/tools/
keycloak_path=$tools/keycloak-18.0.0

$keycloak_path/bin/kc.sh start-dev