#!/bin/bash
## -u Update Mapping API  Script

echo "Terminating telegraph dial in and dial out container"
docker stop telegraf_out
docker stop telegraf_in

elasticsearch/update.sh 0.0.0.0 9200

echo "Starting telegraph dial in and dial out container"
docker start telegraf_in
docker start telegraf_out
