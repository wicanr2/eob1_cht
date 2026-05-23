#!/bin/bash
set -x
pkill -9 scummvm 2>/dev/null || true
pkill -9 Xvfb 2>/dev/null || true
sleep 2

Xvfb :99 -screen 0 800x600x24 > /tmp/xvfb.log 2>&1 &
sleep 1
echo "Xvfb pid: $(pgrep Xvfb)"

DISPLAY=:99 nohup /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht --path=/root/eob1cht --auto-detect \
    > /tmp/scummvm.log 2>&1 &
SCUMMVM_PID=$!
echo "scummvm pid: $SCUMMVM_PID"

sleep 5
if kill -0 $SCUMMVM_PID 2>/dev/null; then
    echo "scummvm alive after 5s"
    DISPLAY=:99 xwininfo -root -tree 2>&1 | head -15
else
    echo "scummvm DIED. Log:"
    tail -30 /tmp/scummvm.log
fi
