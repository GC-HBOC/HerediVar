

#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path"
   echo "Download the automatic classification algorithm to the specified directory"
   echo -e "\t-p The path where bootstrap will be installed"
   exit 1 # Exit script after printing help
}

while getopts "p:" opt
do
   case "$opt" in
      p ) path="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$path" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi
# Begin script in case all parameters are correct
echo "Downloading the automatic classification algorithm to $path."


mkdir -p $path
cd $path

git clone https://github.com/akatzke/variant_classification.git

variant_classification_path=$path/variant_classification

cd $variant_classification
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
tar -zxvf Python-3.10.13.tgz
cd Python-3.10.13
mkdir -p .localpython
./configure --prefix=$path/variant_classification/.localpython
make
make install

cd ..
cd .localpython/bin
./pip3 install virtualenv


cd ../..
.localpython/bin/python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install wheel
pip install setuptools
python3 -m pip install --upgrade setuptools wheel
pip install pyyaml
pip install cyvcf2
pip install biopython
pip install pyensembl
pip install hgvs
pip install pybedtools
pip install openpyxl
pip install jsonschema
pip install pandas

cd $variant_classification
bash install_dependencies/install_pyensembl.sh -v 110

bash install_dependencies/download_data.sh -p $path


# adjust configuration
cp config.yaml config_production.yaml
sed -r -i "s:/home/katzkean/:$variant_classification/:g" config_production.yaml
sed -r -i "s:variant_classification/data/critical_region:data/critical_region:g" config_production.yaml


sed -r -i "s:/home/katzkean/:$variant_classification/:g" gene_specific/acmg_brca1.yaml
sed -r -i "s:variant_classification/data/critical_region:data/critical_region:g" gene_specific/acmg_brca1.yaml

sed -r -i "s:/home/katzkean/:$variant_classification/:g" gene_specific/acmg_brca2.yaml
sed -r -i "s:variant_classification/data/critical_region:data/critical_region:g" gene_specific/acmg_brca2.yaml


