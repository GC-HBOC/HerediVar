
#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
SCRIPTPATH=$(dirname "$SCRIPTPATH")
cd $SCRIPTPATH

python -m pytest ##-v