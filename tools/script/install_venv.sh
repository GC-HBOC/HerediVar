#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p venvpath -n venvname -y pythonpath"
   echo "This script installs a python venv with all required packages for heredivar"
   echo -e "\t-p The path ngs-bits will be installed"
   exit 1 # Exit script after printing help
}

while getopts "p:n:y:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      n ) venvname="$OPTARG" ;;
      y ) pythonpath="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$basedir" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Setting up python venv in $basedir..."


# do this on windows to allow activation of virtualenvs
#Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process


$pythonpath -m venv $basedir/$venvname
source $basedir/$venvname/bin/activate

python3 -m pip install --upgrade pip
pip install wheel
pip install setuptools
python3 -m pip install --upgrade setuptools wheel

pip install flask flask-session flask-paginate
#pip install Flask-OIDC
pip install authlib
pip install mysql-connector-python


pip install spliceai tensorflow
pip install CrossMap



pip install blinker
pip install lxml


pip install celery redis

#pip install reportlab

pip install python-dotenv


pip install biopython



pip install jsonschema

pip install pytest


pip install gunicorn
pip install gevent

pip install flask-mail


pip install pytest-playwright
playwright install
#pip install pytest-asyncio
pip install pytest-flask


pip install xlsx2csv


pip install gffutils

