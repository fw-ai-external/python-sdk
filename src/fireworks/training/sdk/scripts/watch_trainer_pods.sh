#!/bin/bash
# Tight-loop pod watcher: finds trainer pods by job ID and streams logs to local files.
# Usage: ./watch_trainer_pods.sh <job_id>
# Set KUBE_CONTEXT to override the default kubectl context.
# Logs go to $HOME/workspace/logs/<job_id>-trainer-<N>.log

JOB_ID="$1"
CTX="${KUBE_CONTEXT:-US_OHIO_1 (lambda us-midwest-2)}"
LOG_DIR="$HOME/workspace/logs"
mkdir -p "$LOG_DIR"

if [ -z "$JOB_ID" ]; then
  echo "Usage: $0 <job_id>"
  exit 1
fi

echo "[watcher] Watching for pods with trainerId=$JOB_ID every 2s..."
FOUND=""
for i in $(seq 1 300); do
  PODS=$(kubectl get pods -l fireworks.ai/trainerId=$JOB_ID --all-namespaces --context "$CTX" \
    -o jsonpath='{range .items[*]}{.metadata.namespace}/{.metadata.name}{"\n"}{end}' 2>/dev/null)
  if [ -n "$PODS" ]; then
    echo "[watcher] Found pods at iteration $i:"
    echo "$PODS"
    while IFS= read -r line; do
      NS=$(echo "$line" | cut -d/ -f1)
      POD=$(echo "$line" | cut -d/ -f2)
      [ -z "$POD" ] && continue
      LOGFILE="$LOG_DIR/${JOB_ID}-${POD}.log"
      if [ -z "$FOUND" ] || ! echo "$FOUND" | grep -q "$POD"; then
        echo "[watcher] Streaming $POD (ns=$NS) -> $LOGFILE"
        kubectl --context "$CTX" logs "$POD" -c trainer -n "$NS" > "$LOGFILE" 2>&1
        kubectl --context "$CTX" logs -f "$POD" -c trainer -n "$NS" >> "$LOGFILE" 2>&1 &
        FOUND="$FOUND $POD"
      fi
    done <<< "$PODS"
    echo "[watcher] Pod status:"
    kubectl get pods -l fireworks.ai/trainerId=$JOB_ID --all-namespaces --context "$CTX" -o wide 2>&1
    echo "[watcher] Streaming started. Monitoring pod status every 5s..."
    for j in $(seq 1 600); do
      sleep 5
      STATUS=$(kubectl get pods -l fireworks.ai/trainerId=$JOB_ID --all-namespaces --context "$CTX" \
        --no-headers 2>/dev/null)
      if [ -z "$STATUS" ]; then
        echo "[watcher] Pods disappeared! Attempting --previous logs..."
        while IFS= read -r line; do
          NS=$(echo "$line" | cut -d/ -f1)
          POD=$(echo "$line" | cut -d/ -f2)
          [ -z "$POD" ] && continue
          PREVLOG="$LOG_DIR/${JOB_ID}-${POD}-previous.log"
          kubectl --context "$CTX" logs "$POD" -c trainer -n "$NS" --previous > "$PREVLOG" 2>&1
          echo "[watcher] Previous logs -> $PREVLOG"
        done <<< "$PODS"
        echo "[watcher] Done. Check ~/workspace/logs/${JOB_ID}-*.log"
        exit 0
      fi
      RESTARTS=$(echo "$STATUS" | awk '{print $4}' | head -1)
      PHASE=$(echo "$STATUS" | awk '{print $3}' | head -1)
      echo "[watcher] [$j] Phase=$PHASE Restarts=$RESTARTS"
      if [ "$RESTARTS" -gt 0 ] 2>/dev/null; then
        echo "[watcher] Crash detected! Capturing --previous logs..."
        while IFS= read -r line; do
          NS=$(echo "$line" | cut -d/ -f1)
          POD=$(echo "$line" | cut -d/ -f2)
          [ -z "$POD" ] && continue
          PREVLOG="$LOG_DIR/${JOB_ID}-${POD}-previous.log"
          kubectl --context "$CTX" logs "$POD" -c trainer -n "$NS" --previous > "$PREVLOG" 2>&1
          echo "[watcher] Previous logs -> $PREVLOG"
        done <<< "$PODS"
      fi
    done
    break
  fi
  sleep 2
done
echo "[watcher] Exiting."
