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
   echo -e "\t-p The bootstrap version. Eg. 2.15.0"
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
echo "Setting up igv js $version in $basedir/$foldername..."





mkdir -p $basedir/$foldername

cd $basedir/$foldername

# official release
#wget -q https://cdn.jsdelivr.net/npm/igv@$version/dist/igv.min.js

# CSP conform version
# download csp conform version from: https://download.imgag.de/ahdoebm1/igv/
wget -q https://download.imgag.de/ahdoebm1/igv/igv.css
wget -q https://download.imgag.de/ahdoebm1/igv/igv.esm.js
mkdir data
cd data
wget -q https://download.imgag.de/ahdoebm1/igv/data/cytoBandIdeo.txt
wget -q https://download.imgag.de/ahdoebm1/igv/data/hg38_alias.tab
wget -q https://download.imgag.de/ahdoebm1/igv/data/refgene.txt
wget -q https://download.imgag.de/ahdoebm1/igv/data/refgene_ngsd.gff3
sort -k1,1V -k4,4n -k5,5rn -k3,3r refgene_ngsd.gff3 > refgene_ngsd_sorted.gff3
mv refgene_ngsd_sorted.gff3 refgene_ngsd.gff3
bgzip refgene_ngsd.gff3
tabix -p gff refgene_ngsd.gff3.gz