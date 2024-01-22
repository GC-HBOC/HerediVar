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
   echo -e "\t-v The ngs-bits version. Eg. 2022_10"
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
git clone --recursive https://github.com/imgag/ngs-bits.git
#git checkout $version && git submodule update --recursive --init ## select stable version once project is finished!
mv ngs-bits $foldername
cd $foldername
make build_3rdparty build_libs_release build_tools_release