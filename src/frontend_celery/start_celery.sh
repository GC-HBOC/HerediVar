#!/bin/bash

#source .venv/bin/activate

#celery -A celery_module.main.celery worker --loglevel=info

celery -A celery_worker.celery worker --loglevel=info --concurrency=5 #--pool=solo