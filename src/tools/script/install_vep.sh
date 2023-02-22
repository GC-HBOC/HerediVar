#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version -d data-version"
   echo "This script installs VEP"
   echo -e "\t-p The path VEP will be installed"
   echo -e "\t-v The VEP version. Eg. 104.3"
   echo -e "\t-d The VEP data version. Eg. 104"
   exit 1 # Exit script after printing help
}

while getopts "p:v:d:" opt
do
   case "$opt" in
      p ) basedir="$OPTARG" ;;
      v ) version="$OPTARG" ;;
      d ) dataversion="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$basedir" ] || [ -z "$version" ] || [ -z "$dataversion" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "Installing VEP $version to $basedir..."


vep_install_dir=$basedir/ensembl-vep-release-$version/
vep_cpan_dir=$vep_install_dir/cpan/
vep_data_dir=$basedir/ensembl-vep-data-$version/

# download ensembl-vep
mkdir -p $vep_install_dir
cd $basedir
wget https://github.com/Ensembl/ensembl-vep/archive/release/$version.tar.gz
tar -C $vep_install_dir --strip-components=1 -xzf $version.tar.gz
rm $version.tar.gz

#install dependencies
mkdir -p $vep_cpan_dir
cpanm -l $vep_cpan_dir -L $vep_cpan_dir Set::IntervalTree URI::Escape Carp::Assert JSON::XS PerlIO::gzip DBI

#download VEP cache data
mkdir -p $vep_data_dir
cd $vep_data_dir
mkdir -p ftp
cd ftp
wget ftp://ftp.ensembl.org/pub/release-$dataversion/variation/indexed_vep_cache/homo_sapiens_vep_$dataversion_GRCh38.tar.gz
wget ftp://ftp.ensembl.org/pub/release-$dataversion/variation/indexed_vep_cache/homo_sapiens_refseq_vep_$dataversion_GRCh38.tar.gz

#install ensembl-vep
PERL5LIB=$vep_install_dir/Bio/:$vep_cpan_dir/lib/perl5/:$PERL5LIB
cd $vep_install_dir
perl INSTALL.pl --SPECIES homo_sapiens,homo_sapiens_refseq --ASSEMBLY GRCh38 --AUTO acp --PLUGINS REVEL,CADD,MaxEntScan --NO_UPDATE --NO_BIOPERL --CACHEDIR $vep_data_dir/cache --CACHEURL $vep_data_dir/ftp --NO_TEST --NO_HTSLIB
cp $vep_data_dir/cache/Plugins/*.pm $vep_install_dir/modules/ #should not be necessary - probably a bug in the VEP installation script when using the CACHEDIR option (MS)

# install MaxEntScan (for MaxEntScan plugin)
#cd $vep_install_dir
#mkdir -p MaxEntScan
#cd MaxEntScan
#wget http://hollywood.mit.edu/burgelab/maxent/download/fordownload.tar.gz
#tar xzf fordownload.tar.gz
#mv fordownload/* .
#rm -rf fordownload*
#chmod -R 755 $vep_install_dir/MaxEntScan