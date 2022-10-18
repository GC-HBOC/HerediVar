#!/bin/bash

#source .venv/bin/activate

#celery -A celery_module.main.celery worker --loglevel=info

export WEBAPP_ENV=dev

celery -A celery_worker.celery worker --loglevel=info --concurrency=5 #--pool=solo