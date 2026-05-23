#!/bin/bash
# Stable driver for iter3 testing.
# - 5 second wait after launch so scummvm passes the unstable startup
# - All input commands have hard timeouts to avoid hanging on dead windows
# - Each input also checks alive first

set -u
DISPLAY_NUM=99
LOG=/tmp/eob1-tester/scummvm.log
SCUMMVM=/root/scummvm_work/scummvm/scummvm
GAMEDIR=/root/eob1cht
SHOT_DIR=/mnt/d/03_game_tmp/eob1_cht/test-reports/screenshots
WID_FILE=/tmp/eob1-tester/wid
PID_FILE=/tmp/eob1-tester/pid

mkdir -p /tmp/eob1-tester $SHOT_DIR
export DISPLAY=:$DISPLAY_NUM

start() {
    pkill -9 scummvm 2>/dev/null
    pkill -9 -f "Xvfb :$DISPLAY_NUM" 2>/dev/null
    sleep 1
    rm -f $WID_FILE $PID_FILE
    Xvfb :$DISPLAY_NUM -nolisten unix -screen 0 800x600x24 +extension GLX >/tmp/eob1-tester/xvfb.log 2>&1 &
    sleep 1
    > $LOG
    setsid bash -c "SDL_VIDEODRIVER=x11 DISPLAY=:$DISPLAY_NUM nohup $SCUMMVM --extrapath=$GAMEDIR --path=$GAMEDIR --gfx-mode=surfacesdl --opl-driver=null --music-driver=null kyra:eob </dev/null >>$LOG 2>&1 & disown" </dev/null >/dev/null 2>&1
    sleep 5  # crucial: don't touch scummvm for 5s
    SC_PID=$(pgrep -f "scummvm.*--path" | head -1)
    [ -z "$SC_PID" ] && { echo "no scummvm pid"; tail -10 $LOG; return 1; }
    WID=$(xdotool search --class scummvm 2>/dev/null | head -1)
    [ -z "$WID" ] && { echo "no window"; return 1; }
    echo $SC_PID > $PID_FILE
    echo $WID > $WID_FILE
    echo "OK pid=$SC_PID wid=$WID"
}

alive() {
    local pid=$(cat $PID_FILE 2>/dev/null)
    [ -n "$pid" ] && kill -0 $pid 2>/dev/null && return 0
    return 1
}

shot() {
    local OUT="$1"
    if ! alive; then echo "DEAD-pre-shot $OUT"; return 1; fi
    local WID=$(cat $WID_FILE)
    timeout 1 import -window $WID "$OUT" 2>/dev/null
    if [ -f "$OUT" ]; then
        echo "snap $OUT ($(stat -c %s "$OUT"))"
    else
        echo "snap FAILED $OUT"
    fi
}

key() {
    if ! alive; then echo "DEAD-pre-key $*"; return 1; fi
    local WID=$(cat $WID_FILE)
    for k in "$@"; do
        timeout 0.5 xdotool key --window $WID --delay 10 "$k" 2>/dev/null
        sleep 0.05
    done
}

clk() {
    if ! alive; then echo "DEAD-pre-clk $*"; return 1; fi
    local WID=$(cat $WID_FILE)
    timeout 0.5 xdotool mousemove --window $WID $1 $2 2>/dev/null
    sleep 0.1
    timeout 0.5 xdotool click --window $WID 1 2>/dev/null
}

rclk() {
    if ! alive; then echo "DEAD-pre-rclk"; return 1; fi
    local WID=$(cat $WID_FILE)
    timeout 0.5 xdotool mousemove --window $WID $1 $2 2>/dev/null
    sleep 0.05
    timeout 0.5 xdotool click --window $WID 3 2>/dev/null
}

wait_s() { sleep "$1"; }

logtail() { tail -20 $LOG; }

stop() {
    pkill -9 scummvm 2>/dev/null
    pkill -9 -f "Xvfb :$DISPLAY_NUM" 2>/dev/null
    rm -f $WID_FILE $PID_FILE
    sleep 0.5
    echo stopped
}

cmd=$1; shift
$cmd "$@"
