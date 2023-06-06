
#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "Download the specified igv.js version to the specified directory"
   echo -e "\t-p The path where igv.js will be installed"
   echo -e "\t-p The bootstrap version. Eg. 2.15.0"
   exit 1 # Exit script after printing help
}

while getopts "p:v:" opt
do
   case "$opt" in
      p ) path="$OPTARG" ;;
      v ) version="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$path" ] || [ -z "$version" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Downloading igv $version to $path/igv."


mkdir -p $path/igv

cd $path/igv

# official release
#wget -q https://cdn.jsdelivr.net/npm/igv@$version/dist/igv.min.js

# CSP conform version
wget -q https://download.imgag.de/ahdoebm1/igv/igv.css
wget -q https://download.imgag.de/ahdoebm1/igv/igv.esm.js
mkdir data
cd data
wget -q https://download.imgag.de/ahdoebm1/igv/data/cytoBandIdeo.txt
wget -q https://download.imgag.de/ahdoebm1/igv/data/hg38_alias.tab
wget -q https://download.imgag.de/ahdoebm1/igv/data/refgene.txt
wget -q https://download.imgag.de/ahdoebm1/igv/data/refgene_ngsd.gff3