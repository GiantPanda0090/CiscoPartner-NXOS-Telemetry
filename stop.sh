#!/bin/bash
## -t Termination Script

secs=$((10))
while [ $secs -gt 0 ]; do
   echo -ne "All Docker Container Terminate in $secs\033[0K second\r"
   sleep 1
   : $((secs--))
done

docker rm -f $(sudo docker ps -a -q)
sudo docker network rm elasticsearch_elk



