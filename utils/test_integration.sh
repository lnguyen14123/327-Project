#!/bin/bash
# utils/test_integration.sh
# Simple local integration test for the CECS 327 P2P client

set -e  # exit immediately if any command fails

# Install dependencies if missing
python3 -m pip install --quiet Pyro5 pygame

# Go to project root so relative imports still work
cd "$(dirname "$0")/.."

echo "=== CECS 327 P2P Integration Test ==="
echo "This will start three local clients and verify that peer discovery works."

# Ensure logs folder exists
mkdir -p utils/logs

# Clean up old logs
rm -f utils/logs/client1.log utils/logs/client2.log utils/logs/client3.log

# Start three clients
echo "Starting Client 1..."
python3 main.py join > utils/logs/client1.log 2>&1 &
PID1=$!
sleep 2

echo "Starting Client 2..."
python3 main.py join > utils/logs/client2.log 2>&1 &
PID2=$!
sleep 2

echo "Starting Client 3..."
python3 main.py join > utils/logs/client3.log 2>&1 &
PID3=$!
sleep 5  # allow time for discovery and one round of messages

# Show logs
echo
echo "---- Client 1 log (first 10 lines) ----"
head -n 10 utils/logs/client1.log || true
echo
echo "---- Client 2 log (first 10 lines) ----"
head -n 10 utils/logs/client2.log || true
echo
echo "---- Client 3 log (first 10 lines) ----"
head -n 10 utils/logs/client3.log || true
echo

# Quick verification for discovery messages
if grep -q "Discovered peer" utils/logs/client1.log utils/logs/client2.log utils/logs/client3.log; then
  echo "✅ SUCCESS: At least one client discovered peers."
else
  echo "❌ WARNING: No discovery messages found in logs. Check network/multicast setup."
fi

# Cleanup
echo "Stopping all clients..."
kill $PID1 $PID2 $PID3 2>/dev/null || true
sleep 1

echo "=== Test complete ==="
