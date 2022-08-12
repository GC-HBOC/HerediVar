#!/bin/bash

#source .venv/bin/activate

celery -A celery_module.main.celery worker --loglevel=info

