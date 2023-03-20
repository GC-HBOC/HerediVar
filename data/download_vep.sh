#!/bin/bash
set -e
set -o pipefail
set -o verbose


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path"
   echo "This script installs VEP version 107.0"
   echo -e "\t-p The path where VEP will be installed."
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

echo "Installing VEP to $path"


cd $path

vep_install_dir=$path/ensembl-vep-release-107.0
vep_data_dir=$path/ensembl-vep-release-107.0/data
cpan_dir=$path/ensembl-vep-release-107.0/cpan

# download ensembl-vep
mkdir -p $vep_install_dir
cd $vep_install_dir
wget https://github.com/Ensembl/ensembl-vep/archive/release/107.0.tar.gz
tar -C $vep_install_dir --strip-components=1 -xzf 107.0.tar.gz
rm 107.0.tar.gz

#install dependencies
mkdir -p $cpan_dir
cpanm -l $cpan_dir -L $cpan_dir Set::IntervalTree URI::Escape DB_File Carp::Assert JSON::XS PerlIO::gzip DBI

#download VEP cache data
mkdir -p $vep_data_dir
cd $vep_data_dir
mkdir -p ftp
cd ftp
wget ftp://ftp.ensembl.org/pub/release-107/variation/indexed_vep_cache/homo_sapiens_vep_107_GRCh38.tar.gz
wget https://ftp.ensembl.org/pub/release-107/variation/indexed_vep_cache/homo_sapiens_refseq_vep_107_GRCh38.tar.gz



#install ensembl-vep
PERL5LIB=$vep_install_dir/Bio/:$cpan_dir/lib/perl5/:$PERL5LIB
cd $vep_install_dir
perl INSTALL.pl --SPECIES homo_sapiens,homo_sapiens_refseq --ASSEMBLY GRCh38 --AUTO acp --PLUGINS REVEL,CADD,MaxEntScan --NO_UPDATE --NO_BIOPERL --CACHEDIR $vep_data_dir/cache --CACHEURL $vep_data_dir/ftp --NO_TEST --NO_HTSLIB
cp $vep_data_dir/cache/Plugins/*.pm $vep_install_dir/modules/ #should not be necessary - probably a bug in the VEP installation script when using the CACHEDIR option (MS)

# install MaxEntScan (for MaxEntScan plugin)
cd $vep_install_dir
mkdir -p MaxEntScan
cd MaxEntScan
wget http://hollywood.mit.edu/burgelab/maxent/download/fordownload.tar.gz
tar xzf fordownload.tar.gz
#mv fordownload/* .
#rm -rf fordownload*
chmod -R 755 $vep_install_dir/MaxEntScan

#### !!! SET THE PERL5LIB env variable when running vep !!! ####