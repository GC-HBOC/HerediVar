#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "This script installs keycloak"
   echo -e "\t-p The path keycloak will be installed"
   echo -e "\t-v The keycloak version. Eg. 18.0.0"
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
echo "Installing keycloak $version to $basedir..."


cd $basedir
wget -q https://github.com/keycloak/keycloak/releases/download/$version/keycloak-$version.zip
unzip keycloak-$version.zip
rm keycloak-$version.zip