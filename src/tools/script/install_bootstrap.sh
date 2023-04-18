

#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "Download the specified bootstrap version to the specified directory"
   echo -e "\t-p The path where bootstrap will be installed"
   echo -e "\t-p The bootstrap version. Eg. 5.2.3"
   exit 1 # Exit script after printing help
}

while getopts "p:v:" opt
do
   case "$opt" in
      p ) path="$OPTARG" ;;
      v ) bsversion="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$path" ] || [ -z "$bsversion" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Downloading bootstrap $bsversion to $path."


mkdir -p $path

cd $path

wget -q https://github.com/twbs/bootstrap/releases/download/v$bsversion/bootstrap-$bsversion-dist.zip
unzip bootstrap-$bsversion-dist.zip
mv bootstrap-$bsversion-dist bootstrap
rm bootstrap-$bsversion-dist.zip
