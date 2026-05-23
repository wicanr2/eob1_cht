#!/bin/bash
# Boot scummvm and immediately spam keys to skip intro before engine self-quits.
set -e
pkill -9 scummvm 2>/dev/null || true
pkill -9 -f "Xvfb :99" 2>/dev/null || true
sleep 1
rm -f /tmp/eob1-tester/scummvm.log
mkdir -p /tmp/eob1-tester
Xvfb :99 -screen 0 800x600x24 +extension GLX >/tmp/eob1-tester/xvfb.log 2>&1 &
sleep 1
DISPLAY=:99 SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=dummy nohup /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht --path=/root/eob1cht \
    --gfx-mode=surfacesdl kyra:eob </dev/null >/tmp/eob1-tester/scummvm.log 2>&1 &
disown
sleep 3
WID=$(DISPLAY=:99 xdotool search --class scummvm | head -1)
echo "wid=$WID"
if [ -z "$WID" ]; then
  echo "ERR no window after 3s"
  exit 1
fi
# Spam space+return for 8 seconds to skip intro/cinematics
END=$(($(date +%s) + 8))
while [ $(date +%s) -lt $END ]; do
  DISPLAY=:99 xdotool key --window $WID --delay 50 space 2>/dev/null || true
  DISPLAY=:99 xdotool key --window $WID --delay 50 Return 2>/dev/null || true
done
sleep 1
echo "==alive check=="
pgrep -af scummvm || echo "DEAD"
echo "==log tail=="
tail -6 /tmp/eob1-tester/scummvm.log
