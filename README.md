# HerediVar
Prevalence of variants of unknown significace (VUS) among few well studied risk genes is at 20%. Thus, every fiveth patient gets a VUS report which can lead to uncertainty and inapropriate therapy of the tumor.
This project aims at integrating bioinformatics and functional genomics in the clinical classification of genetic variation for hereditary breast and ovarian cancer.

To close the gap between genetic data analysis, variant classification and clinical interpretation, we developed an interactive variant database "HerediVar" which features ...
- automatical gathering of both, public and private annotation data for germline variants while ensuring data privacy
- plug-and-play system for annotation sources
- multiple annotation schemes (e. g. ACMG) and easy integration of updates
- user role management
- a consensus procedure for classifications
- publishing of classifications

The live version is hosted online at [https://heredivar.uni-koeln.de/](https://heredivar.uni-koeln.de/).

Further details about the features of HerediVar can be found here: [https://heredivar.uni-koeln.de/documentation](https://heredivar.uni-koeln.de/documentation)

## Tooling
HerediVar uses the following tools:
- Backend: Python Flask
- Background tasks: Celery + Redis
- Frontend: Bootstrap, JQuery
- Authentication and authorization: Keycloak

## Installation
The HerediVar installation is quite lengthy, because it requires a lot of data and tools. It is recommended that you have at least 500 GB of free disk space to install HerediVar. HerediVar was developed and tested on Linux Ubuntu 20.04. So the following steps assume you are using this operating system. (There is however a good chance that HerediVar will work properly on any operating system, but you might need to adjust the installation scripts.)

Note: the HerediVar installation is mostly self-contained. This means it will install all tools within the repository folder. If you already have one or another tool in place and want to reuse that installation you can skip the installation step and adjust the paths in HerediVar/makefile and HerediVar/src/common/paths.py.

Note: If you want to use another version of a tool, package or database you can modify the makefile. There are variables for each tool and database which have a versioned download.

Note: Every package or tool has utility functions to update or remove. For example: to update gnomAD ```make gnomad_update``` (remove and install again) and to remove gnomAD ```make gnomad_clean```

### 1. install system requirements
First ensure that all system requirements are met. This requires administrator priviegles and the whole step can be skipped if you already have the packages mentioned below.

[optional] Make sure the package manager is up-to-date:
```
sudo apt-get update
```
Install system packages.

Note: This already installs required packages for third party tools.
```
sudo apt-get install autoconf automake make gcc perl zlib1g-dev libbz2-dev liblzma-dev libcurl4-gnutls-dev libssl-dev libncurses5-dev libncursesw5-dev
sudo apt-get install g++ libqt5xmlpatterns5-dev libqt5sql5-mysql libcurl4 libcurl4-openssl-dev
sudo apt-get install qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools
sudo apt-get install -y mariadb-server
sudo apt-get install default-jdk -y
sudo apt install genometools
sudo apt install libdb-dev
sudo apt-get install libpq-dev libffi-dev libsqlite3-dev
```
### 3. install tools
Next, install the following tools: python, venv, htslib, keycloak, redis, vep, ngs_bits, samtools and herediclass. You may choose to install every tool on its own (eg. ```make python```) or install all at once using
```
make tools
```
Also, install javascript libraries: bootstrap, igv, jquery and datatables. 

Note: In production it is recommended to use the content security policy (CSP) header. However, IGV.js is not CSP conform. Thus, I compiled my own IGV.js. If you want to use HerediVar with CSP you have to compile your own IGV as well. You also want to download cytoBandIdeo.txt, hg38_alias.tab, refgene.txt and a refgene.gff3. Further information on how to install IGV.js can be found on their GitHub [https://github.com/igvteam/igv.js/](https://github.com/igvteam/igv.js/).

Again, they can be installed on its own (eg. ```make bootstrap```) or all together using
```
make js_libs
```
### 4. download annotation databases
This step takes the longest time since a lot of data needs to be downloaded and prepared to be digestable by HerediVar.

First install the reference genomes: grch37, grch38 and chainfile or install all at once using
```
make genomes
```

Install data that is required for database initialization: omim, mapping_tables, pfam, mane, refseq, ensembl, orphanet and hgnc. Install independently or all at once using
```
make initialization_data
```

Install data that is required for variant annotation: brca_exchange, flossies, dbsnp, phylop, cadd, revel, cancerhotspots, tp53, gnomad, hci_priors, spliceai, bayesdel, clinvar, coldspot and cspecassays. Install independently or all at once using
```
make annotation_data
```

Note: Although HerediVar only annotates the variant identifier from COSMIC it requires a license. Once you have the data you can take a look two conversion scripts that were used: [https://github.com/imgag/megSAP/blob/master/src/Tools/db_converter_cosmic.php](https://github.com/imgag/megSAP/blob/master/src/Tools/db_converter_cosmic.php) and [https://github.com/GC-HBOC/HerediVar/blob/main/data/script/download_cosmic.sh](https://github.com/GC-HBOC/HerediVar/blob/main/data/script/download_cosmic.sh)

### 5. initialize HerediVar database
First connect to the mariadb (or mysql) console and create a new scheme:
```
CREATE DATABASE HerediVar;
```
Note: You can use whatever name you want. Simply change the config according to your choice (see subsequent sections).

Now create five database users:
- HerediVar_user
- HerediVar_superuser
- HerediVar_annotation
- HerediVar_read_only
- HerediVar_admin

Note: You can again use whatever database usernames you want. Simply change the config according to your choice (see subsequent sections).

Provide the HerediVar_admin user with all privileges on the new database
```
GRANT ALL PRIVILEGES ON HerediVar.* TO 'HerediVar_admin'@'localhost' WITH GRANT OPTION;
```
Disconnect from the mariadb console and verify that login works with HerediVar_admin and that you see the database.

Create the database structure. Use the most recent dump
```
mrd=$(cat HerediVar/resources/backups/database_dumper/most_recent_dump.txt)
gunzip HerediVar/resources/backups/database_dumper/dev/structure/structure-$mrd.sql.gz
mysql -p -u HerediVar_admin HerediVar < HerediVar/resources/backups/database_dumper/dev/structure/structure-$mrd.sql
```

Initialize user privileges

Note: If you changed the database name / database users you have to adjust the names in the users-$mrd.sql file. 
```
gunzip HerediVar/resources/backups/database_dumper/dev/users/users-$mrd.sql.gz
mysql -p -u HerediVar_admin HerediVar < HerediVar/resources/backups/database_dumper/dev/users/users-$mrd.sql
```

Initialize static table data
```
gunzip HerediVar/resources/backups/database_dumper/dev/static/static-$mrd.sql.gz
mysql -p -u HerediVar_admin HerediVar < HerediVar/resources/backups/database_dumper/dev/static/static-$mrd.sql
source HerediVar/.venv/bin/activate
python3 HerediVar/tools/init_db.py
```

### 6 Initialize Keycloak
Run the following commands from a terminal and replace "xxx" with a username and **STRONG** password. 
```
KEYCLOAK_ADMIN=xxx
KEYCLOAK_ADMIN_PASSWORD=xxx
mrd=$(cat HerediVar/resources/backups/keycloak_export/most_recent_dump.txt)
HerediVar/tools/keycloak-18.0.0/bin/kc.sh import --file HerediVar/resources/backups/keycloak_export/dev/$mrd/HerediVar-realm.json
```


## Start HerediVar
You have to start five services which must run any time. You can start them using the commands below. Each start script requires you to specify the environment (-w option). Set this variable to
- "dev" if you are developing HerediVar
- "prod" in a production installation

The commands to start the services are:
- Redis: ```HerediVar/src/frontend_celery/start_redis.sh -w $WEBAPP_ENV```
- HerediVar Flask server: ```HerediVar/src/frontend_celery/start_webapp.sh -w $WEBAPP_ENV```
- Celery: ```HerediVar/src/frontend_celery/start_celery.sh -w $WEBAPP_ENV```
- Keycloak: ```HerediVar/src/frontend_celery/start_keycloak.sh -w $WEBAPP_ENV```
- HerediClassify: ```HerediVar/src/frontend_celery/start_herediclass.sh -w $WEBAPP_ENV```

Note: I recommend to start Redis before HerediVar and Celery because both of them connect to Redis to store data

Note: In a production environment you should use systemd to always keep these services alive

## Configure HerediVar




## Run tests


## Contribute and Questions
If you are interested in contributing classifications to HerediVar please reach out to Jan Hauke ().

If you have questions about classifications on HerediVar please use the online form on our website: [https://heredivar.uni-koeln.de/contact](https://heredivar.uni-koeln.de/contact)
