#!/data/data/com.termux/files/usr/bin/bash
# Kill all processes running on a specified port

PORT=$1
LOG_FILE=$2
APP_PATH=$3

logmsg() {
    local msg="$1"
    local logfile="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$(basename "$0")] $msg" | tee -a "$logfile"
}

# Check if a port number was provided
if [ -z "$1" ]; then
  echo "⚠️  Usage: $0 <port>"
  exit 1
fi

# Find process IDs using the port
PIDS=$(lsof -t -i:$PORT)

if [ -z "$PIDS" ]; then
  logmsg "✅ No process found using port $PORT." "$LOG_FILE"
else
  logmsg "💀 Killing processes on port $PORT: $PIDS" "$LOG_FILE"
  # Force kill each process
  for PID in $PIDS; do
    kill -9 "$PID" >>"$LOG_FILE" && echo "   🔪 Killed PID $PID" 2>&1 | tee -a "$LOG_FILE"
  done
  logmsg "✅ All processes using port $PORT have been terminated." "$LOG_FILE"
fi


# # Find the PID of the Flask app
# PID=$(ps -ef | grep "$APP_PATH/app.py" | grep -v grep | awk '{print $2}')

# if [ -n "$PID" ]; then
#   logmsg "🛑 Found Flask process on port $PORT (PID $PID). Killing..." "$LOG_FILE"
#   kill -9 "$PID"
#   sleep 2
#   logmsg "✅ Flask process $PID killed." "$LOG_FILE"
# else
#   logmsg "ℹ️ No Flask process found for port $PORT." "$LOG_FILE"
# fi

PIDS=$(ps -ef | grep "$APP_PATH/app.py" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
  logmsg "🛑 Found Flask processes on port $PORT: $PIDS. Killing..." "$LOG_FILE"
  for PID in $PIDS; do
    kill -9 "$PID" 2>&1 | tee -a "$LOG_FILE"
    logmsg "   ➜ Killed process $PID" "$LOG_FILE"
  done
  logmsg "✅ All Flask processes killed." "$LOG_FILE"
else
  logmsg "ℹ️ No Flask process found for port $PORT." "$LOG_FILE"
fi
