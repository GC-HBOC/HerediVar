#!/bin/bash
set -e
set -o pipefail
set -o verbose


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version -n folder_name"
   echo "This script installs a python with all required packages for heredivar"
   echo -e "\t-p The path python will be installed"
   exit 1 # Exit script after printing help
}

while getopts "p:v:n:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      v ) version="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$basedir" ] || [ -z "$version" ] || [ -z "$foldername" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Setting up python $version in $basedir/$foldername..."


cd $basedir
wget https://www.python.org/ftp/python/$version/Python-$version.tgz
tar -zxvf Python-$version.tgz
cd Python-$version
mkdir -p $foldername
./configure --prefix=$basedir/$foldername
make
make install

cd ..
cd $foldername/bin
./pip3 install virtualenv

cd $basedir
rm Python-$version.tgz