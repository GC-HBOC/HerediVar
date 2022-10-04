
#!/bin/bash

SCRIPT=$(readlink -f "$0")
echo $SCRIPT
SCRIPTPATH=$(dirname "$SCRIPT")
echo $SCRIPTPATH
SCRIPTPATH=$(dirname "$SCRIPTPATH")
echo $SCRIPTPATH
cd $SCRIPTPATH

python -m pytest ##-v