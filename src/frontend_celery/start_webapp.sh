#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd $SCRIPTPATH

echo "${WEBAPP_ENV}"

if [ -z "${WEBAPP_ENV}" ]
then
    echo Environment variable WEBAPP_ENV not set.
    exit 1
fi

if [ "${WEBAPP_ENV}" == "dev" ]
then
    python3 main.py
fi

if [ "${WEBAPP_ENV}" == "prod" ]
then
    gunicorn -b heredivar.uni-koeln.de:8000 -w 4 'webapp:create_app()'
    #gunicorn -b SRV018.img.med.uni-tuebingen.de:8001 -w 1 'webapp:create_app()'
fi