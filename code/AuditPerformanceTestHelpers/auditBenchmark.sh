#!/usr/bin/env bash
set -e # Exit if any command fails

# Parameters for tuning testing
TIME_TO_WAIT_FOR_AUDIT_TO_SETTLE_IN_SECONDS=3
HOW_LONG_TO_RUN_AUDIT_FOR_IN_SECONDS=120
# Add audit settle time to audit runtime as this time period has no events occuring
AUDIT_RUNTIME_IN_SECONDS=$(( $TIME_TO_WAIT_FOR_AUDIT_TO_SETTLE_IN_SECONDS + $HOW_LONG_TO_RUN_AUDIT_FOR_IN_SECONDS ))
TIME_TO_PRODUCE_EVENTS_FOR=15
THREADS=4

# 1. Restart BPFContain daemon to reset global audit stats counter - so we should run with root privileges

# If stop fails (the daemon was not already running), ignore the failure result
bpfcontain daemon stop || true

# Need to wait a moment as BPFContain uses a pid lock
sleep 1s

bpfcontain daemon start

# Wait for BPFContain to start up
sleep 2s

# 2. Audit creation request

# Audit creation request parameters
AUDIT_END_TIME_ISO_8601=$(date -u --date "+${AUDIT_RUNTIME_IN_SECONDS} seconds" +"%Y-%m-%dT%H:%M:%SZ")
SERVICE_ID_FOR_AUDIT=46940

# Perform audit creation request
printf "Audit creation request response:\n"
curl -f --location --request POST 'http://localhost:7060/bpfca/api/v1/audits' \
--header 'Content-Type: application/vnd.api+json' \
--header 'Accept: application/vnd.api+json' \
--data-raw "{
   \"data\":{
      \"type\": \"audits\",
      \"attributes\":{
         \"endTime\": \"${AUDIT_END_TIME_ISO_8601}\",
         \"serviceId\": 46940
      }
   }
}"

# Wait for the audit creation to settle
sleep 3s

# 3. Contain and run our spammy program
printf "\n\nStarted to produce audit events at $(date)\n"

bpfcontain run perfTest.yml -- "/home/cody/Desktop/AuditEventSpam/eventSpam -t ${THREADS} -s ${TIME_TO_PRODUCE_EVENTS_FOR}"

printf "Finished producing audit events at $(date)\n"