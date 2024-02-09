#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -n foldername"
   echo "Download the automatic classification algorithm to the specified directory"
   echo -e "\t-p The path where bootstrap will be installed"
   exit 1 # Exit script after printing help
}

while getopts "p:n:" opt
do
   case "$opt" in
      p ) path="$OPTARG" ;;
      n ) foldername="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$path" ] || [ -z "$foldername" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi
# Begin script in case all parameters are correct
echo "Downloading the automatic classification algorithm to $path."


mkdir -p $path
cd $path

git clone https://github.com/akatzke/variant_classification.git $foldername

variant_classification_path=$path/$foldername

cd $variant_classification_path
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
tar -zxvf Python-3.10.13.tgz
cd Python-3.10.13
mkdir -p .localpython
./configure --prefix=$variant_classification_path/.localpython
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
pip install pyensembl==2.2.9
pip install hgvs
pip install pybedtools
pip install openpyxl
pip install jsonschema
pip install pandas
pip install fastapi
pip install uvicorn

cd $variant_classification_path
bash $variant_classification_path/install_dependencies/install_pyensembl.sh -v 110

sed -r -i "s:/variant_classification::g" $variant_classification_path/install_dependencies/download_data.sh

bash $variant_classification_path/install_dependencies/download_data.sh -p $variant_classification_path


cd databases/Clinvar
wget --no-check-certificate https://download.imgag.de/ahdoebm1/extern/clinvar_spliceai_all_sorted.vcf.gz
in_path_spliceai_clinvar=$variant_classification_path/databases/Clinvar/clinvar_spliceai_all_sorted.vcf.gz
python $variant_classification_path/install_dependencies/data_filter_clinvar.py -i $in_path_spliceai_clinvar


# adjust configuration
cd $variant_classification_path
cp config.yaml config_production.yaml
sed -r -i "s:/home/katzkean/:$variant_classification_path/:g" config_production.yaml
sed -r -i "s:variant_classification/::g" config_production.yaml

gene_specific_config_path=$variant_classification_path/gene_specific
for filename in $gene_specific_config_path/*.yaml; do
   sed -r -i "s:/home/katzkean/:$variant_classification_path/:g" $filename
   sed -r -i "s:variant_classification/::g" $filename
done



