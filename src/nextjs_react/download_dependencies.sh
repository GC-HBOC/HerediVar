#!/bin/bash
set -e
set -o pipefail
set -o verbose


root="$(dirname `pwd`)"
tools=$root/tools


# install node.js see: https://github.com/nodejs/help/wiki/Installation and https://nodejs.org/en/download/
VERSION=v16.15.0
DISTRO=linux-x64

cd $tools
mkdir -p nodejs
cd nodejs

#wget https://nodejs.org/dist/$VERSION/node-$VERSION-$DISTRO.tar.xz
#tar -xJvf node-$VERSION-$DISTRO.tar.xz


nodejs=$tools/nodejs/node-$VERSION-$DISTRO/bin
echo $nodejs

export PATH=/home/ukt.ad.local/ahdoebm1/HerediVar_React/nodejs/node-$VERSION-$DISTRO/bin:$PATH

export PATH=/mnt/users/ahdoebm1/HerediVar/src/nextjs_react/node-v16.15.0-linux-x64/bin:$PATH

$nodejs/npx create-next-app heredivar --use-npm


