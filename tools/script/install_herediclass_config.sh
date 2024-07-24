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
echo "Updating automatic classification config in $path."



variant_classification_path=$path/$foldername


# adjust configuration
cd $variant_classification_path
cp config.yaml config_production.yaml
sed -r -i "s:/home/katzkean/:$variant_classification_path/:g" config_production.yaml
sed -r -i "s:/gene_specific:/gene_specific_production:g" config_production.yaml
sed -r -i "s:variant_classification/::g" config_production.yaml

gene_specific_config_path=$variant_classification_path/gene_specific
extension=_production
gene_sepcific_config_path_production=$gene_specific_config_path$extension
rm -rf $gene_sepcific_config_path_production
cp -r $gene_specific_config_path $gene_sepcific_config_path_production
for filename in $gene_sepcific_config_path_production/*.yaml; do
   sed -r -i "s:/home/katzkean/:$variant_classification_path/:g" $filename
   sed -r -i "s:variant_classification/::g" $filename
done



