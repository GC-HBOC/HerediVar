#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "This script installs htslib"
   echo -e "\t-p The path htslib will be installed"
   echo -e "\t-v The htslib version. Eg. 1.16"
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
echo "Installing htslib $version to $basedir..."


cd $basedir
wget https://github.com/samtools/htslib/releases/download/$version/htslib-$version.tar.bz2
tar -vxjf htslib-$version.tar.bz2
cd htslib-$version
make
rm -f htslib-$version.tar.bz2