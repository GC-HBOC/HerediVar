#!/bin/bash

#source .venv/bin/activate

celery -A main.celery worker --loglevel=info