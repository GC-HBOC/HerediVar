#!/bin/bash


root=/mnt/users/ahdoebm1/HerediVar
tools=$root/src/tools
datadir=$root/data/dbs
testdir=$root/src/annotation_service/tests
testdatadir=$testdir/data/testdbs

# prepare folder
mkdir -p $testdatadir


# get dbsnp
zcat $datadir/dbSNP/dbSNP_v155.vcf.gz | head -n 100 > $testdatadir/dbSNP.vcf
#chr1    10001   rs1570391677    T       A       .       .       RS=1570391677;dbSNPBuildID=154;SSR=0;PSEUDOGENEINFO=DDX11L1:100287102;VC=SNV;R5;GNO;FREQ=KOREAN:0.9891,0.0109,.|SGDP_PRJ:0,1,.|dbGaP_PopFreq:1,.,0;COMMON

bgzip -f $testdatadir/dbSNP.vcf
tabix -p vcf $testdatadir/dbSNP.vcf.gz




