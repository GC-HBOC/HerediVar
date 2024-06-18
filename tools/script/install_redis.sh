#!/bin/bash
set -e
set -o pipefail
set -o verbose


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername"
   echo "This script installs REDIS"
   echo -e "\t-p The path where redis will be installed."
   exit 1 # Exit script after printing help
}

while getopts "p:n:" opt
do
   case "$opt" in
      p ) basepath="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$basepath" ] || [ -z "$foldername" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

echo "Installing redis to $basepath/$foldername"

mkdir -p $basepath
cd $basepath
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
rm redis-stable.tar.gz
cd redis-stable
make
cd ..
mv redis-stable $foldername
