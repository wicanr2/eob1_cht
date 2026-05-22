#!/bin/bash
pkill -9 scummvm 2>/dev/null
sleep 1
ls -la /root/eob1cht/ | grep -i kyra
echo ---
# Verify KYRA.DAT contents
echo "First 16 bytes of KYRA.DAT:"
xxd /root/eob1cht/KYRA.DAT | head -1
echo ---
# Run scummvm and capture output
DISPLAY=:0 /root/scummvm_work/scummvm/scummvm \
    --extrapath=/root/eob1cht \
    --path=/root/eob1cht \
    --auto-detect \
    -d 5 \
    > /mnt/c/Temp/scummvm_debug.log 2>&1 &

SCUMMVM_PID=$!
echo "scummvm started, PID=$SCUMMVM_PID"

# Wait up to 15s for it to either error out or render
for i in $(seq 1 15); do
    if ! kill -0 $SCUMMVM_PID 2>/dev/null; then
        echo "scummvm exited at second $i"
        break
    fi
    sleep 1
done

echo "--- LOG TAIL ---"
tail -100 /mnt/c/Temp/scummvm_debug.log
