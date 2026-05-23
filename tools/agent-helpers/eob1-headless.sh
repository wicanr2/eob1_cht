#!/bin/bash
# EOB1 headless game-tester driver — uses Xvfb (no Windows window appears).
#
# Usage:
#   ./eob1-headless.sh start                  # boot scummvm in Xvfb :99
#   ./eob1-headless.sh shot <output.png>      # PNG of current scummvm window
#   ./eob1-headless.sh key  <keys>            # send keystrokes (e.g. "Return" or "Escape" or "a b c")
#   ./eob1-headless.sh keydown <keys>         # hold key then release after 50ms
#   ./eob1-headless.sh click <x> <y>          # click at window-relative coords (640x480 game canvas)
#   ./eob1-headless.sh rclick <x> <y>         # right click
#   ./eob1-headless.sh wait <seconds>         # sleep N seconds (animations etc)
#   ./eob1-headless.sh status                 # show PID + window state + log tail
#   ./eob1-headless.sh stop                   # kill scummvm + Xvfb
#
# All output goes to /tmp/eob1-tester/ inside WSL.
#
# Game canvas is 640x480 (rendered in 320x200 doubled). Coords are 0,0 = top-left.

set -e

DISPLAY_NUM=99
SCREEN_W=800
SCREEN_H=600
LOG=/tmp/eob1-tester/scummvm.log
PIDFILE=/tmp/eob1-tester/pids
mkdir -p /tmp/eob1-tester

SCUMMVM=/root/scummvm_work/scummvm/scummvm
GAMEDIR=/root/eob1cht

start_xvfb() {
    if pgrep -f "Xvfb :$DISPLAY_NUM" >/dev/null; then
        echo "Xvfb :$DISPLAY_NUM already running"
        return 0
    fi
    # +extension GLX is required even though we won't use GL — scummvm probes for it
    Xvfb :$DISPLAY_NUM -screen 0 ${SCREEN_W}x${SCREEN_H}x24 +extension GLX >/tmp/eob1-tester/xvfb.log 2>&1 &
    XVFB_PID=$!
    echo "xvfb=$XVFB_PID" >> $PIDFILE
    sleep 1
    if ! kill -0 $XVFB_PID 2>/dev/null; then
        echo "ERR: Xvfb failed to start"
        cat /tmp/eob1-tester/xvfb.log
        exit 1
    fi
    echo "Xvfb :$DISPLAY_NUM started (pid $XVFB_PID)"
}

start_scummvm() {
    if pgrep -f "scummvm.*eob1cht" >/dev/null; then
        echo "scummvm already running"
        return 0
    fi
    # Fully detach: setsid + surface SDL (Xvfb GL is incomplete)
    # Use explicit target kyra:eob (skip launcher GUI which crashes in Xvfb)
    (
        setsid bash -c "DISPLAY=:$DISPLAY_NUM SDL_VIDEODRIVER=x11 nohup $SCUMMVM \
            --extrapath=$GAMEDIR \
            --path=$GAMEDIR \
            --gfx-mode=surfacesdl \
            kyra:eob \
            </dev/null >$LOG 2>&1 &
            disown
        " </dev/null >/dev/null 2>&1 &
    )
    sleep 5
    SCUMMVM_PID=$(pgrep -f "scummvm.*eob1cht" | head -1)
    if [ -z "$SCUMMVM_PID" ]; then
        echo "ERR: scummvm died. Log:"
        tail -15 $LOG
        exit 1
    fi
    echo "scummvm=$SCUMMVM_PID" >> $PIDFILE
    echo "scummvm started (pid $SCUMMVM_PID)"
}

find_window() {
    DISPLAY=:$DISPLAY_NUM xdotool search --class scummvm 2>/dev/null | head -1
}

cmd_start() {
    rm -f $PIDFILE
    start_xvfb
    start_scummvm
    sleep 4
    WID=$(find_window)
    if [ -z "$WID" ]; then
        echo "WARN: window not found yet, trying once more"
        sleep 4
        WID=$(find_window)
    fi
    echo "wid=$WID" >> $PIDFILE
    echo "DONE. window_id=$WID"
}

cmd_shot() {
    local OUT="$1"
    if [ -z "$OUT" ]; then echo "usage: shot <output.png>"; exit 1; fi
    WID=$(find_window)
    if [ -z "$WID" ]; then echo "ERR: no scummvm window"; exit 1; fi
    DISPLAY=:$DISPLAY_NUM import -window $WID "$OUT"
    ls -la "$OUT"
}

cmd_key() {
    WID=$(find_window)
    if [ -z "$WID" ]; then echo "ERR: no window"; exit 1; fi
    DISPLAY=:$DISPLAY_NUM xdotool windowfocus --sync $WID
    for k in "$@"; do
        DISPLAY=:$DISPLAY_NUM xdotool key --window $WID --delay 30 "$k"
    done
}

cmd_keydown() {
    WID=$(find_window)
    DISPLAY=:$DISPLAY_NUM xdotool windowfocus --sync $WID
    for k in "$@"; do
        DISPLAY=:$DISPLAY_NUM xdotool keydown --window $WID "$k"
        sleep 0.05
        DISPLAY=:$DISPLAY_NUM xdotool keyup --window $WID "$k"
    done
}

cmd_click() {
    local X="$1" Y="$2"
    if [ -z "$X" ] || [ -z "$Y" ]; then echo "usage: click <x> <y>"; exit 1; fi
    WID=$(find_window)
    DISPLAY=:$DISPLAY_NUM xdotool mousemove --window $WID $X $Y
    sleep 0.1
    DISPLAY=:$DISPLAY_NUM xdotool click --window $WID 1
}

cmd_rclick() {
    local X="$1" Y="$2"
    WID=$(find_window)
    DISPLAY=:$DISPLAY_NUM xdotool mousemove --window $WID $X $Y
    sleep 0.1
    DISPLAY=:$DISPLAY_NUM xdotool click --window $WID 3
}

cmd_wait() {
    sleep "$1"
}

cmd_status() {
    echo "=== PIDs ==="
    cat $PIDFILE 2>/dev/null || echo "no pidfile"
    echo "=== Processes ==="
    pgrep -af 'Xvfb|scummvm' | grep -v eob1-headless
    echo "=== Window ==="
    DISPLAY=:$DISPLAY_NUM xwininfo -root -tree 2>&1 | grep -B1 -A0 scummvm | head -5
    echo "=== Log tail ==="
    tail -10 $LOG 2>/dev/null
}

cmd_stop() {
    pkill -9 scummvm 2>/dev/null || true
    pkill -9 -f "Xvfb :$DISPLAY_NUM" 2>/dev/null || true
    rm -f $PIDFILE
    sleep 1
    echo "stopped"
}

case "$1" in
    start)   cmd_start ;;
    shot)    shift; cmd_shot "$@" ;;
    key)     shift; cmd_key "$@" ;;
    keydown) shift; cmd_keydown "$@" ;;
    click)   shift; cmd_click "$@" ;;
    rclick)  shift; cmd_rclick "$@" ;;
    wait)    shift; cmd_wait "$@" ;;
    status)  cmd_status ;;
    stop)    cmd_stop ;;
    *)       echo "usage: $0 {start|shot|key|keydown|click|rclick|wait|status|stop} [args...]"; exit 1 ;;
esac
