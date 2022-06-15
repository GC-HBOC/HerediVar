#!/bin/bash


root="$(dirname `pwd`)"
basecertbot=$root/flask_keycloak_test_2/certbot

configdir=$basecertbot/config
workdir=$basecertbot/work
logsdir=$basecertbot/logs

mkdir -p $basecertbot
mkdir -p $configdir
mkdir -p $workdir
mkdir -p $logsdir

echo $basecertbot

certbot certonly --standalone --preferred-challenges http -d srv018.img.med.uni-tuebingen.de:5050 --dry-run --config-dir $configdir --work-dir $workdir --logs-dir $logsdir