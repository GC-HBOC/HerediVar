#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "This script installs samtools"
   echo -e "\t-p The path samtools will be installed"
   echo -e "\t-v The samtools version. Eg. 1.11"
   exit 1 # Exit script after printing help
}

while getopts "p:v:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      v ) version="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$basedir" ] || [ -z "$version" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Installing samtools $version to $basedir..."



cd $basedir
wget https://github.com/samtools/samtools/releases/download/$version/samtools-$version.tar.bz2
tar xjf samtools-$version.tar.bz2
cd samtools-$version
make
rm samtools-$version.tar.bz2
#cd ..
#mv samtools-$version samtools



