#!/bin/bash
# Robust detached scummvm start. Returns when window exists.
pkill -9 scummvm 2>/dev/null || true
pkill -9 -f "Xvfb :99" 2>/dev/null || true
sleep 1
mkdir -p /tmp/eob1-tester
rm -f /tmp/eob1-tester/scummvm.log

# Start Xvfb fully detached
setsid nohup Xvfb :99 -screen 0 800x600x24 +extension GLX >/tmp/eob1-tester/xvfb.log 2>&1 </dev/null &
disown
sleep 1

# Start scummvm fully detached, ensure stdin/stdout/stderr redirected
setsid nohup env DISPLAY=:99 SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=dummy \
    /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht --path=/root/eob1cht \
    --gfx-mode=surfacesdl kyra:eob \
    >/tmp/eob1-tester/scummvm.log 2>&1 </dev/null &
disown
echo "started, scummvm pid=$!"
sleep 3
echo "==processes=="
pgrep -af scummvm
pgrep -af "Xvfb :99"
echo "==wid=="
DISPLAY=:99 xdotool search --class scummvm 2>/dev/null | head -1
