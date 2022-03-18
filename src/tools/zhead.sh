#!/bin/bash

# this basically executes #zcat file.gz | head -n x 
# but can be savely run with set -o pipefail
zhead_py=$(cat <<'EOF'
import sys, gzip
gzf = gzip.GzipFile(sys.argv[1], 'rb')
outFile = sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout
numLines = 0
maxLines = int(sys.argv[2])
for line in gzf:
    if numLines >= maxLines:
        sys.exit(0)
    outFile.write(line)
    numLines += 1
EOF
)
zhead() { python3 -c "$zhead_py" "$@"; }