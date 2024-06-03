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
   echo -e "\t-v The keycloak version. Eg. 18.0.0"
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
echo "Setting up python $version in $basedir/$foldername..."


cd $basedir
wget -q https://github.com/keycloak/keycloak/releases/download/$version/keycloak-$version.zip
unzip keycloak-$version.zip
rm keycloak-$version.zip
mv keycloak-$version $foldername

# init keycloak
#KEYCLOAK_ADMIN=xxx
#KEYCLOAK_ADMIN_PASSWORD=xxx
#keycloak-18.0.0/bin/kc.sh import --file /mnt/storage2/users/ahdoebm1/HerediVar/src/frontend_celery/keycloak_export/Heredivar-realm.json
#keycloak-18.0.0/bin/kc.sh build --http-relative-path /kc


# production commands:
# follow this tutorial: https://gist.github.com/matissime/f9c6e72826862d5fd8a582289b2a2d5f
#mkdir -p keycloak/data/import/
#cp $basedir/tools/data/init_keycloak.json keycloak/data/import/
#keycloak/bin/kc.sh --verbose start --auto-build --import-realm --http-relative-path=/kc --db mysql --proxy=edge --hostname-strict=false --log-level INFO --http-host=localhost --db-url "jdbc:mysql://$KEYCLOAK_DB_HOST:$KEYCLOAK_DB_PORT/$KEYCLOAK_DB_SCHEME?allowPublicKeyRetrieval=true\&useSSL=false" --db-url-host $KEYCLOAK_DB_HOST --db-url-port $KEYCLOAK_DB_PORT --db-schema $KEYCLOAK_DB_SCHEME --http-port=$KEYCLOAK_PORT --db-username $KEYCLOAK_DB_USERNAME --db-password $KEYCLOAK_DB_PW
#rm keycloak/data/import/init_keycloak.json
