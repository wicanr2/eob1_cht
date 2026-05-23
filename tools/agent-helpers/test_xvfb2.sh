#!/bin/bash
# Test with explicit surface SDL (no OpenGL)
pkill -9 scummvm 2>/dev/null
pkill -9 Xvfb 2>/dev/null
sleep 2

Xvfb :99 -screen 0 800x600x24 +extension GLX > /tmp/xvfb.log 2>&1 &
sleep 1
echo "Xvfb: $(pgrep Xvfb)"

(setsid bash -c "DISPLAY=:99 SDL_VIDEODRIVER=x11 nohup /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht --path=/root/eob1cht --auto-detect --gfx-mode=surfacesdl \
    </dev/null >/tmp/scummvm.log 2>&1 &
disown
" </dev/null >/dev/null 2>&1 &)

sleep 5
SCUMMVM_PID=$(pgrep -f "scummvm.*eob1cht" | head -1)
if [ -n "$SCUMMVM_PID" ]; then
    echo "scummvm $SCUMMVM_PID alive"
    DISPLAY=:99 xwininfo -root -tree | head -10
fi

# Wait 10 more seconds — see if it survives
sleep 10
if pgrep -f "scummvm.*eob1cht" >/dev/null; then
    echo "STILL ALIVE after 15s"
    DISPLAY=:99 import -window root /tmp/test_shot.png && echo "shot ok"
else
    echo "DIED. Log:"
    tail -10 /tmp/scummvm.log
fi
