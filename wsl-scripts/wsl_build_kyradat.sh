#!/bin/bash
set -e
cd /root/scummvm_work/scummvm/devtools/create_kyradat
echo "Building create_kyradat..."
# Compile directly without going through scummvm's full configure
g++ -std=c++14 -O2 -I. -I../.. \
    create_kyradat.cpp games.cpp md5.cpp pak.cpp resources.cpp types.cpp util.cpp \
    -o create_kyradat 2>&1 | tail -30
ls -la create_kyradat
