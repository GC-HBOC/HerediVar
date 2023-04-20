

#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "Download the specified datatables version to the specified directory"
   echo -e "\t-p The path where datatables will be installed"
   echo -e "\t-p The datatables version. Eg. 1.13.4"
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

path=$path/datatables

mkdir -p $path

cd $path

wget -q https://cdn.datatables.net/$bsversion/js/jquery.dataTables.min.js
wget -q https://cdn.datatables.net/$bsversion/css/jquery.dataTables.min.css
