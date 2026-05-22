#!/bin/bash
pkill -9 scummvm 2>/dev/null
sleep 1
/root/scummvm_work/scummvm/scummvm --help 2>&1 | head -80
