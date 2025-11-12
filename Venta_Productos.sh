#!/data/data/com.termux/files/usr/bin/bash

PORT=5000
APP_PATH="/storage/emulated/0/SyncFolder/ventaproductos"
URL="http://127.0.0.1:$PORT"
LOG_FILE="$APP_PATH/init_shell_log.txt"

logmsg() {
    local msg="$1"
    local logfile="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$(basename "$0")] $msg" | tee -a "$logfile"
}

echo "">"$LOG_FILE"

~/.shortcuts/kill_port.sh 5000 $LOG_FILE $APP_PATH

sleep 3

logmsg "----- $(date) Starting Flask -----" "$LOG_FILE"

#nohup python "$APP_PATH/app.py" 2>&1 | tee -a "$LOG_FILE"
# ✅ Fully detached Flask start (logs both stdout & stderr)
nohup bash -c "python '$APP_PATH/app.py' 2>&1 | tee -a '$LOG_FILE'" &

logmsg "✅ Flask started in background. Logging to $LOG_FILE" "$LOG_FILE"

sleep 3


# 0x00008000     # FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
# 0x10200000        # FLAG_ACTIVITY_CLEAR_TOP
# 0x10208000 + 0x00008000 = 0x10208000  # COMBINED

# # Open Chrome
# am start \
#   -a android.intent.action.VIEW \
#   -n com.android.chrome/com.google.android.apps.chrome.Main \
#   -f 0x10208000 \
#   -d "$URL" \
#   2>&1 | tee -a "$LOG_FILE"

am start \
  -a android.intent.action.VIEW \
  -n com.android.chrome/com.google.android.apps.chrome.Main \
  -d "$URL" \
  --activity-clear-top \
  --activity-exclude-from-recents \
  2>&1 | tee -a "$LOG_FILE"




exit 0


0x10200000