#!/bin/bash
set -e
cd /root/scummvm_work/scummvm
echo "=== configure (tools only, no engines needed) ==="
./configure --backend=null --disable-all-engines 2>&1 | tail -20
echo
echo "=== make devtools ==="
make devtools 2>&1 | tail -30
echo
ls -la devtools/create_kyradat/create_kyradat
