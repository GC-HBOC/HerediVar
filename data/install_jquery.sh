
#!/bin/bash
set -e
set -o pipefail


helpFunction()
{
   echo ""
   echo "Usage: $0 -p path -v version"
   echo "Download the specified jQuery version to the specified directory"
   echo -e "\t-p The path where jQuery will be installed"
   echo -e "\t-p The bootstrap version. Eg. 3.6.3"
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
echo "Downloading jQuery $version to $path."


mkdir -p $path

cd $path

wget -q https://code.jquery.com/jquery-$version.min.js

mv jquery-$version.min.js jquery.min.js
