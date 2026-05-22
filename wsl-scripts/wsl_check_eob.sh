#!/bin/bash
cd /root/scummvm_work/scummvm
echo "=== configure help (kyra+eob+lol) ==="
./configure --help 2>&1 | grep -iE "kyra|eob|lol|kyrandia"
echo
echo "=== current config.mk grep ENGINES ==="
grep -iE "ENGINE.*(KYRA|EOB|LOL)" config.mk 2>&1 | head -20
echo
echo "=== check engines/kyra/configure.engine ==="
cat engines/kyra/configure.engine 2>&1
